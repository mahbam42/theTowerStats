"""Service-layer functions for the core app.

Services in `core` coordinate Django persistence concerns (ORM, transactions)
with pure parsing/analysis modules.
"""

from __future__ import annotations

from django.db import IntegrityError, transaction

from core.models import GameData, RunProgress
from core.parsers.battle_report import parse_battle_report


def ingest_battle_report(raw_text: str) -> tuple[GameData, bool]:
    """Ingest a Battle Report, rejecting duplicates by checksum.

    Args:
        raw_text: Raw Battle Report text as pasted by the user.

    Returns:
        A tuple of (game_data, created) where `created` is False when the report
        is a duplicate.
    """

    parsed = parse_battle_report(raw_text)
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
            )
            return game_data, True
    except IntegrityError:
        return GameData.objects.get(checksum=parsed.checksum), False
