"""Views for Phase 1 ingestion and charting."""

from __future__ import annotations

import json

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from analysis.engine import analyze_runs
from analysis.dto import RunAnalysis
from core.forms import BattleReportImportForm, DateRangeFilterForm
from core.models import RunProgress
from core.services import ingest_battle_report


def dashboard(request: HttpRequest) -> HttpResponse:
    """Render the Phase 1 dashboard (import form + single time-series chart)."""

    if request.method == "POST":
        import_form = BattleReportImportForm(request.POST)
        if import_form.is_valid():
            raw_text = import_form.cleaned_data["raw_text"]
            _, created = ingest_battle_report(raw_text)
            if created:
                messages.success(request, "Battle Report imported.")
            else:
                messages.warning(request, "Duplicate Battle Report ignored.")
            return redirect("core:dashboard")
    else:
        import_form = BattleReportImportForm()

    filter_form = DateRangeFilterForm(request.GET)
    filter_form.is_valid()

    runs = _filtered_runs(filter_form)
    analysis_result = analyze_runs(runs)
    chart_points = _chart_points(analysis_result.runs)

    context = {
        "import_form": import_form,
        "filter_form": filter_form,
        "chart_labels_json": json.dumps([p["x"] for p in chart_points]),
        "chart_values_json": json.dumps([p["y"] for p in chart_points]),
    }
    return render(request, "core/dashboard.html", context)


def _filtered_runs(filter_form: DateRangeFilterForm) -> QuerySet[RunProgress]:
    """Return a filtered RunProgress queryset based on validated form data."""

    runs = RunProgress.objects.select_related("game_data").order_by("battle_date")
    if not filter_form.is_valid():
        return runs

    start_date = filter_form.cleaned_data.get("start_date")
    end_date = filter_form.cleaned_data.get("end_date")
    if start_date:
        runs = runs.filter(battle_date__date__gte=start_date)
    if end_date:
        runs = runs.filter(battle_date__date__lte=end_date)
    return runs


def _chart_points(runs: tuple[RunAnalysis, ...]) -> list[dict[str, object]]:
    """Convert analysis results into a Chart.js-friendly point list."""

    points: list[dict[str, object]] = []
    for run in runs:
        points.append(
            {
                "x": run.battle_date.date().isoformat(),
                "y": round(run.waves_per_hour, 2),
            }
        )
    return points
