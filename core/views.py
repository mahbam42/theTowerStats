"""Views for Phase 1 ingestion and Phase 3 navigation structure."""

from __future__ import annotations

import hashlib
import json

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from typing import Callable, TypedDict

from analysis.aggregations import (
    summarize_window,
    simple_moving_average,
)
from analysis.deltas import delta
from analysis.engine import analyze_metric_series, analyze_runs
from analysis.dto import MetricPoint, RunAnalysis
from analysis.metrics import get_metric_definition
from core.analysis_context import RevisionPolicy, build_player_context
from core.forms import BattleReportImportForm, ChartContextForm, ComparisonForm
from definitions.models import CardDefinition
from gamedata.models import BattleReport
from player_state.models import Player, PlayerCard, Preset
from core.services import ingest_battle_report


class ChartDataset(TypedDict, total=False):
    """A Chart.js dataset payload for the dashboard line chart."""

    label: str
    metricKey: str
    metricKind: str
    unit: str
    seriesKind: str
    data: list[float | None]
    borderColor: str
    backgroundColor: str
    spanGaps: bool
    borderDash: list[int]
    borderWidth: int
    pointRadius: int
    pointHoverRadius: int
    tension: float


class ChartData(TypedDict):
    """The full Chart.js payload (labels + datasets) for the dashboard."""

    labels: list[str]
    datasets: list[ChartDataset]


def dashboard(request: HttpRequest) -> HttpResponse:
    """Render the Phase 1 dashboard (import form + single time-series chart)."""

    if request.method == "POST":
        import_form = BattleReportImportForm(request.POST)
        if import_form.is_valid():
            raw_text = import_form.cleaned_data["raw_text"]
            preset_name = import_form.cleaned_data.get("preset_name") or None
            _, created = ingest_battle_report(raw_text, preset_name=preset_name)
            if created:
                messages.success(request, "Battle Report imported.")
            else:
                messages.warning(request, "Duplicate Battle Report ignored.")
            return redirect("core:dashboard")
    else:
        import_form = BattleReportImportForm()

    chart_form = ChartContextForm(request.GET)
    chart_form.is_valid()

    runs = _filtered_runs(chart_form)
    total_filtered_runs = runs.count()
    context_runs = _context_filtered_runs(chart_form)
    base_analysis = analyze_runs(context_runs)

    metric_key = chart_form.cleaned_data.get("metric") or "coins_per_hour"
    metric_def = get_metric_definition(metric_key)
    player_context = None
    revision_assumption: str | None = None
    if metric_def.kind == "derived":
        player_context = build_player_context(revision_policy=RevisionPolicy(mode="latest"))
        revision_assumption = (
            "Parameter revision policy: latest by WikiData.last_seen (tie-breaker: id)."
        )

    series_result = analyze_metric_series(
        runs,
        metric_key=metric_key,
        context=player_context,
        monte_carlo_trials=chart_form.cleaned_data.get("ev_trials"),
        monte_carlo_seed=chart_form.cleaned_data.get("ev_seed"),
    )
    metric_assumptions = list(series_result.assumptions)
    if revision_assumption:
        metric_assumptions.append(revision_assumption)

    chart_data = _build_chart_data(
        series_result.points,
        metric_def=series_result.metric,
        overlay_group=chart_form.cleaned_data.get("overlay_group") or "none",
        moving_average_window=chart_form.cleaned_data.get("moving_average_window"),
    )

    comparison_form = ComparisonForm(request.GET, runs_queryset=context_runs)
    comparison_form.is_valid()
    comparison_result = _build_comparison_result(
        comparison_form,
        base_analysis=base_analysis.runs,
    )

    chart_context = _chart_context_summary(chart_form)
    chart_empty_state = _chart_empty_state_message(
        total_filtered_runs=total_filtered_runs,
        chartable_runs=sum(1 for point in series_result.points if point.value is not None),
        has_filters=_form_has_filters(chart_form),
    )

    context = {
        "import_form": import_form,
        "chart_form": chart_form,
        "comparison_form": comparison_form,
        "comparison_result": comparison_result,
        "metric_definition": series_result.metric,
        "metric_assumptions": tuple(metric_assumptions),
        "used_parameters": series_result.used_parameters,
        "chart_context_json": json.dumps(chart_context),
        "chart_empty_state": chart_empty_state,
        "chart_labels_json": json.dumps(chart_data["labels"]),
        "chart_datasets_json": json.dumps(chart_data["datasets"]),
        "chart_values_json": json.dumps(chart_data["datasets"][0]["data"])
        if chart_data["datasets"]
        else "[]",
    }
    return render(request, "core/dashboard.html", context)


