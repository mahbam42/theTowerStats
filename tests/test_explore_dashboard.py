"""Integration tests for the Explore dashboard."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from django.urls import reverse

from gamedata.models import BattleReport, BattleReportDerivedMetrics, BattleReportProgress
from player_state.models import ExploreQuery

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_explore_view_renders(auth_client, player) -> None:
    """Explore dashboard renders with an empty state."""

    response = auth_client.get(reverse("core:explore"))
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Explore Battles" in content
    assert "explore-dsl-input" in content


@pytest.mark.django_db
def test_explore_query_runs_and_saves(auth_client, player) -> None:
    """Explore queries can run and be saved."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nRecovery Packages\t9\n",
        checksum="explore-run".ljust(64, "x"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2025, 12, 5, tzinfo=timezone.utc),
        tier=7,
        wave=100,
        real_time_seconds=300,
    )
    BattleReportDerivedMetrics.objects.create(
        player=player,
        battle_report=report,
        values={"recovery_packages": 9},
        raw_values={"recovery_packages": "9"},
    )

    dsl_query = (
        'name "Recovery packages by tier"\n'
        "scope date [date:YYYY-MM-DD]..[date:YYYY-MM-DD]\n"
        "scope tier [tier:—]\n"
        "scope preset [preset:—]\n"
        "scope snapshot [snapshot:—]\n"
        "scope past_n_runs [runs:—]\n"
        "breakdown by tier\n"
        "metric recovery_packages sum\n"
        "output table\n"
    )

    run_response = auth_client.post(
        reverse("core:explore"),
        data={
            "dsl_query": dsl_query,
            "action": "run_explore_query",
        },
    )
    assert run_response.status_code == 200
    assert run_response.context["explore_results"] is not None
    assert run_response.context["explore_results"]["rows"]

    save_response = auth_client.post(
        reverse("core:explore"),
        data={
            "dsl_query": dsl_query,
            "action": "save_explore_query",
        },
        follow=True,
    )
    assert save_response.status_code == 200
    assert ExploreQuery.objects.filter(player=player, name="Recovery packages by tier").exists()
