"""Django integration tests for Phase 1 chart view."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

import pytest
from django.test import override_settings

from analysis.engine import analyze_runs
from gamedata.models import BattleReport, BattleReportProgress
from player_state.models import Preset

pytestmark = pytest.mark.integration

FILTER_START = date(2025, 12, 1)


@pytest.mark.django_db
def test_dashboard_view_renders(auth_client, player) -> None:
    """Create minimal records and verify the dashboard view returns HTTP 200."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins: 12345\n",
        checksum="x" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    response = auth_client.get("/", {"start_date": FILTER_START})
    assert response.status_code == 200


@pytest.mark.django_db
def test_dashboard_view_renders_with_no_data(auth_client) -> None:
    """Render the dashboard with no imported runs and show a neutral empty state."""

    response = auth_client.get("/", {"start_date": FILTER_START})
    assert response.status_code == 200
    assert response.context["chart_empty_state"] == "No runs match the current filters."


@pytest.mark.django_db
def test_dashboard_quick_import_accepts_space_separated_headers(auth_client, player) -> None:
    """Dashboard quick import accepts reports where headers are separated by multiple spaces."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date  Dec 21, 2025 13:18",
            "Tier  8",
            "Wave  1141",
            "Real Time  2h 46m 15s",
            "Coins earned  16.89M",
        ]
    )
    response = auth_client.post("/", data={"raw_text": raw_text}, follow=True)
    assert response.status_code == 200

    assert BattleReport.objects.filter(player=player).count() == 1
    assert "Battle Report imported." in response.content.decode("utf-8")


@pytest.mark.django_db
def test_dashboard_quick_import_allows_missing_battle_date(auth_client, player) -> None:
    """Dashboard quick import allows reports missing Battle Date."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Game Time\t1d 9h 39m 5s",
            "Real Time\t9h 3m 18s",
            "Tier\t1",
            "Wave\t3656",
            "Killed By\tFast",
            "Coins earned\t17.29M",
        ]
    )
    response = auth_client.post("/", data={"raw_text": raw_text}, follow=True)
    assert response.status_code == 200

    report = BattleReport.objects.get(player=player)
    assert report.run_progress.battle_date is None


