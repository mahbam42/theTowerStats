"""Views for Phase 1 ingestion and charting."""

from __future__ import annotations

import json

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from typing import Callable, TypedDict

from analysis.aggregations import (
    daily_average_series,
    summarize_window,
    simple_moving_average,
)
from analysis.deltas import delta
from analysis.engine import analyze_runs
from analysis.dto import RunAnalysis
from core.forms import BattleReportImportForm, ChartContextForm, ComparisonForm
from core.models import GameData
from core.services import ingest_battle_report


class ChartDataset(TypedDict, total=False):
    """A Chart.js dataset payload for the dashboard line chart."""

    label: str
    data: list[float | None]
    borderColor: str
    backgroundColor: str
    spanGaps: bool
    borderDash: list[int]


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
    analysis_result = analyze_runs(runs)
    chart_data = _build_chart_data(
        analysis_result.runs,
        overlay_group=chart_form.cleaned_data.get("overlay_group") or "none",
        moving_average_window=chart_form.cleaned_data.get("moving_average_window"),
    )

    comparison_form = ComparisonForm(request.GET, runs_queryset=runs)
    comparison_form.is_valid()
    comparison_result = _build_comparison_result(
        comparison_form,
        base_analysis=analysis_result.runs,
    )

    context = {
        "import_form": import_form,
        "chart_form": chart_form,
        "comparison_form": comparison_form,
        "comparison_result": comparison_result,
        "chart_labels_json": json.dumps(chart_data["labels"]),
        "chart_datasets_json": json.dumps(chart_data["datasets"]),
        "chart_values_json": json.dumps(chart_data["datasets"][0]["data"])
        if chart_data["datasets"]
        else "[]",
    }
    return render(request, "core/dashboard.html", context)


def _filtered_runs(filter_form: ChartContextForm) -> QuerySet[GameData]:
    """Return a filtered GameData queryset based on validated form data."""

    runs = GameData.objects.select_related(
        "run_progress",
        "run_progress__preset_tag",
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
        runs = runs.filter(run_progress__preset_tag=preset)
    return runs


def _build_chart_data(
    runs: tuple[RunAnalysis, ...],
    *,
    overlay_group: str,
    moving_average_window: int | None,
) -> ChartData:
    """Build Chart.js-friendly labels and datasets from analysis output."""

    group_key: Callable[[RunAnalysis], object]
    label_for_key: Callable[[object], str]

    if overlay_group == "tier":
        def group_key(run: RunAnalysis) -> object:
            """Group key function for tier overlays."""

            return run.tier

        def label_for_key(key: object) -> str:
            """Render dataset labels for tier overlays."""

            return f"Tier {key}" if isinstance(key, int) else "Tier (unknown)"
    elif overlay_group == "preset":
        def group_key(run: RunAnalysis) -> object:
            """Group key function for preset overlays."""

            return run.preset_name

        def label_for_key(key: object) -> str:
            """Render dataset labels for preset overlays."""

            return str(key) if isinstance(key, str) and key.strip() else "No preset"
    else:
        def group_key(_run: RunAnalysis) -> object:
            """Group key function for the single-dataset baseline chart."""

            return "all"

        def label_for_key(_key: object) -> str:
            """Render dataset labels for the single-dataset baseline chart."""

            return "Coins per hour"

    groups: dict[object, list[RunAnalysis]] = {}
    for run in runs:
        key = group_key(run)
        groups.setdefault(key, []).append(run)

    labels = sorted({run.battle_date.date().isoformat() for run in runs})
    datasets: list[ChartDataset] = []

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

    sorted_groups = sorted(groups.items(), key=lambda kv: str(kv[0]))
    for index, (key, group_runs) in enumerate(sorted_groups):
        series = daily_average_series(group_runs)
        data = [round(series[label], 2) if label in series else None for label in labels]
        color = palette[index % len(palette)]
        dataset_label = label_for_key(key)
        datasets.append(
            {
                "label": dataset_label,
                "data": data,
                "borderColor": color,
                "backgroundColor": color,
                "spanGaps": True,
            }
        )

        if moving_average_window is not None:
            ma = simple_moving_average(data, window=moving_average_window)
            datasets.append(
                {
                    "label": f"{dataset_label} (MA{moving_average_window})",
                    "data": [round(v, 2) if v is not None else None for v in ma],
                    "borderColor": color,
                    "backgroundColor": color,
                    "borderDash": [6, 4],
                    "spanGaps": True,
                }
            )

    return {"labels": labels, "datasets": datasets}


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
                "label_a": run_a_result[0].battle_date.date().isoformat(),
                "label_b": run_b_result[0].battle_date.date().isoformat(),
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
        computed = delta(window_a.average_coins_per_hour, window_b.average_coins_per_hour)
        return {
            "kind": "windows",
            "window_a": window_a,
            "window_b": window_b,
            "delta": computed,
            "percent_display": computed.percent * 100 if computed.percent is not None else None,
        }

    return None
