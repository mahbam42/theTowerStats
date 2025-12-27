"""Service-layer functions for the core app.

Services in `core` coordinate Django persistence concerns (ORM, transactions)
with pure parsing/analysis modules.
"""

from __future__ import annotations

from django.db import IntegrityError, transaction

from definitions.models import UltimateWeaponDefinition
from gamedata.models import (
    BattleReport,
    BattleReportDerivedMetrics,
    BattleReportProgress,
    RunCombatUltimateWeapon,
    RunUtilityUltimateWeapon,
)
from player_state.models import Player, Preset
from analysis.raw_text_metrics import extract_raw_text_metrics
from core.parsers.battle_report import extract_ultimate_weapon_usage, parse_battle_report


def ingest_battle_report(
    raw_text: str, *, player: Player, preset_name: str | None = None, is_tournament: bool = False
) -> tuple[BattleReport, bool]:
    """Ingest a Battle Report, rejecting duplicates by checksum.

    Args:
        raw_text: Raw Battle Report text as pasted by the user.
        player: Owning player derived from the authenticated user.
        preset_name: Optional preset label to associate with the run.
        is_tournament: Manual override to mark a run as a tournament.

    Returns:
        A tuple of (battle_report, created) where `created` is False when the report
        is a duplicate.
    """

    parsed = parse_battle_report(raw_text)
    preset = _resolve_preset(preset_name, player=player)
    preset_snapshot = _preset_snapshot(preset)
    try:
        with transaction.atomic():
            battle_report = BattleReport.objects.create(
                player=player,
                raw_text=raw_text,
                checksum=parsed.checksum,
            )
            _persist_derived_metrics(battle_report=battle_report, player=player, raw_text=raw_text)
            BattleReportProgress.objects.create(
                battle_report=battle_report,
                player=player,
                battle_date=parsed.battle_date,
                tier=parsed.tier,
                wave=parsed.wave,
                real_time_seconds=parsed.real_time_seconds,
                preset=preset,
                preset_name_snapshot=preset_snapshot["name"],
                preset_color_snapshot=preset_snapshot["color"],
                killed_by=parsed.killed_by,
                coins_earned=parsed.coins_earned,
                coins_earned_raw=parsed.coins_earned_raw,
                cash_earned=parsed.cash_earned,
                cash_earned_raw=parsed.cash_earned_raw,
                interest_earned=parsed.interest_earned,
                interest_earned_raw=parsed.interest_earned_raw,
                gem_blocks_tapped=parsed.gem_blocks_tapped,
                cells_earned=parsed.cells_earned,
                reroll_shards_earned=parsed.reroll_shards_earned,
                is_tournament=is_tournament,
            )
            _ingest_run_ultimate_weapon_usage(battle_report=battle_report, player=player)
            return battle_report, True
    except IntegrityError:
        battle_report = BattleReport.objects.get(player=player, checksum=parsed.checksum)
        if preset is not None or is_tournament:
            BattleReportProgress.objects.filter(battle_report=battle_report, player=player).update(
                preset=preset,
                preset_name_snapshot=preset_snapshot["name"],
                preset_color_snapshot=preset_snapshot["color"],
                is_tournament=is_tournament,
            )
        _persist_derived_metrics(battle_report=battle_report, player=player, raw_text=raw_text)
        _ingest_run_ultimate_weapon_usage(battle_report=battle_report, player=player)
        return battle_report, False


def _resolve_preset(preset_name: str | None, *, player: Player) -> Preset | None:
    """Resolve an optional preset name into a Preset.

    Args:
        preset_name: Raw user input.
        player: Owning player derived from the authenticated user.

    Returns:
        A Preset instance when `preset_name` is non-empty; otherwise None.
    """

    if preset_name is None:
        return None
    cleaned = preset_name.strip()
    if not cleaned:
        return None
    preset, _ = Preset.objects.get_or_create(player=player, name=cleaned)
    return preset


def _preset_snapshot(preset: Preset | None) -> dict[str, str]:
    """Return a snapshot dict for optional preset display.

    Args:
        preset: Preset row when a preset label was applied; otherwise None.

    Returns:
        Dict with keys:
        - `name`: Stable display label captured at assignment time.
        - `color`: Stable palette key captured at assignment time.
    """

    if preset is None:
        return {"name": "", "color": ""}
    return {"name": preset.name, "color": preset.badge_color()}


def _persist_derived_metrics(*, battle_report: BattleReport, player: Player, raw_text: str) -> None:
    """Persist derived metrics parsed from the Battle Report raw text."""

    extracted = extract_raw_text_metrics(raw_text)
    values = {key: parsed.value for key, parsed in extracted.items()}
    raw_values = {key: parsed.raw_value for key, parsed in extracted.items()}
    BattleReportDerivedMetrics.objects.update_or_create(
        battle_report=battle_report,
        defaults={"player": player, "values": values, "raw_values": raw_values},
    )


def _ingest_run_ultimate_weapon_usage(*, battle_report: BattleReport, player: Player) -> None:
    """Persist best-effort Ultimate Weapon usage rows for a Battle Report.

    Args:
        battle_report: Persisted BattleReport row to attach usage to.
        player: Owning player derived from the authenticated user.

    Notes:
        Usage rows are derived from the Battle Report raw text. Unknown names
        are ignored, and existing rows are left in place to keep ingestion
        idempotent for duplicate imports.
    """

    combat_names, utility_names = extract_ultimate_weapon_usage(battle_report.raw_text or "")
    if not combat_names and not utility_names:
        return

    definitions = {
        definition.name.casefold(): definition
        for definition in UltimateWeaponDefinition.objects.order_by("id")
    }

    existing_combat_ids = set(
        RunCombatUltimateWeapon.objects.filter(
            player=player, battle_report=battle_report
        ).values_list("ultimate_weapon_definition_id", flat=True)
    )
    existing_utility_ids = set(
        RunUtilityUltimateWeapon.objects.filter(
            player=player, battle_report=battle_report
        ).values_list("ultimate_weapon_definition_id", flat=True)
    )

    combat_rows: list[RunCombatUltimateWeapon] = []
    for name in combat_names:
        definition = definitions.get(name.casefold())
        if definition is None or definition.id in existing_combat_ids:
            continue
        combat_rows.append(
            RunCombatUltimateWeapon(
                player=player,
                battle_report=battle_report,
                ultimate_weapon_definition=definition,
            )
        )

    utility_rows: list[RunUtilityUltimateWeapon] = []
    for name in utility_names:
        definition = definitions.get(name.casefold())
        if definition is None or definition.id in existing_utility_ids:
            continue
        utility_rows.append(
            RunUtilityUltimateWeapon(
                player=player,
                battle_report=battle_report,
                ultimate_weapon_definition=definition,
            )
        )

    if combat_rows:
        RunCombatUltimateWeapon.objects.bulk_create(combat_rows)
    if utility_rows:
        RunUtilityUltimateWeapon.objects.bulk_create(utility_rows)
