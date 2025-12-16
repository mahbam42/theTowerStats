"""Views for Phase 1 ingestion and Phase 3 navigation structure."""

from __future__ import annotations

import hashlib
import json
from datetime import date

from django.contrib import messages
from django.db.models import Case, ExpressionWrapper, F, FloatField, QuerySet, Value, When
from django.http import HttpRequest, HttpResponse, QueryDict
from django.shortcuts import redirect, render
from django.core.paginator import Paginator

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
from core.forms import (
    BattleHistoryFilterForm,
    BattleReportImportForm,
    ChartContextForm,
    ComparisonForm,
)
from definitions.models import CardDefinition
from gamedata.models import BattleReport
from player_state.models import (
    Player,
    PlayerBot,
    PlayerCard,
    PlayerGuardianChip,
    PlayerUltimateWeapon,
    Preset,
)
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

    default_chart_data = request.GET.copy()
    if "start_date" not in default_chart_data:
        default_chart_data = default_chart_data.copy()
        default_chart_data["start_date"] = date(2025, 12, 9).isoformat()

    chart_form = ChartContextForm(default_chart_data)
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
        as_of = chart_form.cleaned_data.get("wiki_as_of")
        policy = RevisionPolicy(mode="latest") if as_of is None else RevisionPolicy(mode="as_of", as_of=as_of)
        player_context = build_player_context(revision_policy=policy)
        if policy.mode == "latest":
            revision_assumption = "Parameter revision policy: latest by WikiData.last_seen (tie-breaker: id)."
        else:
            revision_assumption = (
                f"Parameter revision policy: as_of={as_of.isoformat()} (latest row with last_seen <= as_of)."
            )

    entity_type: str | None = None
    entity_name: str | None = None
    if metric_key.startswith("uw_"):
        selection = chart_form.cleaned_data.get("ultimate_weapon")
        if selection is not None:
            entity_type = "ultimate_weapon"
            entity_name = selection.name
    elif metric_key.startswith("guardian_"):
        selection = chart_form.cleaned_data.get("guardian_chip")
        if selection is not None:
            entity_type = "guardian_chip"
            entity_name = selection.name
    elif metric_key.startswith("bot_"):
        selection = chart_form.cleaned_data.get("bot")
        if selection is not None:
            entity_type = "bot"
            entity_name = selection.name

    series_result = analyze_metric_series(
        runs,
        metric_key=metric_key,
        context=player_context,
        entity_type=entity_type,
        entity_name=entity_name,
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

    secondary_series_result = None
    secondary_chart_data: ChartData | None = None
    if series_result.metric.kind == "derived":
        secondary_series_result = analyze_metric_series(
            runs,
            metric_key="coins_per_hour",
            context=None,
            entity_type=None,
            entity_name=None,
        )
        secondary_chart_data = _build_chart_data(
            secondary_series_result.points,
            metric_def=secondary_series_result.metric,
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
        "secondary_metric_definition": secondary_series_result.metric if secondary_series_result else None,
        "secondary_chart_labels_json": json.dumps(secondary_chart_data["labels"])
        if secondary_chart_data
        else "[]",
        "secondary_chart_datasets_json": json.dumps(secondary_chart_data["datasets"])
        if secondary_chart_data
        else "[]",
        "chart_values_json": json.dumps(chart_data["datasets"][0]["data"])
        if chart_data["datasets"]
        else "[]",
    }
    return render(request, "core/dashboard.html", context)


def battle_history(request: HttpRequest) -> HttpResponse:
    """Render the Battle History dashboard with filters and pagination."""

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
            return redirect("core:battle_history")
    else:
        import_form = BattleReportImportForm()

    filter_form = BattleHistoryFilterForm(request.GET)
    filter_form.is_valid()

    sort_key = filter_form.cleaned_data.get("sort") or "-run_progress__battle_date"
    runs = BattleReport.objects.select_related("run_progress", "run_progress__preset")
    if sort_key.lstrip("-") == "coins_per_hour":
        coins_per_hour_expr = Case(
            When(
                run_progress__coins_earned__isnull=False,
                run_progress__real_time_seconds__gt=0,
                then=ExpressionWrapper(
                    F("run_progress__coins_earned") * Value(3600.0) / F("run_progress__real_time_seconds"),
                    output_field=FloatField(),
                ),
            ),
            default=Value(None),
            output_field=FloatField(),
        )
        runs = runs.annotate(coins_per_hour=coins_per_hour_expr)

    ordering = [sort_key]
    if sort_key.lstrip("-") != "parsed_at":
        ordering.append("-parsed_at")
    runs = runs.order_by(*ordering)

    tier = filter_form.cleaned_data.get("tier") if filter_form.is_valid() else None
    if tier:
        runs = runs.filter(run_progress__tier=tier)

    killed_by = filter_form.cleaned_data.get("killed_by") if filter_form.is_valid() else None
    if killed_by:
        runs = runs.filter(run_progress__killed_by__icontains=killed_by)

    goal = filter_form.cleaned_data.get("goal") if filter_form.is_valid() else None
    if goal:
        runs = runs.filter(run_progress__preset__name__icontains=goal)

    paginator = Paginator(runs, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    analyzed_runs = analyze_runs(page_obj.object_list).runs
    run_metrics = {entry.run_id: entry for entry in analyzed_runs}
    page_rows = [
        (run, run_metrics.get(getattr(getattr(run, "run_progress", None), "id", None) or run.id))
        for run in page_obj.object_list
    ]

    sort_querystrings = _build_sort_querystrings(
        request.GET,
        current_sort=sort_key,
        sortable_keys={
            "battle_date": "run_progress__battle_date",
            "tier": "run_progress__tier",
            "killed_by": "run_progress__killed_by",
            "coins_earned": "run_progress__coins_earned",
            "coins_per_hour": "coins_per_hour",
            "cash_earned": "run_progress__cash_earned",
            "interest_earned": "run_progress__interest_earned",
            "gem_blocks": "run_progress__gem_blocks_tapped",
            "cells_earned": "run_progress__cells_earned",
            "reroll_shards": "run_progress__reroll_shards_earned",
            "preset": "run_progress__preset__name",
            "imported": "parsed_at",
        },
    )

    querystring = request.GET.copy()
    if "page" in querystring:
        querystring.pop("page")
    base_querystring = querystring.urlencode()

    return render(
        request,
        "core/battle_history.html",
        {
            "import_form": import_form,
            "filter_form": filter_form,
            "page_obj": page_obj,
            "page_rows": page_rows,
            "base_querystring": base_querystring,
            "sort_querystrings": sort_querystrings,
            "current_sort": sort_key,
        },
    )


def _build_sort_querystrings(
    query_params: QueryDict, *, current_sort: str, sortable_keys: dict[str, str]
) -> dict[str, str]:
    """Build encoded querystrings for clickable column sorting.

    Args:
        query_params: A QueryDict-like object (e.g. request.GET).
        current_sort: Current validated sort key.
        sortable_keys: Mapping of template keys to base sort expressions.

    Returns:
        A mapping of template keys to urlencoded querystrings (without leading `?`).
    """

    base = query_params.copy()
    if "page" in base:
        base.pop("page")

    def _toggle(sort_expr: str) -> str:
        asc = sort_expr.lstrip("-")
        desc = f"-{asc}"
        if current_sort == desc:
            return asc
        return desc

    querystrings: dict[str, str] = {}
    for template_key, sort_expr in sortable_keys.items():
        params = base.copy()
        params["sort"] = _toggle(sort_expr)
        querystrings[template_key] = params.urlencode()
    return querystrings


def cards(request: HttpRequest) -> HttpResponse:
    """Render the cards page (definitions + player progress + preset labels)."""

    definitions = CardDefinition.objects.order_by("name")
    player, _ = Player.objects.get_or_create(name="default")
    player_cards = PlayerCard.objects.filter(player=player).select_related("card_definition").order_by(
        "card_slug"
    )
    presets = Preset.objects.filter(player=player).order_by("name")
    card_slots = {
        "unlocked": player_cards.count(),
        "next_cost": None,
    }
    return render(
        request,
        "core/cards.html",
        {
            "definitions": definitions,
            "player_cards": player_cards,
            "presets": presets,
            "card_slots": card_slots,
        },
    )


def ultimate_weapon_progress(request: HttpRequest) -> HttpResponse:
    """Render the Ultimate Weapon progress page."""
    player, _ = Player.objects.get_or_create(name="default")
    ultimate_weapons = (
        PlayerUltimateWeapon.objects.filter(player=player)
        .select_related("ultimate_weapon_definition")
        .prefetch_related("parameters__parameter_definition")
        .order_by("ultimate_weapon_slug")
    )
    progress = [
        {
            "name": uw.ultimate_weapon_definition.name if uw.ultimate_weapon_definition else uw.ultimate_weapon_slug,
            "unlocked": uw.unlocked,
            "parameters": _parameter_rows(uw.parameters.all()),
        }
        for uw in ultimate_weapons
    ]

    return render(request, "core/ultimate_weapon_progress.html", {"ultimate_weapons": progress})


def guardian_progress(request: HttpRequest) -> HttpResponse:
    """Render the Guardian progress page."""
    player, _ = Player.objects.get_or_create(name="default")
    guardians = (
        PlayerGuardianChip.objects.filter(player=player)
        .select_related("guardian_chip_definition")
        .prefetch_related("parameters__parameter_definition")
        .order_by("guardian_chip_slug")
    )
    progress = [
        {
            "name": chip.guardian_chip_definition.name if chip.guardian_chip_definition else chip.guardian_chip_slug,
            "unlocked": chip.unlocked,
            "parameters": _parameter_rows(chip.parameters.all()),
        }
        for chip in guardians
    ]
    return render(request, "core/guardian_progress.html", {"guardians": progress})


def bots_progress(request: HttpRequest) -> HttpResponse:
    """Render the Bots progress page."""

    player, _ = Player.objects.get_or_create(name="default")
    bots = (
        PlayerBot.objects.filter(player=player)
        .select_related("bot_definition")
        .prefetch_related("parameters__parameter_definition")
        .order_by("bot_slug")
    )
    progress = [
        {
            "name": bot.bot_definition.name if bot.bot_definition else bot.bot_slug,
            "unlocked": bot.unlocked,
            "parameters": _parameter_rows(bot.parameters.all()),
        }
        for bot in bots
    ]
    return render(request, "core/bots_progress.html", {"bots": progress})


def _parameter_rows(parameters: QuerySet) -> list[dict[str, object | None]]:
    """Return display-ready parameter summaries for progress widgets."""

    rows: list[dict[str, object | None]] = []
    for param in parameters:
        definition = getattr(param, "parameter_definition", None)
        value = None
        unit = None
        if definition is not None:
            level_row = definition.levels.filter(level=param.level).first()
            if level_row is None:
                level_row = definition.levels.order_by("level").last()
            value = getattr(level_row, "value_raw", None)
            unit = definition.get_unit_kind_display()
        rows.append(
            {
                "name": getattr(definition, "display_name", "Unknown"),
                "level": getattr(param, "level", 0),
                "value": value,
                "unit": unit,
            }
        )
    return rows


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
