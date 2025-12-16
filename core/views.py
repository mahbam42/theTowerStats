"""Views for Phase 1 ingestion and Phase 3 navigation structure."""

from __future__ import annotations

import json
from datetime import date

from django.contrib import messages
from django.db.models import Case, ExpressionWrapper, F, FloatField, QuerySet, Value, When
from django.http import HttpRequest, HttpResponse, QueryDict
from django.shortcuts import redirect, render
from django.core.paginator import Paginator

from analysis.aggregations import summarize_window
from analysis.deltas import delta
from analysis.engine import analyze_runs
from analysis.dto import RunAnalysis
from analysis.series_registry import DEFAULT_REGISTRY
from core.charting.configs import (
    CHART_CONFIG_BY_ID,
    default_selected_chart_ids,
    list_selectable_chart_configs,
)
from core.charting.render import render_charts
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


def dashboard(request: HttpRequest) -> HttpResponse:
    """Render the Charts dashboard driven by ChartConfig definitions."""

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

    comparison_form = ComparisonForm(request.GET, runs_queryset=context_runs)
    comparison_form.is_valid()
    comparison_result = _build_comparison_result(
        comparison_form,
        base_analysis=base_analysis.runs,
    )

    selected_chart_ids = tuple(chart_form.cleaned_data.get("charts") or ())
    selected_configs = tuple(
        CHART_CONFIG_BY_ID[chart_id] for chart_id in selected_chart_ids if chart_id in CHART_CONFIG_BY_ID
    )
    rendered = render_charts(
        configs=selected_configs,
        records=runs,
        registry=DEFAULT_REGISTRY,
        moving_average_window=chart_form.cleaned_data.get("moving_average_window"),
        entity_selections={
            "uw": getattr(chart_form.cleaned_data.get("ultimate_weapon"), "name", None),
            "guardian": getattr(chart_form.cleaned_data.get("guardian_chip"), "name", None),
            "bot": getattr(chart_form.cleaned_data.get("bot"), "name", None),
        },
    )

    chart_panels = [
        {
            "id": entry.config.id,
            "title": entry.config.title,
            "description": entry.config.description,
            "unit": entry.unit,
        }
        for entry in rendered
    ]
    chart_panels_json = json.dumps(
        [
            {
                "id": entry.config.id,
                "labels": entry.data["labels"],
                "datasets": entry.data["datasets"],
            }
            for entry in rendered
        ]
    )

    chart_context = _chart_context_summary(chart_form, selectable_configs=list_selectable_chart_configs())
    chart_empty_state = _chart_empty_state_message(
        total_filtered_runs=total_filtered_runs,
        chartable_runs=sum(
            1
            for panel in rendered
            for dataset in panel.data["datasets"]
            for value in dataset.get("data", [])
            if value is not None
        ),
        has_filters=_form_has_filters(chart_form),
    )

    context = {
        "import_form": import_form,
        "chart_form": chart_form,
        "comparison_form": comparison_form,
        "comparison_result": comparison_result,
        "chart_panels": chart_panels,
        "chart_panels_json": chart_panels_json,
        "chart_context_json": json.dumps(chart_context),
        "chart_empty_state": chart_empty_state,
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
            "wave": "run_progress__wave",
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
    ).prefetch_related(
        "run_bots__bot_definition",
        "run_guardians__guardian_chip_definition",
        "run_combat_uws__ultimate_weapon_definition",
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
    charts = tuple(form.cleaned_data.get("charts") or ())
    if charts and set(charts) != set(default_selected_chart_ids()):
        return True
    if form.cleaned_data.get("moving_average_window") is not None:
        return True
    if form.cleaned_data.get("ev_trials") is not None or form.cleaned_data.get("ev_seed") is not None:
        return True
    return False


def _chart_context_summary(
    form: ChartContextForm, *, selectable_configs: tuple[object, ...]
) -> dict[str, str | None]:
    """Build a small, template-friendly summary of the current chart context."""

    if not form.is_valid():
        return {
            "charts": None,
            "start_date": None,
            "end_date": None,
            "tier": None,
            "preset": None,
            "moving_average_window": None,
            "ev_trials": None,
            "ev_seed": None,
        }

    selected_chart_ids = tuple(form.cleaned_data.get("charts") or ())
    titles_by_id = {getattr(cfg, "id", ""): getattr(cfg, "title", "") for cfg in selectable_configs}
    selected_titles = [titles_by_id.get(chart_id, chart_id) for chart_id in selected_chart_ids]
    selected_display = ", ".join([title for title in selected_titles if title])
    start_date = form.cleaned_data.get("start_date")
    end_date = form.cleaned_data.get("end_date")
    tier = form.cleaned_data.get("tier")
    preset = form.cleaned_data.get("preset")
    moving_average_window = form.cleaned_data.get("moving_average_window")
    ev_trials = form.cleaned_data.get("ev_trials")
    ev_seed = form.cleaned_data.get("ev_seed")

    return {
        "charts": selected_display or None,
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None,
        "tier": str(tier) if tier else None,
        "preset": preset.name if preset else None,
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
