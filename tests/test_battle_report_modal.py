"""Integration tests for the Battle Report modal payload."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from gamedata.models import BattleReport, BattleReportProgress

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_battle_report_modal_payload_includes_metrics_and_raw_text(auth_client, player) -> None:
    """Modal payload returns raw text and metric link metadata."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="z" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        tier=2,
        wave=100,
        real_time_seconds=600,
        coins_earned=1200,
        coins_earned_raw="1,200",
        gem_blocks_tapped=3,
    )

    response = auth_client.get(reverse("core:battle_report_modal", args=[report.id]))
    assert response.status_code == 200

    payload = response.json()
    assert payload["ok"] is True
    assert payload["report"]["raw_text"].startswith("Battle Report")
    assert payload["report"]["run_number"] == 1

    metrics = {metric["key"]: metric for metric in payload["report"]["metrics"]}
    assert metrics["coins_earned"]["chart_id"] == "coins_earned"
    assert metrics["coins_per_hour"]["value"] == "7,200.00"
    assert metrics["gem_blocks_tapped"]["chart_id"] is None
    assert metrics["interest_earned"]["value"] == "—"


@pytest.mark.django_db
def test_battle_report_modal_run_number_is_player_scoped(auth_client, player) -> None:
    """Modal run numbers use player-scoped ordering."""

    user_model = get_user_model()
    other_user = user_model.objects.create_user(username="bob", password="password")
    other_player = other_user.player

    for idx in range(2):
        report = BattleReport.objects.create(
            player=other_player,
            raw_text="Battle Report\nCoins earned    1,200\n",
            checksum=(f"other-{idx}".ljust(64, "x")),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=other_player,
            battle_date=datetime(2025, 12, idx + 1, tzinfo=timezone.utc),
            tier=1,
            wave=100,
            real_time_seconds=600,
            coins_earned=1200,
        )

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="player-report".ljust(64, "y"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2025, 12, 3, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        coins_earned=2400,
    )

    response = auth_client.get(reverse("core:battle_report_modal", args=[report.id]))
    assert response.status_code == 200

    payload = response.json()
    assert payload["report"]["run_number"] == 1


@pytest.mark.django_db
def test_battle_report_modal_marks_fallback_battle_date(auth_client, player) -> None:
    """Modal payload marks fallback battle dates."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="fallback-date".ljust(64, "x"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=report.parsed_at,
        tier=2,
        wave=100,
        real_time_seconds=600,
    )

    response = auth_client.get(reverse("core:battle_report_modal", args=[report.id]))
    assert response.status_code == 200

    payload = response.json()
    assert payload["report"]["battle_date_fallback"] is True
