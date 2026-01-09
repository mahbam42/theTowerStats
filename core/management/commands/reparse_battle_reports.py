"""Reparse stored Battle Reports and backfill parsed progress fields."""

from __future__ import annotations

from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.db.models import DateTimeField, QuerySet
from django.db.models.functions import Coalesce

from analysis.raw_text_metrics import extract_raw_text_metrics
from core.parsers.battle_report import (
    fallback_battle_date,
    parse_battle_report,
    record_unrecognized_unit_suffixes,
)
from core.services import backfill_run_bot_usage, pending_run_bot_usage_count
from definitions.models import PatchBoundary
from gamedata.models import BattleReport, BattleReportDerivedMetrics, BattleReportProgress


class Command(BaseCommand):
    """Reparse Battle Reports and populate BattleReportProgress fields."""

    help = "Reparse Battle Reports and backfill BattleReportProgress fields (idempotent)."

    def add_arguments(self, parser) -> None:
        """Add command arguments."""

        parser.add_argument(
            "--check",
            action="store_true",
            help="Dry-run: report what would change without writing.",
        )
        parser.add_argument(
            "--write",
            action="store_true",
            help="Write changes to the database.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Optional maximum number of Battle Reports to process.",
        )
        parser.add_argument(
            "--patch",
            type=str,
            default=None,
            help="Restrict to Battle Reports within the named patch boundary window.",
        )

    def handle(self, *args, **options) -> str | None:
        """Run the command."""

        check: bool = options["check"]
        write: bool = options["write"]
        limit: int | None = options["limit"]
        patch: str | None = options["patch"]

        if check and write:
            raise CommandError("Use either --check or --write, not both.")
        if not check and not write:
            raise CommandError("Refusing to write without explicit intent; pass --check or --write.")

        queryset = BattleReport.objects.select_related("run_progress", "derived_metrics").order_by("id")
        if patch:
            boundary = _resolve_patch_boundary(patch)
            if boundary is None:
                raise CommandError(f"Unknown patch boundary: {patch!r}")
            queryset = _filter_reports_for_patch(queryset, boundary)
        if limit is not None:
            queryset = _limit_to_last_n_reports(queryset, limit)

        totals = {
            "processed": 0,
            "created_progress": 0,
            "updated_progress": 0,
            "created_derived": 0,
            "updated_derived": 0,
            "created_bots": 0,
            "no_change": 0,
        }

        for report in queryset:
            totals["processed"] += 1
            if write:
                record_unrecognized_unit_suffixes(report.raw_text)
            parsed = parse_battle_report(report.raw_text)
            derived_payload = _derived_metrics_payload(report.raw_text)

            progress = getattr(report, "run_progress", None)
            created = False
            if progress is None:
                progress = BattleReportProgress(battle_report=report, player=report.player)
                created = True

            battle_date = fallback_battle_date(parsed.battle_date, parsed_at=report.parsed_at)
            updated_fields = {
                "battle_date": battle_date,
                "tier": parsed.tier,
                "wave": parsed.wave,
                "real_time_seconds": parsed.real_time_seconds,
                "killed_by": parsed.killed_by,
                "coins_earned": parsed.coins_earned,
                "coins_earned_raw": parsed.coins_earned_raw,
                "cash_earned": parsed.cash_earned,
                "cash_earned_raw": parsed.cash_earned_raw,
                "interest_earned": parsed.interest_earned,
                "interest_earned_raw": parsed.interest_earned_raw,
                "gem_blocks_tapped": parsed.gem_blocks_tapped,
                "cells_earned": parsed.cells_earned,
                "reroll_shards_earned": parsed.reroll_shards_earned,
            }

            progress_changed = created or any(getattr(progress, key) != value for key, value in updated_fields.items())
            derived = getattr(report, "derived_metrics", None)
            derived_changed = (
                derived is None
                or derived.values != derived_payload["values"]
                or derived.raw_values != derived_payload["raw_values"]
            )

            bot_pending = pending_run_bot_usage_count(battle_report=report, player=report.player)
            if not progress_changed and not derived_changed and bot_pending == 0:
                totals["no_change"] += 1
                continue

            if progress_changed:
                totals["created_progress"] += int(created)
                totals["updated_progress"] += int(not created)

                if write:
                    for key, value in updated_fields.items():
                        setattr(progress, key, value)
                    progress.save()

            if derived_changed:
                totals["created_derived"] += int(derived is None)
                totals["updated_derived"] += int(derived is not None)

                if write:
                    BattleReportDerivedMetrics.objects.update_or_create(
                        battle_report=report,
                        defaults={
                            "player": report.player,
                            "values": derived_payload["values"],
                            "raw_values": derived_payload["raw_values"],
                        },
                    )

            if write:
                totals["created_bots"] += backfill_run_bot_usage(
                    battle_report=report,
                    player=report.player,
                )
            else:
                totals["created_bots"] += bot_pending

        mode = "CHECK" if check else "WRITE"
        self.stdout.write(f"[{mode}] {totals}")
        return None


def _derived_metrics_payload(raw_text: str) -> dict[str, dict[str, float | str]]:
    """Return persisted derived metrics payload from Battle Report text."""

    extracted = extract_raw_text_metrics(raw_text)
    return {
        "values": {key: parsed.value for key, parsed in extracted.items()},
        "raw_values": {key: parsed.raw_value for key, parsed in extracted.items()},
    }


def _resolve_patch_boundary(patch: str) -> PatchBoundary | None:
    """Resolve a patch boundary by label or date string.

    Args:
        patch: Patch label or ISO date string.

    Returns:
        PatchBoundary when matched; otherwise None.
    """

    normalized = patch.strip()
    if not normalized:
        return None
    boundary = PatchBoundary.objects.filter(label__iexact=normalized).first()
    if boundary is not None:
        return boundary
    try:
        boundary_date = date.fromisoformat(normalized)
    except ValueError:
        return None
    return PatchBoundary.objects.filter(boundary_date=boundary_date).first()


def _filter_reports_for_patch(
    queryset: QuerySet[BattleReport], boundary: PatchBoundary
) -> QuerySet[BattleReport]:
    """Restrict Battle Reports to the selected patch window.

    Args:
        queryset: Base BattleReport queryset.
        boundary: PatchBoundary representing the window start.

    Returns:
        QuerySet filtered to the patch window.
    """

    boundary_dates = list(PatchBoundary.objects.values_list("boundary_date", flat=True).order_by("boundary_date"))
    if boundary.boundary_date not in boundary_dates:
        return queryset.none()
    idx = boundary_dates.index(boundary.boundary_date)
    next_date = boundary_dates[idx + 1] if idx + 1 < len(boundary_dates) else None

    filtered = queryset.annotate(
        effective_battle_date=Coalesce(
            "run_progress__battle_date",
            "parsed_at",
            output_field=DateTimeField(),
        )
    ).filter(effective_battle_date__date__gte=boundary.boundary_date)
    if next_date is not None:
        filtered = filtered.filter(effective_battle_date__date__lt=next_date)
    return filtered


def _limit_to_last_n_reports(queryset: QuerySet[BattleReport], limit: int) -> QuerySet[BattleReport]:
    """Limit the queryset to the most recent N reports by id.

    Args:
        queryset: BattleReport queryset.
        limit: Maximum number of rows to keep.

    Returns:
        QuerySet reduced to the newest `limit` reports.
    """

    if limit <= 0:
        return queryset.none()
    ids = list(queryset.order_by("-id").values_list("id", flat=True)[:limit])
    if not ids:
        return queryset.none()
    return queryset.filter(id__in=ids).order_by("id")
