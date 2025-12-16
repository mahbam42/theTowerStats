"""Django integration tests for Phase 1 chart view."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

import pytest

from analysis.engine import analyze_runs
from gamedata.models import BattleReport, BattleReportProgress
from player_state.models import Player, Preset

FILTER_START = date(2025, 12, 1)


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

    response = client.get("/", {"start_date": FILTER_START})
    assert response.status_code == 200


@pytest.mark.django_db
def test_dashboard_view_renders_with_no_data(client) -> None:
    """Render the dashboard with no imported runs and show a neutral empty state."""

    response = client.get("/", {"start_date": FILTER_START})
    assert response.status_code == 200
    assert response.context["chart_empty_state"] == "No runs match the current filters."


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

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_per_hour"]
    labels = panel["labels"]
    values = panel["datasets"][0]["data"]

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

    response = client.get("/", {"tier": 2, "start_date": FILTER_START})
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_per_hour"]
    labels = panel["labels"]
    values = panel["datasets"][0]["data"]
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

    response = client.get("/", {"preset": preset.pk, "start_date": FILTER_START})
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_per_hour"]
    labels = panel["labels"]
    values = panel["datasets"][0]["data"]
    assert labels == ["2025-12-01"]
    assert values == [7200.0]


@pytest.mark.django_db
def test_dashboard_view_comparison_chart_by_tier(client) -> None:
    """Render a tier comparison chart with multiple datasets."""

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

    response = client.get("/", {"charts": ["coins_earned_by_tier"], "start_date": FILTER_START})
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    datasets = panels["coins_earned_by_tier"]["datasets"]
    dataset_labels = [d["label"] for d in datasets]
    assert dataset_labels == ["Tier 1", "Tier 2"]


@pytest.mark.django_db
def test_dashboard_view_series_includes_moving_average_transform(client) -> None:
    """Include explicit moving-average series when selected."""

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

    response = client.get("/", {"charts": ["coins_per_hour_moving_average"], "moving_average_window": 2, "start_date": FILTER_START})
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    datasets = panels["coins_per_hour_moving_average"]["datasets"]
    dataset_labels = [d["label"] for d in datasets]
    assert dataset_labels == ["Coins per Hour", "Moving Average"]


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

    response = client.get("/", {"start_date": FILTER_START})
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

    response = client.get("/", {"run_a": first.pk, "run_b": second.pk, "start_date": FILTER_START})
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


@pytest.mark.django_db
def test_dashboard_view_window_delta_ignores_chart_date_filters(client) -> None:
    """Keep comparison windows independent from chart start/end filters."""

    first = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="chartwin-a".ljust(64, "h"),
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
        checksum="chartwin-b".ljust(64, "i"),
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
            "start_date": date(2025, 12, 9),
            "window_a_start": date(2025, 12, 1),
            "window_a_end": date(2025, 12, 1),
            "window_b_start": date(2025, 12, 10),
            "window_b_end": date(2025, 12, 10),
        },
    )
    assert response.status_code == 200

    result = response.context["comparison_result"]
    assert result["kind"] == "windows"
    assert result["baseline_value"] == 7200.0
    assert result["comparison_value"] == 14400.0
    assert result["delta"].absolute == 7200.0


@pytest.mark.django_db
def test_dashboard_view_window_delta_respects_tier_filter(client) -> None:
    """Compute window deltas using only runs in the requested tier context."""

    # Window A: one run at tier 1 and one at tier 2 (same date window).
    a_tier_one = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="tierwin-a1".ljust(64, "a"),
    )
    BattleReportProgress.objects.create(
        battle_report=a_tier_one,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    a_tier_two = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    3,600\n",
        checksum="tierwin-a2".ljust(64, "b"),
    )
    BattleReportProgress.objects.create(
        battle_report=a_tier_two,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=2,
        wave=100,
        real_time_seconds=600,
    )

    # Window B: again, one run at each tier.
    b_tier_one = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="tierwin-b1".ljust(64, "c"),
    )
    BattleReportProgress.objects.create(
        battle_report=b_tier_one,
        battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    b_tier_two = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    1,800\n",
        checksum="tierwin-b2".ljust(64, "d"),
    )
    BattleReportProgress.objects.create(
        battle_report=b_tier_two,
        battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc),
        tier=2,
        wave=100,
        real_time_seconds=600,
    )

    # With tier=2, the comparison should use only the tier 2 runs:
    # - Window A avg: 3,600/600*3600 = 21,600
    # - Window B avg: 1,800/600*3600 = 10,800
    response = client.get(
        "/",
        {
            "tier": 2,
            "window_a_start": date(2025, 12, 1),
            "window_a_end": date(2025, 12, 1),
            "window_b_start": date(2025, 12, 10),
            "window_b_end": date(2025, 12, 10),
        },
    )
    assert response.status_code == 200

    result = response.context["comparison_result"]
    assert result["kind"] == "windows"
    assert result["baseline_value"] == 21600.0
    assert result["comparison_value"] == 10800.0
    assert result["delta"].absolute == -10800.0
    assert result["percent_display"] == -50.0


@pytest.mark.django_db
def test_dashboard_view_window_delta_respects_preset_filter(client) -> None:
    """Compute window deltas using only runs in the requested preset context."""

    player = Player.objects.create(name="default")
    farming = Preset.objects.create(player=player, name="Farming")

    tagged_a = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="presetwin-a".ljust(64, "e"),
    )
    BattleReportProgress.objects.create(
        battle_report=tagged_a,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        preset=farming,
    )

    untagged_a = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="presetwin-a2".ljust(64, "f"),
    )
    BattleReportProgress.objects.create(
        battle_report=untagged_a,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    tagged_b = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="presetwin-b".ljust(64, "g"),
    )
    BattleReportProgress.objects.create(
        battle_report=tagged_b,
        battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        preset=farming,
    )

    response = client.get(
        "/",
        {
            "preset": farming.pk,
            "window_a_start": date(2025, 12, 1),
            "window_a_end": date(2025, 12, 1),
            "window_b_start": date(2025, 12, 10),
            "window_b_end": date(2025, 12, 10),
        },
    )
    assert response.status_code == 200

    result = response.context["comparison_result"]
    assert result["kind"] == "windows"
    assert result["baseline_value"] == 7200.0
    assert result["comparison_value"] == 14400.0
    assert result["delta"].absolute == 7200.0
    assert result["percent_display"] == 100.0
