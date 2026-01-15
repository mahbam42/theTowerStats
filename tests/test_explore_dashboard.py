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


@pytest.mark.django_db
def test_explore_preview_returns_json(auth_client, player) -> None:
    """Explore previews return JSON payloads for modal rendering."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nRecovery Packages\t4\n",
        checksum="explore-preview".ljust(64, "y"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2025, 12, 6, tzinfo=timezone.utc),
        tier=6,
        wave=80,
        real_time_seconds=240,
    )
    BattleReportDerivedMetrics.objects.create(
        player=player,
        battle_report=report,
        values={"recovery_packages": 4},
        raw_values={"recovery_packages": "4"},
    )

    dsl_query = (
        'name "Recovery packages by run"\n'
        "scope date [date:YYYY-MM-DD]..[date:YYYY-MM-DD]\n"
        "scope tier [tier:—]\n"
        "scope preset [preset:—]\n"
        "scope snapshot [snapshot:—]\n"
        "scope past_n_runs [runs:—]\n"
        "breakdown by run\n"
        "metric recovery_packages sum\n"
        "output table\n"
    )

    response = auth_client.post(
        reverse("core:explore"),
        data={
            "dsl_query": dsl_query,
            "action": "run_explore_query",
        },
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["results"]["rows"]
    assert payload["results"]["rows"][0]["run_id"] == report.id


@pytest.mark.django_db
def test_explore_farming_efficiency_summary(auth_client, player) -> None:
    """Explore farming efficiency summary renders for avg coins/hour by tier."""

    def add_run(*, checksum: str, tier: int, coins: int, seconds: int) -> None:
        report = BattleReport.objects.create(
            player=player,
            raw_text="Battle Report\nCoins Earned\t0\n",
            checksum=checksum.ljust(64, "z"),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=player,
            battle_date=datetime(2025, 12, 7, tzinfo=timezone.utc),
            tier=tier,
            wave=100,
            coins_earned=coins,
            real_time_seconds=seconds,
        )

    for idx in range(3):
        add_run(checksum=f"farm-tier7-{idx}", tier=7, coins=1000, seconds=3600)
        add_run(checksum=f"farm-tier8-{idx}", tier=8, coins=1010, seconds=3600)
    for idx in range(2):
        add_run(checksum=f"farm-tier9-{idx}", tier=9, coins=980, seconds=3600)

    dsl_query = (
        'name "Farming efficiency by tier"\n'
        "scope date [date:YYYY-MM-DD]..[date:YYYY-MM-DD]\n"
        "scope tier all not tournament\n"
        "scope preset [preset:—]\n"
        "scope snapshot [snapshot:—]\n"
        "scope past_n_runs [runs:—]\n"
        "breakdown by tier\n"
        "metric coins_per_hour avg\n"
        "output table\n"
    )

    response = auth_client.post(
        reverse("core:explore"),
        data={
            "dsl_query": dsl_query,
            "action": "run_explore_query",
        },
    )

    assert response.status_code == 200
    summary = response.context["explore_farming"]
    assert summary is not None
    assert summary["best_tier"] == 8
    assert summary["plateau_tier"] == 8
    assert any("Low sample size" in warning for warning in summary["warnings"])


@pytest.mark.django_db
def test_explore_bar_chart_orders_tiers_numerically(auth_client, player) -> None:
    """Explore bar charts order tier breakdowns numerically."""

    def add_run(*, checksum: str, tier: int, coins: int) -> None:
        report = BattleReport.objects.create(
            player=player,
            raw_text="Battle Report\nCoins Earned\t0\n",
            checksum=checksum.ljust(64, "w"),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=player,
            battle_date=datetime(2025, 12, 8, tzinfo=timezone.utc),
            tier=tier,
            wave=50,
            coins_earned=coins,
            real_time_seconds=600,
        )

    add_run(checksum="tier-1", tier=1, coins=100)
    add_run(checksum="tier-11", tier=11, coins=1100)
    add_run(checksum="tier-2", tier=2, coins=200)

    dsl_query = (
        'name "Coins by tier"\n'
        "scope date [date:YYYY-MM-DD]..[date:YYYY-MM-DD]\n"
        "scope tier all not tournament\n"
        "scope preset [preset:—]\n"
        "scope snapshot [snapshot:—]\n"
        "scope past_n_runs [runs:—]\n"
        "breakdown by tier\n"
        "metric coins_earned sum\n"
        "output bar\n"
    )

    response = auth_client.post(
        reverse("core:explore"),
        data={
            "dsl_query": dsl_query,
            "action": "run_explore_query",
        },
    )

    assert response.status_code == 200
    chart = response.context["explore_results"]["chart"]
    assert chart["labels"] == ["Tier 1", "Tier 2", "Tier 11"]


@pytest.mark.django_db
def test_explore_multi_metric_table_renders_all_metrics(auth_client, player) -> None:
    """Explore multi-metric queries render values for each metric."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCells Earned\t12\n",
        checksum="multi-metric".ljust(64, "m"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2025, 12, 9, tzinfo=timezone.utc),
        tier=5,
        wave=120,
        coins_earned=3600,
        real_time_seconds=3600,
        cells_earned=12,
    )

    dsl_query = (
        'name "Multi metric"\n'
        "scope date [date:YYYY-MM-DD]..[date:YYYY-MM-DD]\n"
        "scope tier all not tournament\n"
        "scope preset [preset:—]\n"
        "scope snapshot [snapshot:—]\n"
        "scope past_n_runs [runs:—]\n"
        "breakdown by tier\n"
        "metric coins_per_hour avg and cells_earned avg\n"
        "output table\n"
    )

    response = auth_client.post(
        reverse("core:explore"),
        data={
            "dsl_query": dsl_query,
            "action": "run_explore_query",
        },
    )

    assert response.status_code == 200
    results = response.context["explore_results"]
    assert results is not None
    assert len(results["metrics"]) == 2
    assert results["rows"]
    first_row = results["rows"][0]
    assert len(first_row["metric_cells"]) == 2
