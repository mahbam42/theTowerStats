"""Django integration tests for Phase 1 chart view."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

import pytest

from analysis.engine import analyze_runs
from core.models import GameData, RunProgress


@pytest.mark.django_db
def test_dashboard_view_renders(client) -> None:
    """Create minimal records and verify the dashboard view returns HTTP 200."""

    game_data = GameData.objects.create(
        raw_text="Battle Report\nCoins: 12345\n", checksum="x" * 64
    )
    RunProgress.objects.create(
        game_data=game_data,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_dashboard_view_filters_and_plots_from_analysis_engine(client) -> None:
    """Filter runs by date and ensure the chart derives from Analysis Engine output."""

    first = GameData.objects.create(
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="a" * 64,
    )
    RunProgress.objects.create(
        game_data=first,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    second = GameData.objects.create(
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="b" * 64,
    )
    RunProgress.objects.create(
        game_data=second,
        battle_date=datetime(2025, 12, 2, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=1200,
    )

    response = client.get("/", {"start_date": date(2025, 12, 2)})
    assert response.status_code == 200

    labels = json.loads(response.context["chart_labels_json"])
    values = json.loads(response.context["chart_values_json"])

    assert labels == ["2025-12-02"]
    assert values == [7200.0]

    expected = analyze_runs(
        GameData.objects.select_related("run_progress").filter(
            run_progress__battle_date__date__gte=date(2025, 12, 2)
        )
    )
    expected_values = [round(run.coins_per_hour, 2) for run in expected.runs]

    assert values == expected_values
