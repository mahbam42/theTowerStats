"""Django integration tests for Phase 1 chart view."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

import pytest

from analysis.engine import analyze_runs
from gamedata.models import BattleReport, BattleReportProgress
from player_state.models import Player, Preset


@pytest.mark.django_db
def test_dashboard_view_renders(client) -> None:
    """Create minimal records and verify the dashboard view returns HTTP 200."""

    report = BattleReport.objects.create(
        raw_text="Battle Report\nCoins: 12345\n", checksum="x" * 64
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_dashboard_view_renders_with_no_data(client) -> None:
    """Render the dashboard with no imported runs and show a neutral empty state."""

    response = client.get("/")
    assert response.status_code == 200
    assert response.context["chart_empty_state"] == "No battle reports yet. Import one to see charts."


@pytest.mark.django_db
def test_dashboard_view_filters_and_plots_from_analysis_engine(client) -> None:
    """Filter runs by date and ensure the chart derives from Analysis Engine output."""

    first = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="a" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=first,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    second = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="b" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=second,
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
        BattleReport.objects.select_related("run_progress").filter(
            run_progress__battle_date__date__gte=date(2025, 12, 2)
        )
    )
    expected_values = [round(run.coins_per_hour, 2) for run in expected.runs]

    assert values == expected_values


@pytest.mark.django_db
def test_dashboard_view_filters_by_tier(client) -> None:
    """Filter runs by tier and ensure chart data reflects the filtered inputs."""

    tier_one = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="c" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=tier_one,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    tier_two = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="d" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=tier_two,
        battle_date=datetime(2025, 12, 2, tzinfo=timezone.utc),
        tier=2,
        wave=100,
        real_time_seconds=600,
    )

    response = client.get("/", {"tier": 2})
    assert response.status_code == 200

    labels = json.loads(response.context["chart_labels_json"])
    values = json.loads(response.context["chart_values_json"])
    assert labels == ["2025-12-02"]
    assert values == [14400.0]


@pytest.mark.django_db
def test_dashboard_view_filters_by_preset(client) -> None:
    """Filter runs by preset label and ensure chart data reflects the filtered inputs."""

    player = Player.objects.create(name="default")
    preset = Preset.objects.create(player=player, name="Farming")

    tagged = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="e" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=tagged,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        preset=preset,
    )

    untagged = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="f" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=untagged,
        battle_date=datetime(2025, 12, 2, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    response = client.get("/", {"preset": preset.pk})
    assert response.status_code == 200

    labels = json.loads(response.context["chart_labels_json"])
    values = json.loads(response.context["chart_values_json"])
    assert labels == ["2025-12-01"]
    assert values == [7200.0]


@pytest.mark.django_db
def test_dashboard_view_overlays_by_tier(client) -> None:
    """Overlay tier datasets when requested."""

    first = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="g" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=first,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    second = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="h" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=second,
        battle_date=datetime(2025, 12, 2, tzinfo=timezone.utc),
        tier=2,
        wave=100,
        real_time_seconds=600,
    )

    response = client.get("/", {"overlay_group": "tier"})
    assert response.status_code == 200

    datasets = json.loads(response.context["chart_datasets_json"])
    dataset_labels = [d["label"] for d in datasets]
    assert dataset_labels == ["Tier 1", "Tier 2"]


@pytest.mark.django_db
def test_dashboard_view_overlays_include_moving_average(client) -> None:
    """Include moving-average datasets when requested."""

    first = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="ma" * 32,
    )
    BattleReportProgress.objects.create(
        battle_report=first,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    second = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="mb" * 32,
    )
    BattleReportProgress.objects.create(
        battle_report=second,
        battle_date=datetime(2025, 12, 2, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    response = client.get(
        "/",
        {
            "overlay_group": "tier",
            "moving_average_window": 2,
        },
    )
    assert response.status_code == 200

    datasets = json.loads(response.context["chart_datasets_json"])
    dataset_labels = [d["label"] for d in datasets]
    assert dataset_labels == ["Tier 1", "Tier 1 (MA2)"]


@pytest.mark.django_db
def test_dashboard_view_includes_legend_toggle_handler(client) -> None:
    """Ensure the dashboard template includes a safe legend toggle handler."""

    report = BattleReport.objects.create(
        raw_text="Battle Report\nCoins: 12345\n",
        checksum="toggle" * 10 + "x" * 4,
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    response = client.get("/")
    assert response.status_code == 200
    assert b"setDatasetVisibility" in response.content


@pytest.mark.django_db
def test_dashboard_view_run_delta_comparison(client) -> None:
    """Compute a run-vs-run delta for coins/hour."""

    first = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="i" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=first,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    second = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="j" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=second,
        battle_date=datetime(2025, 12, 2, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    response = client.get("/", {"run_a": first.pk, "run_b": second.pk})
    assert response.status_code == 200

    result = response.context["comparison_result"]
    assert result["kind"] == "runs"
    assert result["metric"] == "coins/hour"
    assert result["baseline_value"] == 7200.0
    assert result["comparison_value"] == 14400.0
    assert result["delta"].absolute == 7200.0
    assert result["percent_display"] == 100.0


@pytest.mark.django_db
def test_dashboard_view_window_delta_comparison(client) -> None:
    """Compute a window-vs-window delta for coins/hour."""

    first = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="k" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=first,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    second = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="l" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=second,
        battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    response = client.get(
        "/",
        {
            "window_a_start": date(2025, 12, 1),
            "window_a_end": date(2025, 12, 2),
            "window_b_start": date(2025, 12, 9),
            "window_b_end": date(2025, 12, 10),
        },
    )
    assert response.status_code == 200

    result = response.context["comparison_result"]
    assert result["kind"] == "windows"
    assert result["metric"] == "coins/hour"
    assert result["baseline_value"] == 7200.0
    assert result["comparison_value"] == 14400.0
    assert result["delta"].absolute == 7200.0
