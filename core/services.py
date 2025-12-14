"""Service-layer functions for the core app.

Services in `core` coordinate Django persistence concerns (ORM, transactions)
with pure parsing/analysis modules.
"""

from __future__ import annotations

from django.db import IntegrityError, transaction

from core.models import GameData, PresetTag, RunProgress
from core.parsers.battle_report import parse_battle_report


def ingest_battle_report(
    raw_text: str, *, preset_name: str | None = None
) -> tuple[GameData, bool]:
    """Ingest a Battle Report, rejecting duplicates by checksum.

    Args:
        raw_text: Raw Battle Report text as pasted by the user.
        preset_name: Optional preset label to associate with the run.

    Returns:
        A tuple of (game_data, created) where `created` is False when the report
        is a duplicate.
    """

    parsed = parse_battle_report(raw_text)
    preset_tag = _resolve_preset_tag(preset_name)
    try:
        with transaction.atomic():
            game_data = GameData.objects.create(
                raw_text=raw_text,
                checksum=parsed.checksum,
            )
            RunProgress.objects.create(
                game_data=game_data,
                battle_date=parsed.battle_date,
                tier=parsed.tier,
                wave=parsed.wave,
                real_time_seconds=parsed.real_time_seconds,
                preset_tag=preset_tag,
            )
            return game_data, True
    except IntegrityError:
        game_data = GameData.objects.get(checksum=parsed.checksum)
        if preset_tag is not None:
            RunProgress.objects.filter(game_data=game_data).update(preset_tag=preset_tag)
        return game_data, False


def _resolve_preset_tag(preset_name: str | None) -> PresetTag | None:
    """Resolve an optional preset name into a PresetTag.

    Args:
        preset_name: Raw user input.

    Returns:
        A PresetTag instance when `preset_name` is non-empty; otherwise None.
    """

    if preset_name is None:
        return None
    cleaned = preset_name.strip()
    if not cleaned:
        return None
    preset_tag, _ = PresetTag.objects.get_or_create(name=cleaned)
    return preset_tag
