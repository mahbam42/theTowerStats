"""Django integration tests for Phase 1 chart view."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

import pytest
from django.test import override_settings
from django.urls import reverse

from analysis.engine import analyze_runs
from analysis.raw_text_metrics import extract_raw_text_metrics
from gamedata.models import BattleReport, BattleReportDerivedMetrics, BattleReportProgress
from player_state.models import ChartSnapshot, Preset
from core.views import WALKTHROUGH_FIRST_LOGIN_SESSION_KEY

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

    response = auth_client.get(reverse("core:dashboard"), {"start_date": FILTER_START})
    assert response.status_code == 200


@pytest.mark.django_db
def test_dashboard_walkthrough_is_available_on_first_login(auth_client) -> None:
    """Walkthrough eligibility is surfaced once for the first login session."""

    session = auth_client.session
    session[WALKTHROUGH_FIRST_LOGIN_SESSION_KEY] = True
    session.save()

    response = auth_client.get(reverse("core:dashboard"), {"start_date": FILTER_START})
    content = response.content.decode("utf-8")
    assert 'data-walkthrough-enabled="true"' in content

    response = auth_client.get(reverse("core:dashboard"), {"start_date": FILTER_START})
    content = response.content.decode("utf-8")
    assert 'data-walkthrough-enabled="true"' not in content


@pytest.mark.django_db
def test_dashboard_free_upgrades_chart_excludes_total_series(auth_client, player) -> None:
    """Free upgrades chart only stacks attack, defense, and utility series."""

    from datetime import date as date_type

    from core.services import ingest_battle_report

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 10, 2025 10:00",
            "Real Time\t1h 0m 0s",
            "Tier\t1",
            "Wave\t100",
            "Free Attack Upgrade\t10",
            "Free Defense Upgrade\t20",
            "Free Utility Upgrade\t30",
        ]
    )
    ingest_battle_report(raw_text, player=player, preset_name=None)

    response = auth_client.get(
        reverse("core:dashboard"),
        {"charts": ["free_upgrades_by_run"], "start_date": date_type(2025, 12, 9)},
    )
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["free_upgrades_by_run"]
    labels = [dataset.get("label") for dataset in panel["datasets"]]
    assert labels == ["Attack", "Defense", "Utility"]


@pytest.mark.django_db
@pytest.mark.regression
def test_dashboard_free_upgrades_chart_totals_sum_all_series(auth_client, player) -> None:
    """Totals for free upgrades sum all stacked series values."""

    from datetime import date as date_type

    from core.services import ingest_battle_report

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tJan 11, 2026 10:00",
            "Real Time\t1h 0m 0s",
            "Tier\t1",
            "Wave\t100",
            "Free Attack Upgrade\t622",
            "Free Defense Upgrade\t568",
            "Free Utility Upgrade\t607",
        ]
    )
    ingest_battle_report(raw_text, player=player, preset_name=None)

    response = auth_client.get(
        reverse("core:dashboard"),
        {"charts": ["free_upgrades_by_run"], "start_date": date_type(2026, 1, 10)},
    )
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["free_upgrades_by_run"]
    assert panel["totals"] == [1797.0]


@pytest.mark.django_db
def test_dashboard_view_renders_with_no_data(auth_client) -> None:
    """Render the dashboard with no imported runs and show a neutral empty state."""

    response = auth_client.get(reverse("core:dashboard"), {"start_date": FILTER_START})
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
    response = auth_client.post(reverse("core:dashboard"), data={"raw_text": raw_text}, follow=True)
    assert response.status_code == 200

    assert BattleReport.objects.filter(player=player).count() == 1
    assert "Battle Report imported." in response.content.decode("utf-8")


@pytest.mark.django_db
def test_dashboard_quick_import_allows_missing_battle_date(auth_client, player) -> None:
    """Dashboard quick import falls back to the parsed timestamp."""

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
    response = auth_client.post(reverse("core:dashboard"), data={"raw_text": raw_text}, follow=True)
    assert response.status_code == 200

    report = BattleReport.objects.get(player=player)
    assert report.run_progress.battle_date == report.parsed_at


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
    response = auth_client.post(reverse("core:dashboard"), data={"raw_text": raw_text}, follow=True)
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
    response = auth_client.post(reverse("core:dashboard"), data={"raw_text": raw_text}, follow=True)
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
    response = auth_client.post(
        reverse("core:dashboard"),
        data={"raw_text": raw_text, "is_tournament": "on", "tournament_rank": "gold"},
        follow=True,
    )
    assert response.status_code == 200
    assert response.context["chart_empty_state"] == "No runs match the current filters."

    response = auth_client.get(reverse("core:dashboard"), {"include_tournaments": "on", "start_date": FILTER_START})
    assert response.status_code == 200
    assert response.context["chart_empty_state"] != "No runs match the current filters."


@pytest.mark.django_db
def test_dashboard_hidden_runs_excluded_unless_included(auth_client, player) -> None:
    """Hidden Battle Reports stay out of charts unless included in the context."""

    visible_report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,000\n",
        checksum="h" * 64,
        is_hidden=False,
    )
    BattleReportProgress.objects.create(
        battle_report=visible_report,
        player=player,
        battle_date=datetime(2025, 12, 3, tzinfo=timezone.utc),
        tier=1,
        wave=10,
        real_time_seconds=60,
    )
    hidden_report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    2,000\n",
        checksum="i" * 64,
        is_hidden=True,
    )
    BattleReportProgress.objects.create(
        battle_report=hidden_report,
        player=player,
        battle_date=datetime(2025, 12, 4, tzinfo=timezone.utc),
        tier=1,
        wave=10,
        real_time_seconds=60,
    )

    response = auth_client.get(
        reverse("core:dashboard"),
        {"start_date": date(2025, 12, 1), "end_date": date(2025, 12, 5)},
    )
    assert response.status_code == 200
    assert response.context["scope_summary"]["runs_in_scope"] == 1

    response = auth_client.get(
        reverse("core:dashboard"),
        {
            "start_date": date(2025, 12, 1),
            "end_date": date(2025, 12, 5),
            "include_hidden": "on",
        },
    )
    assert response.status_code == 200
    assert response.context["scope_summary"]["runs_in_scope"] == 2


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_dashboard_import_exception_shows_user_error(auth_client, monkeypatch) -> None:
    """Unexpected ingest failures surface a safe error message in production."""

    def _boom(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("core.views.ingest_battle_report", _boom)
    response = auth_client.post(reverse("core:dashboard"), data={"raw_text": "Battle Report\nTier 1\nWave 1\nReal Time 1m\n"}, follow=True)
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

    response = auth_client.get(reverse("core:dashboard"), {"start_date": date(2025, 12, 2)})
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
@pytest.mark.regression
@pytest.mark.golden
def test_dashboard_view_date_filter_falls_back_to_import_time(auth_client, player) -> None:
    """Date filters fall back to the import timestamp when Battle Date is missing."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="z" * 64,
    )
    BattleReport.objects.filter(id=report.id).update(parsed_at=datetime(2025, 12, 2, 3, 0, tzinfo=timezone.utc))
    report.refresh_from_db()

    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=None,
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    response = auth_client.get(reverse("core:dashboard"), {"start_date": date(2025, 12, 2), "end_date": date(2025, 12, 2)})
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_per_hour"]
    assert panel["labels"] == ["2025-12-02"]
    assert panel["datasets"][0]["data"] == [7200.0]


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

    response = auth_client.get(reverse("core:dashboard"), {"tier": "tier:2", "start_date": FILTER_START})
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_per_hour"]
    labels = panel["labels"]
    values = panel["datasets"][0]["data"]
    assert labels == ["2025-12-02"]
    assert values == [14400.0]


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_view_tier_choices_include_tournament_filters(auth_client, player) -> None:
    """Tier selector includes tournament filter options."""

    response = auth_client.get(reverse("core:dashboard"))
    assert response.status_code == 200

    choices = {value for value, _label in response.context["chart_form"].fields["tier"].choices}
    assert "tournament:all" in choices
    assert "tournament:gold" in choices


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.golden
def test_dashboard_view_filters_by_tournament_rank(auth_client, player) -> None:
    """Filter charts by tournament rank selections."""

    gold_report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="g" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=gold_report,
        player=player,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        is_tournament=True,
        tournament_rank="gold",
    )

    silver_report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="s" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=silver_report,
        player=player,
        battle_date=datetime(2025, 12, 2, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        is_tournament=True,
        tournament_rank="silver",
    )

    response = auth_client.get(
        reverse("core:dashboard"),
        {"tier": "tournament:gold", "start_date": FILTER_START},
    )
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_per_hour"]
    assert panel["datasets"][0]["data"] == [7200.0]


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_view_snapshot_filter_combines_with_date_range(auth_client, player) -> None:
    """Snapshot filters intersect with the explicit date range."""

    reports = []
    for day, coins in ((1, 1200), (4, 2400), (10, 3600)):
        report = BattleReport.objects.create(
            player=player,
            raw_text=f"Battle Report\nCoins earned    {coins:,}\n",
            checksum=f"snapshot-{day}".ljust(64, "s"),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=player,
            battle_date=datetime(2025, 12, day, tzinfo=timezone.utc),
            tier=1,
            wave=100,
            real_time_seconds=600,
        )
        reports.append(report)

    snapshot = ChartSnapshot.objects.create(
        player=player,
        name="Early window",
        target="charts",
        chart_context={"start_date": "2025-12-01", "end_date": "2025-12-05"},
    )

    response = auth_client.get(
        reverse("core:dashboard"),
        {
            "context_snapshot": snapshot.id,
            "start_date": "2025-12-03",
            "end_date": "2025-12-10",
        },
    )
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_per_hour"]
    assert panel["labels"] == ["2025-12-04"]


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

    response = auth_client.get(reverse("core:dashboard"), {"preset": preset.pk, "start_date": FILTER_START})
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_per_hour"]
    labels = panel["labels"]
    values = panel["datasets"][0]["data"]
    assert labels == ["2025-12-01"]
    assert values == [7200.0]


