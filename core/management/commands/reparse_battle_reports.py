"""Reparse stored Battle Reports and backfill parsed progress fields."""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from core.parsers.battle_report import parse_battle_report
from gamedata.models import BattleReport, BattleReportProgress


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

    def handle(self, *args, **options) -> str | None:
        """Run the command."""

        check: bool = options["check"]
        write: bool = options["write"]
        limit: int | None = options["limit"]

        if check and write:
            raise CommandError("Use either --check or --write, not both.")
        if not check and not write:
            raise CommandError("Refusing to write without explicit intent; pass --check or --write.")

        queryset = BattleReport.objects.select_related("run_progress").order_by("id")
        if limit is not None:
            queryset = queryset[:limit]

        totals = {
            "processed": 0,
            "created_progress": 0,
            "updated_progress": 0,
            "no_change": 0,
        }

        for report in queryset:
            totals["processed"] += 1
            parsed = parse_battle_report(report.raw_text)

            progress = getattr(report, "run_progress", None)
            created = False
            if progress is None:
                progress = BattleReportProgress(battle_report=report, player=report.player)
                created = True

            updated_fields = {
                "battle_date": parsed.battle_date,
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

            changed = created or any(getattr(progress, key) != value for key, value in updated_fields.items())
            if not changed:
                totals["no_change"] += 1
                continue

            totals["created_progress"] += int(created)
            totals["updated_progress"] += int(not created)

            if write:
                for key, value in updated_fields.items():
                    setattr(progress, key, value)
                progress.save()

        mode = "CHECK" if check else "WRITE"
        self.stdout.write(f"[{mode}] {totals}")
        return None
