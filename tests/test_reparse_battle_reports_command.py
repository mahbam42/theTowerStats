"""Integration tests for the reparse_battle_reports management command."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from django.core.management import call_command
from definitions.models import PatchBoundary

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


@pytest.mark.django_db
def test_reparse_battle_reports_falls_back_to_parsed_at(player) -> None:
    """Reparsing backfills missing battle dates from parsed_at."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Real Time\t2h 17m 23s",
            "Tier\t7",
            "Wave\t1301",
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

    call_command("reparse_battle_reports", "--write")

    progress = BattleReportProgress.objects.get(battle_report=report)
    assert progress.battle_date == report.parsed_at


@pytest.mark.django_db
def test_reparse_battle_reports_respects_patch_boundary(player) -> None:
    """Patch filtering limits reparsing to the selected window."""

    PatchBoundary.objects.create(boundary_date=datetime(2025, 12, 10, tzinfo=timezone.utc).date(), label="27.2.3")
    PatchBoundary.objects.create(boundary_date=datetime(2025, 12, 15, tzinfo=timezone.utc).date(), label="27.2.4")

    in_window_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 12, 2025 10:00",
            "Real Time\t1h 0m 0s",
            "Tier\t3",
            "Wave\t200",
            "Coins earned\t1.20M",
        ]
    )
    out_window_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 16, 2025 10:00",
            "Real Time\t1h 0m 0s",
            "Tier\t3",
            "Wave\t200",
            "Coins earned\t2.40M",
        ]
    )

    in_window_report = BattleReport.objects.create(
        player=player,
        raw_text=in_window_text,
        checksum=compute_battle_report_checksum(in_window_text),
    )
    BattleReportProgress.objects.create(
        battle_report=in_window_report,
        player=player,
        battle_date=datetime(2025, 12, 12, 10, 0, tzinfo=timezone.utc),
    )

    out_window_report = BattleReport.objects.create(
        player=player,
        raw_text=out_window_text,
        checksum=compute_battle_report_checksum(out_window_text),
    )
    BattleReportProgress.objects.create(
        battle_report=out_window_report,
        player=player,
        battle_date=datetime(2025, 12, 16, 10, 0, tzinfo=timezone.utc),
    )

    call_command("reparse_battle_reports", "--write", "--patch", "27.2.3")

    in_window_progress = BattleReportProgress.objects.get(battle_report=in_window_report)
    out_window_progress = BattleReportProgress.objects.get(battle_report=out_window_report)
    assert in_window_progress.coins_earned == 1_200_000
    assert out_window_progress.coins_earned is None
