"""Service-layer functions for the core app.

Services in `core` coordinate Django persistence concerns (ORM, transactions)
with pure parsing/analysis modules.
"""

from __future__ import annotations

from django.db import IntegrityError, transaction

from definitions.models import BotDefinition, UltimateWeaponDefinition
from gamedata.models import (
    BattleReport,
    BattleReportDerivedMetrics,
    BattleReportProgress,
    RunCombatUltimateWeapon,
    RunBot,
    RunUtilityUltimateWeapon,
)
from player_state.models import Player, Preset
from analysis.raw_text_metrics import extract_raw_text_metrics
from core.parsers.battle_report import (
    extract_bot_usage,
    extract_ultimate_weapon_usage,
    fallback_battle_date,
    parse_battle_report,
    record_unrecognized_unit_suffixes,
)


def ingest_battle_report(
    raw_text: str,
    *,
    player: Player,
    preset_name: str | None = None,
    is_tournament: bool = False,
    tournament_rank: str | None = None,
) -> tuple[BattleReport, bool]:
    """Ingest a Battle Report, rejecting duplicates by checksum.

    Args:
        raw_text: Raw Battle Report text as pasted by the user.
        player: Owning player derived from the authenticated user.
        preset_name: Optional preset label to associate with the run.
        is_tournament: Manual override to mark a run as a tournament.
        tournament_rank: Optional tournament rank label for manual tournament runs.

    Returns:
        A tuple of (battle_report, created) where `created` is False when the report
        is a duplicate.
    """

    parsed = parse_battle_report(raw_text)
    preset = _resolve_preset(preset_name, player=player)
    preset_snapshot = _preset_snapshot(preset)
    try:
        with transaction.atomic():
            record_unrecognized_unit_suffixes(raw_text)
            battle_report = BattleReport.objects.create(
                player=player,
                raw_text=raw_text,
                checksum=parsed.checksum,
            )
            _persist_derived_metrics(battle_report=battle_report, player=player, raw_text=raw_text)
            battle_date = fallback_battle_date(parsed.battle_date, parsed_at=battle_report.parsed_at)
            BattleReportProgress.objects.create(
                battle_report=battle_report,
                player=player,
                battle_date=battle_date,
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
                tournament_rank=(tournament_rank if is_tournament else None),
            )
            _ingest_run_bot_usage(battle_report=battle_report, player=player)
            _ingest_run_ultimate_weapon_usage(battle_report=battle_report, player=player)
            return battle_report, True
    except IntegrityError:
        battle_report = BattleReport.objects.get(player=player, checksum=parsed.checksum)
        record_unrecognized_unit_suffixes(raw_text)
        if preset is not None or is_tournament:
            BattleReportProgress.objects.filter(battle_report=battle_report, player=player).update(
                preset=preset,
                preset_name_snapshot=preset_snapshot["name"],
                preset_color_snapshot=preset_snapshot["color"],
                is_tournament=is_tournament,
                tournament_rank=(tournament_rank if is_tournament else None),
            )
        _persist_derived_metrics(battle_report=battle_report, player=player, raw_text=raw_text)
        _ingest_run_bot_usage(battle_report=battle_report, player=player)
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

    Returns:
        Number of RunBot rows created.
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


def _ingest_run_bot_usage(*, battle_report: BattleReport, player: Player) -> int:
    """Persist best-effort Bot usage rows for a Battle Report.

    Args:
        battle_report: Persisted BattleReport row to attach usage to.
        player: Owning player derived from the authenticated user.

    Notes:
        Usage rows are derived from the Battle Report raw text. Unknown names
        are ignored, and existing rows are left in place to keep ingestion
        idempotent for duplicate imports.
    """

    rows = _bot_usage_rows(battle_report=battle_report, player=player)
    if rows:
        RunBot.objects.bulk_create(rows)
    return len(rows)


def backfill_run_bot_usage(*, battle_report: BattleReport, player: Player) -> int:
    """Backfill bot usage rows for an existing Battle Report.

    Args:
        battle_report: Persisted BattleReport row to attach usage to.
        player: Owning player derived from the authenticated user.

    Returns:
        Number of RunBot rows created.
    """

    return _ingest_run_bot_usage(battle_report=battle_report, player=player)


def pending_run_bot_usage_count(*, battle_report: BattleReport, player: Player) -> int:
    """Return how many RunBot rows are missing for a report.

    Args:
        battle_report: Persisted BattleReport row to inspect.
        player: Owning player derived from the authenticated user.

    Returns:
        Count of RunBot rows that would be created on backfill.
    """

    return len(_bot_usage_rows(battle_report=battle_report, player=player))


def _bot_usage_rows(*, battle_report: BattleReport, player: Player) -> list[RunBot]:
    """Build missing RunBot rows inferred from raw text or derived metrics.

    Args:
        battle_report: Persisted BattleReport row to inspect.
        player: Owning player derived from the authenticated user.

    Returns:
        List of RunBot rows to create.
    """

    bot_names = set(extract_bot_usage(battle_report.raw_text or ""))
    bot_names.update(_bot_names_from_derived_metrics(battle_report))
    if not bot_names:
        return []

    definitions = {
        definition.name.casefold(): definition for definition in BotDefinition.objects.order_by("id")
    }
    existing_ids = set(
        RunBot.objects.filter(player=player, battle_report=battle_report).values_list(
            "bot_definition_id",
            flat=True,
        )
    )

    rows: list[RunBot] = []
    for name in bot_names:
        definition = definitions.get(name.casefold())
        if definition is None or definition.id in existing_ids:
            continue
        rows.append(
            RunBot(
                player=player,
                battle_report=battle_report,
                bot_definition=definition,
            )
        )
    return rows


def _bot_names_from_derived_metrics(battle_report: BattleReport) -> set[str]:
    """Return bot display names inferred from derived metrics values.

    Args:
        battle_report: BattleReport row with optional derived metrics.

    Returns:
        Set of bot display names inferred from derived metric values.
    """

    derived = getattr(battle_report, "derived_metrics", None)
    values = getattr(derived, "values", None)
    if not isinstance(values, dict):
        return set()
    metric_to_name = {
        "flame_bot_damage": "Flame Bot",
        "thunder_bot_stuns": "Thunder Bot",
        "golden_bot_coins_earned": "Golden Bot",
        "enemies_destroyed_in_golden_bot": "Golden Bot",
    }
    names: set[str] = set()
    for metric_key, name in metric_to_name.items():
        raw_value = values.get(metric_key)
        if raw_value is None:
            continue
        try:
            numeric = float(raw_value)
        except (TypeError, ValueError):
            continue
        if numeric > 0:
            names.add(name)
    return names