@pytest.mark.django_db
def test_dashboard_view_filters_by_patch_boundary(auth_client, player) -> None:
    """Patch boundary filters limit charts to the selected window."""

    from definitions.models import PatchBoundary

    early_boundary = PatchBoundary.objects.create(
        boundary_date=date(2025, 12, 1),
        label="27.3",
    )
    PatchBoundary.objects.create(
        boundary_date=date(2025, 12, 10),
        label="27.4",
    )

    early_report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="patch-filter-early".ljust(64, "p"),
    )
    BattleReportProgress.objects.create(
        battle_report=early_report,
        player=player,
        battle_date=datetime(2025, 12, 5, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        coins_earned=1200,
    )

    late_report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="patch-filter-late".ljust(64, "q"),
    )
    BattleReportProgress.objects.create(
        battle_report=late_report,
        player=player,
        battle_date=datetime(2025, 12, 12, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        coins_earned=2400,
    )

    response = auth_client.get(
        reverse("core:dashboard"),
        {
            "charts": ["coins_earned"],
            "start_date": FILTER_START,
            "end_date": "2025-12-31",
            "patch_boundaries": [early_boundary.id],
        },
    )
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_earned"]
    assert panel["labels"] == ["2025-12-05"]


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

    response = auth_client.get(reverse("core:dashboard"), {"charts": ["coins_earned_by_tier"], "start_date": FILTER_START})
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

    response = auth_client.get(reverse("core:dashboard"),
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

    response = auth_client.get(reverse("core:dashboard"), {"start_date": FILTER_START})
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

    response = auth_client.get(reverse("core:dashboard"), {"run_a": first.pk, "run_b": second.pk, "start_date": FILTER_START})
    assert response.status_code == 200

    result = response.context["comparison_result"]
    assert result["kind"] == "runs"
    assert result["metric"] == "coins/hour"
    assert result["baseline_value"] == 7200.0
    assert result["comparison_value"] == 14400.0
    assert result["delta"].absolute == 7200.0
    assert result["percent_display"] == 100.0


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_view_compare_table_uses_unit_formatting_helper(auth_client, player) -> None:
    """Compare summary table renders unit formatting data attributes."""

    scope_a = []
    for idx, coins in enumerate((1200, 2400), start=1):
        report = BattleReport.objects.create(
            player=player,
            raw_text=f"Battle Report\nCoins earned    {coins:,}\n",
            checksum=f"format-a-{idx}".ljust(64, "a"),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=player,
            battle_date=datetime(2025, 12, idx, tzinfo=timezone.utc),
            tier=1,
            wave=100,
            real_time_seconds=600,
            coins_earned=coins,
        )
        scope_a.append(report)

    scope_b = []
    for idx, coins in enumerate((3600, 4800), start=3):
        report = BattleReport.objects.create(
            player=player,
            raw_text=f"Battle Report\nCoins earned    {coins:,}\n",
            checksum=f"format-b-{idx}".ljust(64, "b"),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=player,
            battle_date=datetime(2025, 12, idx, tzinfo=timezone.utc),
            tier=1,
            wave=100,
            real_time_seconds=600,
            coins_earned=coins,
        )
        scope_b.append(report)

    response = auth_client.get(
        reverse("core:dashboard"),
        {
            "scope_a_runs": [run.id for run in scope_a],
            "scope_b_runs": [run.id for run in scope_b],
            "summary_focus": "economy",
            "scope_average": "on",
            "start_date": FILTER_START,
        },
    )
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert 'data-format="unit-value"' in content


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_view_multi_run_scope_compare_defaults_to_economy(auth_client, player) -> None:
    """Summarize multi-run scopes and include goal-aware advice by default."""

    runs: list[BattleReport] = []
    for idx, coins in enumerate((1200, 2400, 3600, 2400, 3600, 4800), start=1):
        report = BattleReport.objects.create(
            player=player,
            raw_text=f"Battle Report\nCoins earned    {coins:,}\n",
            checksum=(f"multirun-{idx}".ljust(64, "x")),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=player,
            battle_date=datetime(2025, 12, idx, tzinfo=timezone.utc),
            tier=1,
            wave=100,
            real_time_seconds=600,
        )
        runs.append(report)

    response = auth_client.get(reverse("core:dashboard"),
        {
            "scope_a_runs": [runs[0].pk, runs[1].pk, runs[2].pk],
            "scope_b_runs": [runs[3].pk, runs[4].pk, runs[5].pk],
            "scope_average": "on",
        },
    )
    assert response.status_code == 200

    result = response.context["comparison_result"]
    assert result["kind"] == "run_sets"
    assert result["summary_focus"] == "economy"
    assert result["baseline_value"] == 14400.0
    assert result["comparison_value"] == 21600.0
    assert result["delta"].absolute == 7200.0
    assert result["percent_display"] == 50.0
    assert any(row["metric_key"] == "coins_per_hour" for row in result["metric_summaries"])

    advice_items = tuple(response.context["advice_items"])
    assert any("Observed change in coins/hour:" in item.title for item in advice_items)
    assert any(item.title.startswith("For your selected goal: Hybrid") for item in advice_items)


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_view_compare_scope_options_include_tiers_and_presets(auth_client, player) -> None:
    """Expose tier/preset options and run mappings for compare scopes."""

    preset = Preset.objects.create(player=player, name="Farming")
    reports = []
    for idx, tier in enumerate((1, 2, 1), start=1):
        report = BattleReport.objects.create(
            player=player,
            raw_text=f"Battle Report\nCoins earned    {1000 * idx}\n",
            checksum=(f"compare-options-{idx}".ljust(64, "x")),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=player,
            battle_date=datetime(2025, 12, idx, tzinfo=timezone.utc),
            tier=tier,
            wave=100,
            real_time_seconds=600,
            preset=preset if idx != 2 else None,
        )
        reports.append(report)

    response = auth_client.get(
        reverse("core:dashboard"),
        {"start_date": "2025-12-01", "end_date": "2025-12-31"},
    )
    assert response.status_code == 200

    tier_values = {opt["value"] for opt in response.context["compare_scope_tier_options"]}
    preset_options = response.context["compare_scope_preset_options"]
    run_map = json.loads(response.context["compare_scope_run_map_json"])

    assert tier_values == {"tier:1", "tier:2"}
    assert preset_options[0]["value"] == f"preset:{preset.id}"
    assert preset_options[0]["label"] == "Farming"
    assert set(run_map["tier:1"]) == {reports[0].id, reports[2].id}
    assert set(run_map[f"preset:{preset.id}"]) == {reports[0].id, reports[2].id}


@pytest.mark.django_db
def test_dashboard_view_compare_scope_options_include_patch_boundaries(auth_client, player) -> None:
    """Expose patch boundary scope options for compare selections."""

    from definitions.models import PatchBoundary

    boundary_a = PatchBoundary.objects.create(boundary_date=date(2025, 12, 1), label="27.3")
    boundary_b = PatchBoundary.objects.create(boundary_date=date(2025, 12, 10), label="27.4")

    early_report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="compare-patch-early".ljust(64, "a"),
    )
    BattleReportProgress.objects.create(
        battle_report=early_report,
        player=player,
        battle_date=datetime(2025, 12, 5, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        coins_earned=1200,
    )
    late_report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="compare-patch-late".ljust(64, "b"),
    )
    BattleReportProgress.objects.create(
        battle_report=late_report,
        player=player,
        battle_date=datetime(2025, 12, 12, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        coins_earned=2400,
    )

    response = auth_client.get(
        reverse("core:dashboard"),
        {"start_date": "2025-12-01", "end_date": "2025-12-31"},
    )
    assert response.status_code == 200

    patch_options = response.context["compare_scope_patch_options"]
    patch_values = {opt["value"] for opt in patch_options}
    run_map = json.loads(response.context["compare_scope_run_map_json"])

    assert patch_values == {
        f"patch:{boundary_a.boundary_date.isoformat()}",
        f"patch:{boundary_b.boundary_date.isoformat()}",
    }
    assert set(run_map[f"patch:{boundary_a.boundary_date.isoformat()}"]) == {early_report.id}
    assert set(run_map[f"patch:{boundary_b.boundary_date.isoformat()}"]) == {late_report.id}


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_view_compare_scope_options_include_tournaments(auth_client, player) -> None:
    """Expose tournament scope options when tournament runs are present."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="compare-tournament".ljust(64, "t"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        is_tournament=True,
        tournament_rank="gold",
    )

    response = auth_client.get(
        reverse("core:dashboard"),
        {"start_date": "2025-12-01", "end_date": "2025-12-31", "include_tournaments": "on"},
    )
    assert response.status_code == 200

    tournament_options = response.context["compare_scope_tournament_options"]
    run_map = json.loads(response.context["compare_scope_run_map_json"])

    option_values = {opt["value"] for opt in tournament_options}
    assert option_values == {"tournament:all", "tournament:gold"}
    assert set(run_map["tournament:all"]) == {report.id}
    assert set(run_map["tournament:gold"]) == {report.id}


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_view_warns_when_scope_sizes_are_skewed(auth_client, player) -> None:
    """Warn when scope A/B sizes differ significantly."""

    reports: list[BattleReport] = []
    for idx in range(10):
        report = BattleReport.objects.create(
            player=player,
            raw_text=f"Battle Report\nCoins earned    {1200 + idx * 100}\n",
            checksum=(f"scope-warn-{idx}".ljust(64, "w")),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=player,
            battle_date=datetime(2025, 12, idx + 1, tzinfo=timezone.utc),
            tier=1,
            wave=100,
            real_time_seconds=600,
        )
        reports.append(report)

    response = auth_client.get(
        reverse("core:dashboard"),
        {
            "scope_a_runs": [r.id for r in reports[:3]],
            "scope_b_runs": [r.id for r in reports[3:11]],
        },
    )
    assert response.status_code == 200
    assert response.context["comparison_scope_warning"] is not None


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_view_multi_run_scope_compare_insufficient(auth_client, player) -> None:
    """Return a single insufficient-data item when either scope is underfilled."""

    runs: list[BattleReport] = []
    for idx, coins in enumerate((1200, 2400, 3600, 2400), start=1):
        report = BattleReport.objects.create(
            player=player,
            raw_text=f"Battle Report\nCoins earned    {coins:,}\n",
            checksum=(f"multirun-thin-{idx}".ljust(64, "y")),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=player,
            battle_date=datetime(2025, 12, idx, tzinfo=timezone.utc),
            tier=1,
            wave=100,
            real_time_seconds=600,
        )
        runs.append(report)

    response = auth_client.get(reverse("core:dashboard"),
        {
            "scope_a_runs": [runs[0].pk, runs[1].pk],
            "scope_b_runs": [runs[2].pk, runs[3].pk],
        },
    )
    assert response.status_code == 200
    advice_items = tuple(response.context["advice_items"])
    assert len(advice_items) == 1
    assert advice_items[0].title == "Insufficient data to draw a conclusion."


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_view_average_scope_compare_allows_single_run(auth_client, player) -> None:
    """Allow averaged scope comparisons with single-run samples."""

    runs: list[BattleReport] = []
    for idx, coins in enumerate((1200, 2400), start=1):
        raw_text = "\n".join(
            [
                "Battle Report",
                "Real Time\t10m 0s",
                f"Coins earned\t{coins:,}",
                "",
            ]
        )
        report = BattleReport.objects.create(
            player=player,
            raw_text=raw_text,
            checksum=(f"multirun-average-{idx}".ljust(64, "a")),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=player,
            battle_date=datetime(2025, 12, idx, tzinfo=timezone.utc),
            tier=1,
            wave=100,
            real_time_seconds=600,
        )
        runs.append(report)

    response = auth_client.get(
        reverse("core:dashboard"),
        {
            "scope_average": "on",
            "scope_a_runs": [runs[0].pk],
            "scope_b_runs": [runs[1].pk],
        },
    )
    assert response.status_code == 200

    advice_items = tuple(response.context["advice_items"])
    assert len(advice_items) == 1
    assert advice_items[0].title.startswith("Observed change in coins/hour:")


@pytest.mark.django_db
@pytest.mark.regression
def test_dashboard_view_single_run_scope_compare_includes_summary_metrics(auth_client, player) -> None:
    """Show summary metrics for single-run scope comparisons without averaging."""

    runs: list[BattleReport] = []
    for idx, coins in enumerate((1200, 2400), start=1):
        raw_text = "\n".join(
            [
                "Battle Report",
                "Real Time\t10m 0s",
                f"Coins earned\t{coins:,}",
                "",
            ]
        )
        report = BattleReport.objects.create(
            player=player,
            raw_text=raw_text,
            checksum=(f"multirun-single-{idx}".ljust(64, "c")),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=player,
            battle_date=datetime(2025, 12, idx, tzinfo=timezone.utc),
            tier=1,
            wave=100,
            real_time_seconds=600,
        )
        runs.append(report)

    response = auth_client.get(
        reverse("core:dashboard"),
        {
            "scope_a_runs": [runs[0].pk],
            "scope_b_runs": [runs[1].pk],
        },
    )
    assert response.status_code == 200

    result = response.context["comparison_result"]
    assert result["kind"] == "run_sets"
    assert result["scope_summary_mode"] == "total"
    assert result["metric_summaries"]


@pytest.mark.django_db
@pytest.mark.regression
def test_dashboard_view_compare_modal_auto_opens_with_results(auth_client, player) -> None:
    """Auto-open the Compare modal when comparison results are present."""

    runs: list[BattleReport] = []
    for idx, coins in enumerate((1200, 2400), start=1):
        report = BattleReport.objects.create(
            player=player,
            raw_text=f"Battle Report\nCoins earned\t{coins:,}\n",
            checksum=(f"compare-auto-open-{idx}".ljust(64, "m")),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=player,
            battle_date=datetime(2025, 12, idx, tzinfo=timezone.utc),
            tier=1,
            wave=100,
            real_time_seconds=600,
            coins_earned=coins,
        )
        runs.append(report)

    response = auth_client.get(
        reverse("core:dashboard"),
        {
            "scope_a_runs": [runs[0].pk],
            "scope_b_runs": [runs[1].pk],
        },
    )
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert 'data-auto-open="true"' in content


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_view_multi_run_scope_compare_requires_focus_metrics(auth_client, player) -> None:
    """Degrade to insufficient data when the selected focus has no usable metrics."""

    runs: list[BattleReport] = []
    for idx, coins in enumerate((1200, 2400, 3600, 2400, 3600, 4800), start=1):
        report = BattleReport.objects.create(
            player=player,
            raw_text=f"Battle Report\nCoins earned    {coins:,}\n",
            checksum=(f"multirun-focus-{idx}".ljust(64, "z")),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=player,
            battle_date=datetime(2025, 12, idx, tzinfo=timezone.utc),
            tier=1,
            wave=100,
            real_time_seconds=600,
        )
        runs.append(report)

    response = auth_client.get(reverse("core:dashboard"),
        {
            "summary_focus": "damage",
            "scope_a_runs": [runs[0].pk, runs[1].pk, runs[2].pk],
            "scope_b_runs": [runs[3].pk, runs[4].pk, runs[5].pk],
        },
    )
    assert response.status_code == 200

    result = response.context["comparison_result"]
    assert result["kind"] == "run_sets"
    assert result["summary_focus"] == "damage"
    assert result["focus_metrics_sufficient"] is False
    assert result["metric_summaries"] == []

    advice_items = tuple(response.context["advice_items"])
    assert len(advice_items) == 1
    assert advice_items[0].title == "Insufficient data to draw a conclusion."


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

    response = auth_client.get(reverse("core:dashboard"),
        {
            "window_a_start": date(2025, 12, 1),
            "window_a_end": date(2025, 12, 2),
            "window_b_start": date(2025, 12, 9),
            "window_b_end": date(2025, 12, 10),
            "scope_average": "on",
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

    response = auth_client.get(reverse("core:dashboard"),
        {
            "start_date": date(2025, 12, 9),
            "window_a_start": date(2025, 12, 1),
            "window_a_end": date(2025, 12, 1),
            "window_b_start": date(2025, 12, 10),
            "window_b_end": date(2025, 12, 10),
            "scope_average": "on",
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
    response = auth_client.get(reverse("core:dashboard"),
        {
            "tier": "tier:2",
            "window_a_start": date(2025, 12, 1),
            "window_a_end": date(2025, 12, 1),
            "window_b_start": date(2025, 12, 10),
            "window_b_end": date(2025, 12, 10),
            "scope_average": "on",
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

    response = auth_client.get(reverse("core:dashboard"),
        {
            "preset": farming.pk,
            "window_a_start": date(2025, 12, 1),
            "window_a_end": date(2025, 12, 1),
            "window_b_start": date(2025, 12, 10),
            "window_b_end": date(2025, 12, 10),
            "scope_average": "on",
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
@pytest.mark.regression
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
            "Coins From Critical Coin\t250",
            "Coins From Golden Combo\t175",
            "Golden Bot Coins Earned\t578",
            "Guardian",
            "Guardian coins stolen\t1.20K",
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
    extracted = extract_raw_text_metrics(raw_text)
    BattleReportDerivedMetrics.objects.create(
        battle_report=report,
        player=player,
        values={key: parsed.value for key, parsed in extracted.items()},
        raw_values={key: parsed.raw_value for key, parsed in extracted.items()},
    )

    response = auth_client.get(reverse("core:dashboard"), {"charts": ["coins_by_source"], "start_date": date(2025, 12, 9)})
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_by_source"]
    assert panel["chart_type"] == "donut"
    assert len(panel["datasets"]) == 1
    labels = panel["labels"]
    values = panel["datasets"][0]["data"]
    death_wave_label = next(label for label in labels if label.startswith("Coins From Death Wave"))
    assert values[labels.index(death_wave_label)] == 2350.0
    critical_coin_label = next(label for label in labels if label.startswith("Coins From Critical Coin"))
    assert values[labels.index(critical_coin_label)] == 250.0
    golden_combo_label = next(label for label in labels if label.startswith("Coins From Golden Combo"))
    assert values[labels.index(golden_combo_label)] == 175.0
    golden_bot_label = next(label for label in labels if label.startswith("Golden Bot Coins Earned"))
    assert values[labels.index(golden_bot_label)] == 578.0
    stolen_label = next(label for label in labels if label.startswith("Guardian coins stolen"))
    assert values[labels.index(stolen_label)] == 1200.0
    assert not any(label.startswith("Other coins") for label in labels)


@pytest.mark.django_db
@pytest.mark.regression
def test_dashboard_view_renders_v28_single_space_damage_and_coin_sources(auth_client, player) -> None:
    """Section-scoped v28 metrics render from single-space clipboard pastes."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date Apr 10, 2026 18:12",
            "Game Time 2d 13h 1m 2s",
            "Real Time 13h 18m 35s",
            "Tier 3",
            "Wave 6402",
            "Killed By Fast",
            "Coins Earned 2.24B",
            "Coins Per Hour 168.38M",
            "Cells Earned 4.64K",
            "Cells Per Hour 349",
            "Damage",
            "Chain Lightning 2.77s",
            "Land Mines 40.40Q",
            "Death Wave 250.95q",
            "Smart Missiles 341.15q",
            "Electrons 0",
            "Rend Armor 0",
            "Black Hole 57.15S",
            "Coins",
            "Golden Tower 1.89B",
            "Black Hole 1.88B",
            "Spotlight 95.24M",
            "Coin Bonus Upgrade 1.98B",
            "Coins From Coin Bonuses 1.88B",
            "Critical Coin 0",
            "Golden Combo 0",
            "Death Wave 721.40M",
            "Golden Bot 196.57M",
            "Coins Fetched 3.33M",
            "Bounty Coins 32.49M",
            "Currencies",
            "Gems 146",
            "Ad Gems 120",
            "Medals 7",
            "Fetch Gems 28",
            "",
        ]
    )
    report = BattleReport.objects.create(player=player, raw_text=raw_text, checksum="single-space".ljust(64, "x"))
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2026, 4, 10, 18, 12, tzinfo=timezone.utc),
        tier=3,
        wave=6402,
        real_time_seconds=47_915,
        coins_earned=2_240_000_000,
        coins_earned_raw="2.24B",
        cells_earned=4640,
    )
    extracted = extract_raw_text_metrics(raw_text)
    BattleReportDerivedMetrics.objects.create(
        battle_report=report,
        player=player,
        values={key: parsed.value for key, parsed in extracted.items()},
        raw_values={key: parsed.raw_value for key, parsed in extracted.items()},
    )

    response = auth_client.get(
        reverse("core:dashboard"),
        {"charts": ["coins_by_source", "damage_by_source", "gems_earned", "medals_earned"], "start_date": date(2026, 4, 1)},
    )
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    damage_panel = panels["damage_by_source"]
    damage_labels = damage_panel["labels"]
    damage_values = damage_panel["datasets"][0]["data"]
    for label_prefix in ("Chain Lightning Damage", "Land Mine Damage", "Death Wave Damage", "Smart Missile Damage"):
        label = next(label for label in damage_labels if label.startswith(label_prefix))
        assert damage_values[damage_labels.index(label)] > 0
    for label_prefix in ("Electrons Damage", "Rend Armor Damage"):
        label = next(label for label in damage_labels if label.startswith(label_prefix))
        assert damage_values[damage_labels.index(label)] == 0.0

    coins_panel = panels["coins_by_source"]
    coins_labels = coins_panel["labels"]
    assert any(label.startswith("Coins From Critical Coin") for label in coins_labels)
    assert any(label.startswith("Coins From Golden Combo") for label in coins_labels)
    assert any(label.startswith("Golden Bot Coins Earned") for label in coins_labels)
    assert not any(label.startswith("Other coins") for label in coins_labels)

    gems_panel = panels["gems_earned"]
    assert gems_panel["datasets"][0]["data"] == [146.0]
    medals_panel = panels["medals_earned"]
    assert medals_panel["datasets"][0]["data"] == [7.0]