def battle_history(request: HttpRequest) -> HttpResponse:
    """Render a simple list of imported runs with minimal metadata."""

    runs = (
        BattleReport.objects.select_related("run_progress", "run_progress__preset")
        .order_by("-run_progress__battle_date", "-parsed_at")
    )
    return render(
        request,
        "core/battle_history.html",
        {"runs": runs},
    )


def cards(request: HttpRequest) -> HttpResponse:
    """Render the cards page (definitions + player progress + preset labels)."""

    definitions = CardDefinition.objects.order_by("name")
    player, _ = Player.objects.get_or_create(name="default")
    player_cards = PlayerCard.objects.filter(player=player).select_related("card_definition").order_by(
        "card_slug"
    )
    presets = Preset.objects.filter(player=player).order_by("name")
    return render(
        request,
        "core/cards.html",
        {
            "definitions": definitions,
            "player_cards": player_cards,
            "presets": presets,
        },
    )


def ultimate_weapon_progress(request: HttpRequest) -> HttpResponse:
    """Render the Ultimate Weapon progress page."""

    return render(request, "core/ultimate_weapon_progress.html", {})


def guardian_progress(request: HttpRequest) -> HttpResponse:
    """Render the Guardian progress page."""

    return render(request, "core/guardian_progress.html", {})


def bots_progress(request: HttpRequest) -> HttpResponse:
    """Render the Bots progress page."""

    return render(request, "core/bots_progress.html", {})


def _filtered_runs(filter_form: ChartContextForm) -> QuerySet[BattleReport]:
    """Return a filtered BattleReport queryset based on validated form data."""

    runs = BattleReport.objects.select_related(
        "run_progress",
        "run_progress__preset",
    ).order_by("run_progress__battle_date")
    if not filter_form.is_valid():
        return runs

    start_date = filter_form.cleaned_data.get("start_date")
    end_date = filter_form.cleaned_data.get("end_date")
    tier = filter_form.cleaned_data.get("tier")
    preset = filter_form.cleaned_data.get("preset")
    if start_date:
        runs = runs.filter(run_progress__battle_date__date__gte=start_date)
    if end_date:
        runs = runs.filter(run_progress__battle_date__date__lte=end_date)
    if tier:
        runs = runs.filter(run_progress__tier=tier)
    if preset:
        runs = runs.filter(run_progress__preset=preset)
    return runs


def _context_filtered_runs(filter_form: ChartContextForm) -> QuerySet[BattleReport]:
    """Return a queryset filtered only by tier/preset context.

    This is used for comparisons where the selected windows should remain
    independent of any chart date filters.
    """

    runs = BattleReport.objects.select_related(
        "run_progress",
        "run_progress__preset",
    ).order_by("run_progress__battle_date")
    if not filter_form.is_valid():
        return runs

    tier = filter_form.cleaned_data.get("tier")
    preset = filter_form.cleaned_data.get("preset")
    if tier:
        runs = runs.filter(run_progress__tier=tier)
    if preset:
        runs = runs.filter(run_progress__preset=preset)
    return runs


