"""Service-layer functions for the core app.

Services in `core` coordinate Django persistence concerns (ORM, transactions)
with pure parsing/analysis modules.
"""

from __future__ import annotations

from django.db import IntegrityError, transaction

from gamedata.models import BattleReport, BattleReportProgress
from player_state.models import Player, Preset
from core.parsers.battle_report import parse_battle_report


def ingest_battle_report(
    raw_text: str, *, player: Player, preset_name: str | None = None
) -> tuple[BattleReport, bool]:
    """Ingest a Battle Report, rejecting duplicates by checksum.

    Args:
        raw_text: Raw Battle Report text as pasted by the user.
        player: Owning player derived from the authenticated user.
        preset_name: Optional preset label to associate with the run.

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
            )
            return battle_report, True
    except IntegrityError:
        battle_report = BattleReport.objects.get(player=player, checksum=parsed.checksum)
        if preset is not None:
            BattleReportProgress.objects.filter(battle_report=battle_report, player=player).update(
                preset=preset,
                preset_name_snapshot=preset_snapshot["name"],
                preset_color_snapshot=preset_snapshot["color"],
            )
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
