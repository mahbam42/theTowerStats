"""Integration tests for comparison run labels."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from core.forms import GameDataChoiceField, GameDataMultipleChoiceField
from gamedata.models import BattleReport, BattleReportProgress

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_run_label_includes_tier_wave_date(player) -> None:
    """Run labels should include tier, wave, and date for compare selects."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="label-test".ljust(64, "x"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2025, 12, 10, 13, 45, tzinfo=timezone.utc),
        tier=6,
        wave=222,
        real_time_seconds=600,
    )

    single = GameDataChoiceField(queryset=BattleReport.objects.all())
    multi = GameDataMultipleChoiceField(queryset=BattleReport.objects.all())

    assert single.label_from_instance(report) == "T6 • W222 • 2025-12-10 13:45:00"
    assert multi.label_from_instance(report) == "T6 • W222 • 2025-12-10 13:45:00"