def _build_chart_data(
    runs: tuple[MetricPoint, ...],
    *,
    metric_def: object,
    overlay_group: str,
    moving_average_window: int | None,
) -> ChartData:
    """Build Chart.js-friendly labels and datasets from analysis output."""

    metric_key = getattr(metric_def, "key", "coins_per_hour")
    metric_kind = getattr(metric_def, "kind", "observed")
    unit = getattr(metric_def, "unit", "coins/hour")

    group_key: Callable[[MetricPoint], object]
    label_for_key: Callable[[object], str]
    color_for_key: Callable[[object], str]

    if overlay_group == "tier":
        def group_key(run: MetricPoint) -> object:
            """Group key function for tier overlays."""

            return run.tier

        def label_for_key(key: object) -> str:
            """Render dataset labels for tier overlays."""

            return f"Tier {key}" if isinstance(key, int) else "Tier (unknown)"

        def color_for_key(key: object) -> str:
            """Return a stable color for a tier overlay dataset."""

            return _color_for_tier(key)
    elif overlay_group == "preset":
        def group_key(run: MetricPoint) -> object:
            """Group key function for preset overlays."""

            return run.preset_name

        def label_for_key(key: object) -> str:
            """Render dataset labels for preset overlays."""

            return str(key) if isinstance(key, str) and key.strip() else "No preset"
        
        def color_for_key(key: object) -> str:
            """Return a stable color for a preset overlay dataset."""

            return _color_for_preset(key)
    else:
        def group_key(_run: MetricPoint) -> object:
            """Group key function for the single-dataset baseline chart."""

            return "all"

        def label_for_key(_key: object) -> str:
            """Render dataset labels for the single-dataset baseline chart."""

            label = getattr(metric_def, "label", None)
            if isinstance(label, str) and label.strip():
                return label
            return unit

        def color_for_key(_key: object) -> str:
            """Return the standard color for the baseline metric dataset."""

            return "#3366CC"

    groups: dict[object, list[MetricPoint]] = {}
    for run in runs:
        key = group_key(run)
        groups.setdefault(key, []).append(run)

    labels = sorted({run.battle_date.date().isoformat() for run in runs})
    datasets: list[ChartDataset] = []

    sorted_groups = sorted(groups.items(), key=lambda kv: str(kv[0]))
    for key, group_runs in sorted_groups:
        series = _daily_average_series_points(group_runs)
        data = [round(series[label], 2) if label in series else None for label in labels]
        color = color_for_key(key)
        dataset_label = label_for_key(key)
        datasets.append(
            {
                "label": dataset_label,
                "metricKey": metric_key,
                "metricKind": metric_kind,
                "unit": unit,
                "seriesKind": "raw",
                "data": data,
                "borderColor": color,
                "backgroundColor": color,
                "spanGaps": False,
                "borderWidth": 2,
                "pointRadius": 2,
                "pointHoverRadius": 5,
                "tension": 0.15,
            }
        )

        if moving_average_window is not None:
            ma = simple_moving_average(data, window=moving_average_window)
            datasets.append(
                {
                    "label": f"{dataset_label} (MA{moving_average_window})",
                    "metricKey": metric_key,
                    "metricKind": metric_kind,
                    "unit": unit,
                    "seriesKind": "moving_average",
                    "data": [round(v, 2) if v is not None else None for v in ma],
                    "borderColor": _hex_to_rgba(color, alpha=0.85),
                    "backgroundColor": _hex_to_rgba(color, alpha=0.85),
                    "borderDash": [6, 4],
                    "spanGaps": False,
                    "borderWidth": 2,
                    "pointRadius": 0,
                    "pointHoverRadius": 3,
                    "tension": 0.15,
                }
            )

    return {"labels": labels, "datasets": datasets}


def _daily_average_series_points(runs: list[MetricPoint]) -> dict[str, float]:
    """Aggregate metric points into a daily average series keyed by ISO date."""

    buckets: dict[str, list[float]] = {}
    for run in runs:
        if run.value is None:
            continue
        key = run.battle_date.date().isoformat()
        buckets.setdefault(key, []).append(run.value)

    averaged: dict[str, float] = {}
    for key, values in buckets.items():
        averaged[key] = sum(values) / len(values)
    return dict(sorted(averaged.items(), key=lambda kv: kv[0]))


def _build_comparison_result(
    form: ComparisonForm,
    *,
    base_analysis: tuple[RunAnalysis, ...],
) -> dict[str, object] | None:
    """Build a comparison result payload for template rendering."""

    if not form.is_valid():
        return None

    run_a = form.cleaned_data.get("run_a")
    run_b = form.cleaned_data.get("run_b")
    if run_a is not None and run_b is not None:
        run_a_result = analyze_runs([run_a]).runs
        run_b_result = analyze_runs([run_b]).runs
        if len(run_a_result) == 1 and len(run_b_result) == 1:
            baseline = run_a_result[0].coins_per_hour
            comparison = run_b_result[0].coins_per_hour
            computed = delta(baseline, comparison)
            return {
                "kind": "runs",
                "metric": "coins/hour",
                "label_a": run_a_result[0].battle_date.date().isoformat(),
                "label_b": run_b_result[0].battle_date.date().isoformat(),
                "baseline_value": baseline,
                "comparison_value": comparison,
                "delta": computed,
                "percent_display": computed.percent * 100 if computed.percent is not None else None,
            }

    a_start = form.cleaned_data.get("window_a_start")
    a_end = form.cleaned_data.get("window_a_end")
    b_start = form.cleaned_data.get("window_b_start")
    b_end = form.cleaned_data.get("window_b_end")
    if a_start and a_end and b_start and b_end:
        window_a = summarize_window(base_analysis, start_date=a_start, end_date=a_end)
        window_b = summarize_window(base_analysis, start_date=b_start, end_date=b_end)
        if (
            window_a.average_coins_per_hour is None
            or window_b.average_coins_per_hour is None
        ):
            return None
        baseline = window_a.average_coins_per_hour
        comparison = window_b.average_coins_per_hour
        computed = delta(baseline, comparison)
        return {
            "kind": "windows",
            "metric": "coins/hour",
            "window_a": window_a,
            "window_b": window_b,
            "baseline_value": baseline,
            "comparison_value": comparison,
            "delta": computed,
            "percent_display": computed.percent * 100 if computed.percent is not None else None,
        }

    return None


