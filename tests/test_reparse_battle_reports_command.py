"""Integration tests for the reparse_battle_reports management command."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from django.core.management import call_command

from core.parsers.battle_report import compute_battle_report_checksum
from gamedata.models import BattleReport, BattleReportDerivedMetrics, BattleReportProgress

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_reparse_battle_reports_backfills_progress_fields(player) -> None:
    """Reparsing populates progress fields for existing Battle Reports."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 07, 2025 21:59",
            "Real Time\t2h 17m 23s",
            "Tier\t7",
            "Wave\t1301",
            "Killed By\tBoss",
            "Coins earned\t17.55M",
            "Cash earned\t$55.90M",
            "Interest earned\t$2.13M",
            "Coins From Golden Tower\t1.25M",
            "Gem Blocks Tapped\t3",
            "Cells Earned\t346",
            "Reroll Shards Earned\t373",
            "",
        ]
    )

    report = BattleReport.objects.create(
        player=player,
        raw_text=raw_text,
        checksum=compute_battle_report_checksum(raw_text),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2025, 12, 7, 21, 59, tzinfo=timezone.utc),
        tier=7,
        wave=1301,
        real_time_seconds=8243,
    )

    call_command("reparse_battle_reports", "--write")

    progress = BattleReportProgress.objects.get(battle_report=report)
    assert progress.killed_by == "Boss"
    assert progress.coins_earned == 17_550_000
    assert progress.coins_earned_raw == "17.55M"
    assert progress.cash_earned == 55_900_000
    assert progress.cash_earned_raw == "$55.90M"
    assert progress.interest_earned == 2_130_000
    assert progress.interest_earned_raw == "$2.13M"
    assert progress.gem_blocks_tapped == 3
    assert progress.cells_earned == 346
    assert progress.reroll_shards_earned == 373
    derived = BattleReportDerivedMetrics.objects.get(battle_report=report)
    assert derived.values["coins_from_golden_tower"] == 1_250_000
    assert derived.raw_values["coins_from_golden_tower"] == "1.25M"


@pytest.mark.django_db
def test_reparse_battle_reports_check_does_not_write(player) -> None:
    """Check mode reports changes without updating stored progress rows."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 07, 2025 21:59",
            "Real Time\t2h 17m 23s",
            "Tier\t7",
            "Wave\t1301",
            "Killed By\tBoss",
            "Coins earned\t17.55M",
            "",
        ]
    )

    report = BattleReport.objects.create(
        player=player,
        raw_text=raw_text,
        checksum=compute_battle_report_checksum(raw_text),
    )
    BattleReportProgress.objects.create(battle_report=report, player=player)

    call_command("reparse_battle_reports", "--check")

    progress = BattleReportProgress.objects.get(battle_report=report)
    assert progress.coins_earned is None
    assert not BattleReportDerivedMetrics.objects.filter(battle_report=report).exists()