@pytest.mark.django_db
def test_dashboard_view_renders_empty_donut_with_typed_none_values(auth_client) -> None:
    """Render donut charts with no runs as typed-but-empty (None-valued) slices."""

    response = auth_client.get(reverse("core:dashboard"), {"charts": ["coins_by_source"], "start_date": date(2025, 12, 9)})
    assert response.status_code == 200
    assert response.context["chart_empty_state"] == "No runs match the current filters."

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_by_source"]
    assert panel["chart_type"] == "donut"
    assert len(panel["datasets"]) == 1
    values = panel["datasets"][0]["data"]
    assert values and all(value is None for value in values)


@pytest.mark.django_db
def test_dashboard_view_renders_area_chart(auth_client, player) -> None:
    """Render the Coins Earned Over Time area chart."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="area".ljust(64, "a"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2025, 12, 12, tzinfo=timezone.utc),
        tier=1,
        wave=50,
        real_time_seconds=1200,
    )

    response = auth_client.get(reverse("core:dashboard"), {"charts": ["coins_earned_over_time"], "start_date": date(2025, 12, 9)})
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_earned_over_time"]
    assert panel["chart_type"] == "area"
    assert panel["labels"] == ["2025-12-12"]
    assert panel["datasets"][0]["data"] == [1200.0]


@pytest.mark.django_db
def test_dashboard_view_renders_scatter_chart(auth_client, player) -> None:
    """Render the Run Duration vs Coins Earned scatter chart."""

    for idx, seconds in enumerate([3600, 5400], start=1):
        report = BattleReport.objects.create(
            player=player,
            raw_text=f"Battle Report\nCoins earned    {idx * 1000}\n",
            checksum=f"scatter{idx}".ljust(64, "s"),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=player,
            battle_date=datetime(2025, 12, 15 + idx, tzinfo=timezone.utc),
            tier=1,
            wave=100,
            real_time_seconds=seconds,
        )

    response = auth_client.get(reverse("core:dashboard"), {"charts": ["run_duration_vs_coins_earned"], "start_date": date(2025, 12, 9)})
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["run_duration_vs_coins_earned"]
    assert panel["chart_type"] == "scatter"
    assert panel["x_label"] == "Run duration"
    assert panel["y_label"] == "Coins earned"
    assert panel["x_unit"] == "hours"
    assert panel["y_unit"] == "coins"
    data_points = panel["datasets"][0]["data"]
    assert len(data_points) == 2
    assert data_points[0]["x"] == 1.0
    assert data_points[0]["y"] == 1000.0
    assert len(panel["run_ids"]) == 2


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

    response = auth_client.get(reverse("core:dashboard"),
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

    response = auth_client.get(reverse("core:dashboard"),
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