def _form_has_filters(form: ChartContextForm) -> bool:
    """Return True when the chart context form applies any filter/overlay options."""

    if not form.is_valid():
        return False
    if form.cleaned_data.get("start_date") or form.cleaned_data.get("end_date"):
        return True
    if form.cleaned_data.get("tier") or form.cleaned_data.get("preset"):
        return True
    metric = form.cleaned_data.get("metric") or "coins_per_hour"
    if metric != "coins_per_hour":
        return True
    overlay_group = form.cleaned_data.get("overlay_group") or "none"
    if overlay_group != "none":
        return True
    if form.cleaned_data.get("moving_average_window") is not None:
        return True
    if form.cleaned_data.get("ev_trials") is not None or form.cleaned_data.get("ev_seed") is not None:
        return True
    return False


def _chart_context_summary(form: ChartContextForm) -> dict[str, str | None]:
    """Build a small, template-friendly summary of the current chart context."""

    if not form.is_valid():
        return {
            "metric": "coins_per_hour",
            "start_date": None,
            "end_date": None,
            "tier": None,
            "preset": None,
            "overlay_group": "none",
            "moving_average_window": None,
            "ev_trials": None,
            "ev_seed": None,
        }

    metric = form.cleaned_data.get("metric") or "coins_per_hour"
    start_date = form.cleaned_data.get("start_date")
    end_date = form.cleaned_data.get("end_date")
    tier = form.cleaned_data.get("tier")
    preset = form.cleaned_data.get("preset")
    overlay_group = form.cleaned_data.get("overlay_group") or "none"
    moving_average_window = form.cleaned_data.get("moving_average_window")
    ev_trials = form.cleaned_data.get("ev_trials")
    ev_seed = form.cleaned_data.get("ev_seed")

    return {
        "metric": metric,
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None,
        "tier": str(tier) if tier else None,
        "preset": preset.name if preset else None,
        "overlay_group": overlay_group,
        "moving_average_window": str(moving_average_window) if moving_average_window else None,
        "ev_trials": str(ev_trials) if ev_trials else None,
        "ev_seed": str(ev_seed) if ev_seed else None,
    }


def _chart_empty_state_message(
    *,
    total_filtered_runs: int,
    chartable_runs: int,
    has_filters: bool,
) -> str | None:
    """Return a neutral empty-state message when the chart has no usable datapoints."""

    if chartable_runs > 0:
        return None

    if total_filtered_runs == 0 and not has_filters:
        return "No battle reports yet. Import one to see charts."

    if total_filtered_runs == 0:
        return "No runs match the current filters."

    return "No chartable runs in the current selection (missing required fields)."


def _hex_to_rgba(hex_color: str, *, alpha: float) -> str:
    """Convert a #RRGGBB hex color to an rgba() string with the given alpha."""

    value = hex_color.lstrip("#")
    if len(value) != 6:
        return hex_color
    r = int(value[0:2], 16)
    g = int(value[2:4], 16)
    b = int(value[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def _color_for_tier(tier: object) -> str:
    """Return a stable color for a tier number."""

    palette = [
        "#3366CC",
        "#DC3912",
        "#FF9900",
        "#109618",
        "#990099",
        "#0099C6",
        "#DD4477",
        "#66AA00",
        "#B82E2E",
        "#316395",
    ]

    if isinstance(tier, int) and tier >= 1:
        return palette[(tier - 1) % len(palette)]
    return "#777777"


def _color_for_preset(preset_name: object) -> str:
    """Return a stable color for a preset name."""

    palette = [
        "#3366CC",
        "#DC3912",
        "#FF9900",
        "#109618",
        "#990099",
        "#0099C6",
        "#DD4477",
        "#66AA00",
        "#B82E2E",
        "#316395",
    ]

    name = str(preset_name or "").strip() or "No preset"
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    index = digest[0] % len(palette)
    return palette[index]
