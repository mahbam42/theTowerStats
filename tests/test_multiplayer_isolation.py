"""Regression tests for Phase 8 multi-player data isolation."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from gamedata.models import BattleReport, BattleReportProgress

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_dashboard_and_battle_history_are_player_scoped(client) -> None:
    """Each authenticated user sees only their own run data."""

    user_model = get_user_model()
    user_a = user_model.objects.create_user(username="user_a", password="password")
    user_b = user_model.objects.create_user(username="user_b", password="password")
    player_a = user_a.player
    player_b = user_b.player

    report_a = BattleReport.objects.create(
        player=player_a,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="a" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=report_a,
        player=player_a,
        battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc),
        tier=1,
        wave=111,
        real_time_seconds=600,
        coins_earned=1200,
    )

    report_b = BattleReport.objects.create(
        player=player_b,
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="b" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=report_b,
        player=player_b,
        battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc),
        tier=1,
        wave=222,
        real_time_seconds=600,
        coins_earned=2400,
    )

    client.force_login(user_a)
    dashboard = client.get(reverse("core:dashboard"), {"start_date": date(2025, 12, 9)})
    assert dashboard.status_code == 200

    panels = {p["id"]: p for p in json.loads(dashboard.context["chart_panels_json"])}
    coins_panel = panels["coins_earned"]
    assert coins_panel["labels"] == ["2025-12-10"]
    assert coins_panel["datasets"][0]["data"] == [1200.0]

    history = client.get(reverse("core:battle_history"))
    assert history.status_code == 200
    content = history.content.decode("utf-8")
    assert ">111<" in content
    assert ">222<" not in content


@pytest.mark.django_db
@pytest.mark.regression
def test_chart_run_numbers_are_player_scoped(client) -> None:
    """Charts use run numbers scoped to the signed-in player."""

    user_model = get_user_model()
    user_a = user_model.objects.create_user(username="user_a", password="password")
    user_b = user_model.objects.create_user(username="user_b", password="password")
    player_a = user_a.player
    player_b = user_b.player

    for idx, hour in enumerate((1, 2), start=1):
        report = BattleReport.objects.create(
            player=player_b,
            raw_text=f"Battle Report\nCoins earned    {idx},000\n",
            checksum="b" * 64 if idx == 1 else "c" * 64,
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=player_b,
            battle_date=datetime(2025, 12, 10, hour, 0, tzinfo=timezone.utc),
            tier=1,
            wave=100 + idx,
            real_time_seconds=600,
            coins_earned=1000 * idx,
        )

    report_a1 = BattleReport.objects.create(
        player=player_a,
        raw_text="Battle Report\nCoins earned    1,500\n",
        checksum="a" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=report_a1,
        player=player_a,
        battle_date=datetime(2025, 12, 10, 3, 0, tzinfo=timezone.utc),
        tier=1,
        wave=111,
        real_time_seconds=600,
        coins_earned=1500,
    )
    report_a2 = BattleReport.objects.create(
        player=player_a,
        raw_text="Battle Report\nCoins earned    2,000\n",
        checksum="d" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=report_a2,
        player=player_a,
        battle_date=datetime(2025, 12, 10, 4, 0, tzinfo=timezone.utc),
        tier=1,
        wave=122,
        real_time_seconds=600,
        coins_earned=2000,
    )

    client.force_login(user_a)
    dashboard = client.get(
        reverse("core:dashboard"),
        {
            "charts": ["coins_earned"],
            "start_date": date(2025, 12, 9),
            "end_date": date(2025, 12, 11),
        },
    )
    assert dashboard.status_code == 200

    panels = {p["id"]: p for p in json.loads(dashboard.context["chart_panels_json"])}
    labels = panels["coins_earned"]["labels"]
    assert any("Run 1" in label for label in labels)
    assert any("Run 2" in label for label in labels)
    assert all(f"Run {report_a1.id}" not in label for label in labels)
    assert all(f"Run {report_a2.id}" not in label for label in labels)