@pytest.mark.django_db
def test_dashboard_quick_import_accepts_single_space_separators(auth_client, player) -> None:
    """Dashboard quick import accepts reports when the clipboard collapses tabs into single spaces."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date Dec 22, 2025 14:56",
            "Game Time 1d 9h 39m 5s",
            "Real Time 9h 3m 18s",
            "Tier 1",
            "Wave 3656",
            "Killed By Fast",
            "Coins earned 17.29M",
        ]
    )
    response = auth_client.post("/", data={"raw_text": raw_text}, follow=True)
    assert response.status_code == 200

    report = BattleReport.objects.get(player=player)
    assert report.run_progress.tier == 1
    assert report.run_progress.wave == 3656


@pytest.mark.django_db
def test_dashboard_quick_import_accepts_crlf_newlines(auth_client, player) -> None:
    """Dashboard quick import accepts reports pasted via textarea submissions using CRLF newlines."""

    raw_text = "\r\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 22, 2025 14:56",
            "Real Time\t9h 3m 18s",
            "Tier\t1",
            "Wave\t3656",
        ]
    )
    response = auth_client.post("/", data={"raw_text": raw_text}, follow=True)
    assert response.status_code == 200

    report = BattleReport.objects.get(player=player)
    assert report.run_progress.tier == 1


@pytest.mark.django_db
def test_dashboard_quick_import_tournament_override_excludes_from_charts_by_default(auth_client, player) -> None:
    """Tournament-tagged runs are excluded from charts unless explicitly included."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 22, 2025 14:56",
            "Real Time\t9h 3m 18s",
            "Tier\t1",
            "Wave\t3656",
            "Coins earned\t17.29M",
        ]
    )
    response = auth_client.post("/", data={"raw_text": raw_text, "is_tournament": "on"}, follow=True)
    assert response.status_code == 200
    assert response.context["chart_empty_state"] == "No runs match the current filters."

    response = auth_client.get("/", {"include_tournaments": "on", "start_date": FILTER_START})
    assert response.status_code == 200
    assert response.context["chart_empty_state"] != "No runs match the current filters."


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_dashboard_import_exception_shows_user_error(auth_client, monkeypatch) -> None:
    """Unexpected ingest failures surface a safe error message in production."""

    def _boom(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("core.views.ingest_battle_report", _boom)
    response = auth_client.post("/", data={"raw_text": "Battle Report\nTier 1\nWave 1\nReal Time 1m\n"}, follow=True)
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Could not import Battle Report." in content
    assert "Import failed." in content


@pytest.mark.django_db
def test_dashboard_view_filters_and_plots_from_analysis_engine(auth_client, player) -> None:
    """Filter runs by date and ensure the chart derives from Analysis Engine output."""

    first = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="a" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=first,
        player=player,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    second = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="b" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=second,
        player=player,
        battle_date=datetime(2025, 12, 2, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=1200,
    )

    response = auth_client.get("/", {"start_date": date(2025, 12, 2)})
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_per_hour"]
    labels = panel["labels"]
    values = panel["datasets"][0]["data"]

    assert labels == ["2025-12-02"]
    assert values == [7200.0]

    expected = analyze_runs(
        BattleReport.objects.select_related("run_progress").filter(
            player=player,
            run_progress__battle_date__date__gte=date(2025, 12, 2)
        )
    )
    expected_values = [round(run.coins_per_hour, 2) for run in expected.runs]

    assert values == expected_values


@pytest.mark.django_db
def test_dashboard_view_filters_by_tier(auth_client, player) -> None:
    """Filter runs by tier and ensure chart data reflects the filtered inputs."""

    tier_one = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="c" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=tier_one,
        player=player,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    tier_two = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="d" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=tier_two,
        player=player,
        battle_date=datetime(2025, 12, 2, tzinfo=timezone.utc),
        tier=2,
        wave=100,
        real_time_seconds=600,
    )

    response = auth_client.get("/", {"tier": 2, "start_date": FILTER_START})
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_per_hour"]
    labels = panel["labels"]
    values = panel["datasets"][0]["data"]
    assert labels == ["2025-12-02"]
    assert values == [14400.0]


@pytest.mark.django_db
def test_dashboard_view_filters_by_preset(auth_client, player) -> None:
    """Filter runs by preset label and ensure chart data reflects the filtered inputs."""

    preset = Preset.objects.create(player=player, name="Farming")

    tagged = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="e" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=tagged,
        player=player,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        preset=preset,
    )

    untagged = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="f" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=untagged,
        player=player,
        battle_date=datetime(2025, 12, 2, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    response = auth_client.get("/", {"preset": preset.pk, "start_date": FILTER_START})
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_per_hour"]
    labels = panel["labels"]
    values = panel["datasets"][0]["data"]
    assert labels == ["2025-12-01"]
    assert values == [7200.0]


@pytest.mark.django_db
def test_dashboard_view_comparison_chart_by_tier(auth_client, player) -> None:
    """Render a tier comparison chart with multiple datasets."""

    first = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="g" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=first,
        player=player,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    second = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="h" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=second,
        player=player,
        battle_date=datetime(2025, 12, 2, tzinfo=timezone.utc),
        tier=2,
        wave=100,
        real_time_seconds=600,
    )

    response = auth_client.get("/", {"charts": ["coins_earned_by_tier"], "start_date": FILTER_START})
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    datasets = panels["coins_earned_by_tier"]["datasets"]
    dataset_labels = [d["label"] for d in datasets]
    assert dataset_labels == ["Tier 1", "Tier 2"]


@pytest.mark.django_db
def test_dashboard_view_series_includes_moving_average_transform(auth_client, player) -> None:
    """Include explicit moving-average series when selected."""

    first = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="ma" * 32,
    )
    BattleReportProgress.objects.create(
        battle_report=first,
        player=player,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    second = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="mb" * 32,
    )
    BattleReportProgress.objects.create(
        battle_report=second,
        player=player,
        battle_date=datetime(2025, 12, 2, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    response = auth_client.get(
        "/",
        {
            "charts": ["coins_per_hour_moving_average"],
            "moving_average_window": 2,
            "start_date": FILTER_START,
        },
    )
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    datasets = panels["coins_per_hour_moving_average"]["datasets"]
    dataset_labels = [d["label"] for d in datasets]
    assert dataset_labels == ["Coins per Hour", "Moving Average"]


@pytest.mark.django_db
def test_dashboard_view_includes_legend_toggle_handler(auth_client, player) -> None:
    """Ensure the dashboard template includes a safe legend toggle handler."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins: 12345\n",
        checksum="toggle" * 10 + "x" * 4,
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    response = auth_client.get("/", {"start_date": FILTER_START})
    assert response.status_code == 200
    assert b"setDatasetVisibility" in response.content


@pytest.mark.django_db
def test_dashboard_view_run_delta_comparison(auth_client, player) -> None:
    """Compute a run-vs-run delta for coins/hour."""

    first = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="i" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=first,
        player=player,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    second = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="j" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=second,
        player=player,
        battle_date=datetime(2025, 12, 2, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    response = auth_client.get("/", {"run_a": first.pk, "run_b": second.pk, "start_date": FILTER_START})
    assert response.status_code == 200

    result = response.context["comparison_result"]
    assert result["kind"] == "runs"
    assert result["metric"] == "coins/hour"
    assert result["baseline_value"] == 7200.0
    assert result["comparison_value"] == 14400.0
    assert result["delta"].absolute == 7200.0
    assert result["percent_display"] == 100.0


@pytest.mark.django_db
def test_dashboard_view_window_delta_comparison(auth_client, player) -> None:
    """Compute a window-vs-window delta for coins/hour."""

    first = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="k" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=first,
        player=player,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    second = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="l" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=second,
        player=player,
        battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    response = auth_client.get(
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
def test_dashboard_view_window_delta_ignores_chart_date_filters(auth_client, player) -> None:
    """Keep comparison windows independent from chart start/end filters."""

    first = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="chartwin-a".ljust(64, "h"),
    )
    BattleReportProgress.objects.create(
        battle_report=first,
        player=player,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    second = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="chartwin-b".ljust(64, "i"),
    )
    BattleReportProgress.objects.create(
        battle_report=second,
        player=player,
        battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    response = auth_client.get(
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
def test_dashboard_view_window_delta_respects_tier_filter(auth_client, player) -> None:
    """Compute window deltas using only runs in the requested tier context."""

    # Window A: one run at tier 1 and one at tier 2 (same date window).
    a_tier_one = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="tierwin-a1".ljust(64, "a"),
    )
    BattleReportProgress.objects.create(
        battle_report=a_tier_one,
        player=player,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    a_tier_two = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    3,600\n",
        checksum="tierwin-a2".ljust(64, "b"),
    )
    BattleReportProgress.objects.create(
        battle_report=a_tier_two,
        player=player,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=2,
        wave=100,
        real_time_seconds=600,
    )

    # Window B: again, one run at each tier.
    b_tier_one = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="tierwin-b1".ljust(64, "c"),
    )
    BattleReportProgress.objects.create(
        battle_report=b_tier_one,
        player=player,
        battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    b_tier_two = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,800\n",
        checksum="tierwin-b2".ljust(64, "d"),
    )
    BattleReportProgress.objects.create(
        battle_report=b_tier_two,
        player=player,
        battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc),
        tier=2,
        wave=100,
        real_time_seconds=600,
    )

    # With tier=2, the comparison should use only the tier 2 runs:
    # - Window A avg: 3,600/600*3600 = 21,600
    # - Window B avg: 1,800/600*3600 = 10,800
    response = auth_client.get(
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
def test_dashboard_view_window_delta_respects_preset_filter(auth_client, player) -> None:
    """Compute window deltas using only runs in the requested preset context."""

    farming = Preset.objects.create(player=player, name="Farming")

    tagged_a = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="presetwin-a".ljust(64, "e"),
    )
    BattleReportProgress.objects.create(
        battle_report=tagged_a,
        player=player,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        preset=farming,
    )

    untagged_a = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="presetwin-a2".ljust(64, "f"),
    )
    BattleReportProgress.objects.create(
        battle_report=untagged_a,
        player=player,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    tagged_b = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="presetwin-b".ljust(64, "g"),
    )
    BattleReportProgress.objects.create(
        battle_report=tagged_b,
        player=player,
        battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        preset=farming,
    )

    response = auth_client.get(
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


@pytest.mark.django_db
def test_dashboard_view_renders_coins_by_source_donut(auth_client, player) -> None:
    """Render the Coins Earned by Source donut chart from Battle Report values."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 14, 2025 01:39",
            "Real Time\t17m 35s",
            "Tier\t11",
            "Wave\t121",
            "Coins earned\t1.24M",
            "Utility",
            "Coins From Death Wave\t2.35K",
            "Coins From Golden Tower\t62.30K",
            "Coins From Black Hole\t0",
            "Coins From Spotlight\t1.76K",
            "Coins From Orb\t0",
            "Coins from Coin Upgrade\t832.21K",
            "Coins from Coin Bonuses\t335.53K",
            "Guardian",
            "Guardian coins stolen\t0",
            "Coins Fetched\t805",
            "",
        ]
    )
    report = BattleReport.objects.create(player=player, raw_text=raw_text, checksum="donut".ljust(64, "x"))
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2025, 12, 14, 1, 39, tzinfo=timezone.utc),
        tier=11,
        wave=121,
        real_time_seconds=1055,
    )

    response = auth_client.get("/", {"charts": ["coins_by_source"], "start_date": date(2025, 12, 9)})
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_by_source"]
    assert panel["chart_type"] == "donut"
    assert len(panel["datasets"]) == 1
    labels = panel["labels"]
    values = panel["datasets"][0]["data"]
    death_wave_label = next(label for label in labels if label.startswith("Coins From Death Wave"))
    assert values[labels.index(death_wave_label)] == 2350.0
    other_label = next(label for label in labels if label.startswith("Other coins"))
    assert values[labels.index(other_label)] == 5045.0
    assert sum(v for v in values if v is not None) == 1_240_000.0


@pytest.mark.django_db
def test_dashboard_view_renders_empty_donut_with_typed_none_values(auth_client) -> None:
    """Render donut charts with no runs as typed-but-empty (None-valued) slices."""

    response = auth_client.get("/", {"charts": ["coins_by_source"], "start_date": date(2025, 12, 9)})
    assert response.status_code == 200
    assert response.context["chart_empty_state"] == "No runs match the current filters."

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_by_source"]
    assert panel["chart_type"] == "donut"
    assert len(panel["datasets"]) == 1
    values = panel["datasets"][0]["data"]
    assert values and all(value is None for value in values)


@pytest.mark.django_db
def test_dashboard_view_applies_rolling_window_last_runs(auth_client, player) -> None:
    """Apply the rolling window after date filtering."""

    for idx, day in enumerate([1, 2, 3], start=1):
        report = BattleReport.objects.create(
            player=player,
            raw_text=f"Battle Report\nCoins earned    {idx * 100}\n",
            checksum=f"roll{idx}".ljust(64, "r"),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=player,
            battle_date=datetime(2025, 12, day, tzinfo=timezone.utc),
            tier=1,
            wave=10,
            real_time_seconds=10,
        )

    response = auth_client.get(
        "/",
        {
            "charts": ["coins_earned"],
            "start_date": FILTER_START,
            "window_kind": "last_runs",
            "window_n": 2,
        },
    )
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_earned"]
    assert panel["labels"] == ["2025-12-02", "2025-12-03"]


@pytest.mark.django_db
def test_dashboard_view_applies_rolling_window_last_days(auth_client, player) -> None:
    """Apply a last-N-days rolling window after base context filtering."""

    for idx, day in enumerate([1, 2, 3], start=1):
        report = BattleReport.objects.create(
            player=player,
            raw_text=f"Battle Report\nCoins earned    {idx * 100}\n",
            checksum=f"days{idx}".ljust(64, "d"),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=player,
            battle_date=datetime(2025, 12, day, tzinfo=timezone.utc),
            tier=1,
            wave=10,
            real_time_seconds=10,
        )

    response = auth_client.get(
        "/",
        {
            "charts": ["coins_earned"],
            "start_date": FILTER_START,
            "window_kind": "last_days",
            "window_n": 2,
        },
    )
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_earned"]
    assert panel["labels"] == ["2025-12-02", "2025-12-03"]
