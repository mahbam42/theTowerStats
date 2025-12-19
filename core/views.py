"""Views for Phase 1 ingestion and Phase 3 navigation structure."""

from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Case, ExpressionWrapper, F, FloatField, Max, QuerySet, Value, When
from django.http import HttpRequest, HttpResponse, JsonResponse, QueryDict
from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.urls import reverse

from analysis.aggregations import summarize_window
from analysis.chart_config_dto import ChartContextDTO
from analysis.chart_config_engine import analyze_chart_config_dto
from analysis.chart_config_validator import validate_chart_config_dto
from analysis.deltas import delta
from analysis.engine import analyze_runs
from analysis.dto import RunAnalysis
from analysis.series_registry import DEFAULT_REGISTRY
from core.advice import AdviceItem, SnapshotDeltaInput, generate_optimization_advice, generate_snapshot_delta_advice
from core.charting.configs import (
    CHART_CONFIG_BY_ID,
    default_selected_chart_ids,
    list_selectable_chart_configs,
)
from core.charting.dto_builder import build_chart_config_dto
from core.charting.flagging import flag_reasons, incomplete_run_labels
from core.charting.render import render_charts
from core.charting.snapshot_codec import decode_chart_config_dto, encode_chart_config_dto
from core.forms import (
    BattleHistoryFilterForm,
    BattleHistoryPresetUpdateForm,
    BattleReportImportForm,
    CardInventoryUpdateForm,
    CardPresetUpdateForm,
    ChartBuilderForm,
    ChartContextForm,
    CardsFilterForm,
    ComparisonForm,
    UpgradeableEntityProgressFilterForm,
    UltimateWeaponProgressFilterForm,
)
from core.upgradeables import (
    ParameterLevelRow,
    build_upgradeable_parameter_view,
    build_uw_parameter_view,
    total_currency_invested_for_parameter,
    total_stones_invested_for_parameter,
    validate_parameter_definitions,
    validate_uw_parameter_definitions,
)
from definitions.models import (
    BotDefinition,
    CardDefinition,
    GuardianChipDefinition,
    PatchBoundary,
    UltimateWeaponDefinition,
)
from gamedata.models import BattleReport, BattleReportProgress
from player_state.card_slots import card_slot_max_slots, next_card_slot_unlock_cost_raw
from player_state.cards import apply_inventory_rollover, derive_card_progress
from player_state.economy import enforce_and_deduct_gems_if_tracked
from player_state.models import (
    ChartSnapshot,
    MAX_ACTIVE_GUARDIAN_CHIPS,
    Player,
    PlayerBot,
    PlayerBotParameter,
    PlayerCard,
    PlayerGuardianChip,
    PlayerGuardianChipParameter,
    PlayerUltimateWeapon,
    PlayerUltimateWeaponParameter,
    Preset,
)
from core.services import ingest_battle_report
from core.uw_sync import build_uw_sync_payload


def _request_player(request: HttpRequest) -> Player:
    """Return the Player associated with the authenticated user."""

    player, _ = Player.objects.get_or_create(
        user=request.user,
        defaults={"display_name": getattr(request.user, "username", "Player")},
    )
    return player


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Render the Charts dashboard driven by ChartConfig definitions."""

    player = _request_player(request)

    effective_get: QueryDict | dict[str, object] = request.GET
    snapshot_id = request.GET.get("snapshot_id")
    if snapshot_id:
        snapshot = ChartSnapshot.objects.filter(player=player, id=int(snapshot_id)).first()
        if snapshot is not None:
            merged = request.GET.copy()
            stored = dict(snapshot.config or {})
            if stored:
                config_dto = decode_chart_config_dto(stored)
                merged["builder"] = "1"
                merged.setlist("metric_keys", list(config_dto.metrics))
                merged["chart_type"] = config_dto.chart_type
                merged["group_by"] = config_dto.group_by
                merged["comparison"] = config_dto.comparison
                merged["smoothing"] = config_dto.smoothing
                if config_dto.scopes is not None:
                    merged["run_a"] = str(config_dto.scopes[0].run_id or "")
                    merged["run_b"] = str(config_dto.scopes[1].run_id or "")
                    merged["window_a_start"] = (config_dto.scopes[0].start_date.isoformat() if config_dto.scopes[0].start_date else "")
                    merged["window_a_end"] = (config_dto.scopes[0].end_date.isoformat() if config_dto.scopes[0].end_date else "")
                    merged["window_b_start"] = (config_dto.scopes[1].start_date.isoformat() if config_dto.scopes[1].start_date else "")
                    merged["window_b_end"] = (config_dto.scopes[1].end_date.isoformat() if config_dto.scopes[1].end_date else "")
                merged["start_date"] = config_dto.context.start_date.isoformat() if config_dto.context.start_date else ""
                merged["end_date"] = config_dto.context.end_date.isoformat() if config_dto.context.end_date else ""
                merged["tier"] = str(config_dto.context.tier or "")
                merged["preset"] = str(config_dto.context.preset_id or "")
            else:
                builder_payload = dict(snapshot.chart_builder or {})
                context_payload = dict(snapshot.chart_context or {})
                merged["builder"] = "1"
                for key, value in builder_payload.items():
                    if key == "metric_keys" and isinstance(value, list):
                        merged.setlist("metric_keys", [str(v) for v in value])
                    else:
                        merged[key] = str(value) if value is not None else ""
                for key, value in context_payload.items():
                    merged[key] = str(value) if value is not None else ""

            effective_get = merged
    if request.method == "POST":
        action = (request.POST.get("action") or "").strip()
        if action == "create_chart_snapshot":
            name = (request.POST.get("snapshot_name") or "").strip()
            if not name:
                messages.error(request, "Snapshot name is required.")
                return redirect("core:dashboard")
            target = (request.POST.get("snapshot_target") or "charts").strip() or "charts"

            chart_form = ChartContextForm(effective_get, player=player)  # type: ignore[arg-type]
            chart_form.is_valid()
            context_runs = _context_filtered_runs(chart_form, player=player)
            builder_form = ChartBuilderForm(request.POST, runs_queryset=context_runs)
            if not builder_form.is_valid():
                messages.error(request, "Could not save snapshot: invalid Chart Builder inputs.")
                return redirect("core:dashboard")

            config_dto = build_chart_config_dto(context_form=chart_form, builder_form=builder_form)
            validation = validate_chart_config_dto(config_dto, registry=DEFAULT_REGISTRY)
            if not validation.is_valid:
                messages.error(request, "Could not save snapshot: ChartConfigDTO validation failed.")
                return redirect("core:dashboard")

            try:
                ChartSnapshot.objects.create(
                    player=player,
                    name=name,
                    target=target,
                    config=encode_chart_config_dto(config_dto),
                )
            except Exception as exc:
                if settings.DEBUG:
                    raise
                messages.error(request, f"Could not save snapshot: {exc}")
                return redirect("core:dashboard")

            messages.success(request, "Snapshot saved.")
            return redirect("core:dashboard")

        import_form = BattleReportImportForm(request.POST)
        if import_form.is_valid():
            raw_text = import_form.cleaned_data["raw_text"]
            preset_name = import_form.cleaned_data.get("preset_name") or None
            _, created = ingest_battle_report(raw_text, player=player, preset_name=preset_name)
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

    chart_form = ChartContextForm(effective_get or default_chart_data, player=player)  # type: ignore[arg-type]
    chart_form.is_valid()

    runs = _filtered_runs(chart_form, player=player)
    total_filtered_runs = runs.count()
    context_runs = _context_filtered_runs(chart_form, player=player)
    base_analysis = analyze_runs(context_runs)

    comparison_form = ComparisonForm(effective_get, runs_queryset=context_runs)  # type: ignore[arg-type]
    comparison_form.is_valid()
    comparison_result = _build_comparison_result(
        comparison_form,
        base_analysis=base_analysis.runs,
    )
    advice_items = generate_optimization_advice(comparison_result)

    advice_snapshot_a = getattr(effective_get, "get", lambda _k: None)("advice_snapshot_a")
    advice_snapshot_b = getattr(effective_get, "get", lambda _k: None)("advice_snapshot_b")
    advice_mode = getattr(effective_get, "get", lambda _k: None)("advice_mode") or "snapshot_vs_current"
    snapshot_advice_items: tuple[AdviceItem, ...] = ()
    if advice_snapshot_a:
        snapshot_advice_items = _build_snapshot_delta_advice(
            player=player,
            runs_current=runs,
            snapshot_a_id=str(advice_snapshot_a),
            snapshot_b_id=(str(advice_snapshot_b) if advice_snapshot_b else None),
            mode=str(advice_mode),
        )
    advice_items = tuple(advice_items) + tuple(snapshot_advice_items)

    builder_data = effective_get if getattr(effective_get, "get", lambda _k: None)("builder") == "1" else None
    chart_builder_form = ChartBuilderForm(builder_data, runs_queryset=context_runs)
    builder_errors: tuple[str, ...] = ()
    builder_panel: dict[str, Any] | None = None
    if chart_builder_form.is_bound:
        if chart_builder_form.is_valid():
            config_dto = build_chart_config_dto(context_form=chart_form, builder_form=chart_builder_form)
            validation = validate_chart_config_dto(config_dto, registry=DEFAULT_REGISTRY)
            if validation.is_valid:
                analyzed = analyze_chart_config_dto(
                    runs,
                    config=config_dto,
                    registry=DEFAULT_REGISTRY,
                    moving_average_window=chart_form.cleaned_data.get("moving_average_window"),
                    entity_selections={},
                )
                palette = [
                    "#3366CC",
                    "#DC3912",
                    "#FF9900",
                    "#109618",
                    "#990099",
                    "#0099C6",
                    "#DD4477",
                    "#66AA00",
                ]
                patch_boundaries = tuple(PatchBoundary.objects.values_list("boundary_date", flat=True))
                incomplete_labels = incomplete_run_labels(runs)
                datasets: list[dict[str, Any]] = []
                if analyzed.chart_type == "donut":
                    slice_colors = [palette[idx % len(palette)] for idx in range(len(analyzed.labels))]
                    unit = analyzed.datasets[0].unit if analyzed.datasets else ""
                    datasets = [
                        {
                            "label": "Chart Builder",
                            "metricKey": "chart_builder_custom",
                            "metricKind": "observed",
                            "unit": unit,
                            "seriesKind": "donut",
                            "data": analyzed.datasets[0].values if analyzed.datasets else [],
                            "borderColor": "#ffffff",
                            "backgroundColor": slice_colors,
                        }
                    ]
                    builder_panel = {
                        "id": "chart_builder_custom",
                        "title": "Chart Builder",
                        "description": "Runtime chart (not persisted).",
                        "unit": unit,
                        "chart_type": "donut",
                        "labels": analyzed.labels,
                        "datasets": datasets,
                    }
                else:
                    for idx, ds in enumerate(analyzed.datasets):
                        color = palette[idx % len(palette)]
                        reasons = flag_reasons(
                            analyzed.labels,
                            values=ds.values,
                            incomplete_labels=incomplete_labels,
                            patch_boundaries=patch_boundaries,
                        )
                        dataset = {
                            "label": ds.label,
                            "metricKey": ds.metric_key,
                            "metricKind": "observed",
                            "unit": ds.unit,
                            "seriesKind": "raw",
                            "data": ds.values,
                            "borderColor": color,
                            "backgroundColor": color,
                            "spanGaps": False,
                            "borderWidth": 2,
                            "pointRadius": [6 if r else 2 for r in reasons],
                            "pointHoverRadius": [8 if r else 5 for r in reasons],
                            "pointBackgroundColor": ["#DC3912" if r else color for r in reasons],
                            "tension": 0.15,
                            "flagReasons": reasons,
                        }
                        datasets.append(dataset)
                    unit = analyzed.datasets[0].unit if analyzed.datasets else ""
                    builder_panel = {
                        "id": "chart_builder_custom",
                        "title": "Chart Builder",
                        "description": "Runtime chart (not persisted).",
                        "unit": unit,
                        "chart_type": analyzed.chart_type,
                        "labels": analyzed.labels,
                        "datasets": datasets,
                    }
            else:
                builder_errors = validation.errors
        else:
            builder_errors = tuple(
                f"{field}: {', '.join(errors)}" for field, errors in chart_builder_form.errors.items()
            )

    selected_chart_ids = tuple(chart_form.cleaned_data.get("charts") or ())
    selected_configs = tuple(
        CHART_CONFIG_BY_ID[chart_id] for chart_id in selected_chart_ids if chart_id in CHART_CONFIG_BY_ID
    )
    configs_to_render = selected_configs
    rendered = render_charts(
        configs=configs_to_render,
        records=runs,
        registry=DEFAULT_REGISTRY,
        moving_average_window=chart_form.cleaned_data.get("moving_average_window"),
        entity_selections={
            "uw": getattr(chart_form.cleaned_data.get("ultimate_weapon"), "name", None),
            "guardian": getattr(chart_form.cleaned_data.get("guardian_chip"), "name", None),
            "bot": getattr(chart_form.cleaned_data.get("bot"), "name", None),
        },
        patch_boundaries=tuple(PatchBoundary.objects.values_list("boundary_date", flat=True)),
    )

    chart_panels: list[dict[str, Any]] = [
        {
            "id": entry.config.id,
            "title": entry.config.title,
            "description": entry.config.description,
            "unit": entry.unit,
            "chart_type": entry.config.chart_type,
            "error": entry.error,
            "warnings": entry.warnings,
        }
        for entry in rendered
    ]
    chart_panels_json = json.dumps(
        [
            {
                "id": entry.config.id,
                "chart_type": entry.config.chart_type,
                "labels": entry.data["labels"],
                "datasets": entry.data["datasets"],
            }
            for entry in rendered
        ]
    )
    if builder_panel is not None:
        chart_panels.insert(
            0,
            {
                "id": builder_panel["id"],
                "title": builder_panel["title"],
                "description": builder_panel["description"],
                "unit": builder_panel["unit"],
                "chart_type": builder_panel["chart_type"],
                "error": None,
                "warnings": (),
            },
        )
        builder_json = json.dumps(
            {
                "id": builder_panel["id"],
                "chart_type": builder_panel["chart_type"],
                "labels": builder_panel["labels"],
                "datasets": builder_panel["datasets"],
            }
        )
        combined = [json.loads(builder_json)] + json.loads(chart_panels_json)
        chart_panels_json = json.dumps(combined)

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
        "advice_items": advice_items,
        "advice_snapshot_a": advice_snapshot_a,
        "advice_snapshot_b": advice_snapshot_b,
        "advice_mode": advice_mode,
        "chart_builder_form": chart_builder_form,
        "chart_builder_errors": builder_errors,
        "chart_snapshots": ChartSnapshot.objects.filter(player=player, target="charts").order_by("-created_at"),
        "chart_builder_metric_meta_json": json.dumps(
            {
                spec.key: {
                    "unit": spec.unit,
                    "category": str(spec.category),
                    "supports_rolling_avg": ("moving_average" in spec.allowed_transforms),
                }
                for spec in DEFAULT_REGISTRY.list()
            }
        ),
        "chart_panels": chart_panels,
        "chart_panels_json": chart_panels_json,
        "chart_context_json": json.dumps(chart_context),
        "chart_empty_state": chart_empty_state,
    }
    return render(request, "core/dashboard.html", context)

def _build_snapshot_delta_advice(
    *,
    player: Player,
    runs_current: QuerySet[BattleReport],
    snapshot_a_id: str,
    snapshot_b_id: str | None,
    mode: str,
) -> tuple[AdviceItem, ...]:
    """Build snapshot-based advice items for the dashboard.

    Args:
        player: Active Player owning the snapshots.
        runs_current: QuerySet already filtered by the current dashboard filters.
        snapshot_a_id: Snapshot id used as the baseline scope.
        snapshot_b_id: Optional snapshot id used as the comparison scope.
        mode: Either "snapshot_vs_current" or "snapshot_vs_snapshot".

    Returns:
        A tuple of AdviceItem values (0–1 for Phase 7).
    """

    try:
        snapshot_a = ChartSnapshot.objects.filter(player=player, id=int(snapshot_a_id)).first()
    except (TypeError, ValueError):
        snapshot_a = None
    if snapshot_a is None or not snapshot_a.config:
        return ()

    dto_a = decode_chart_config_dto(dict(snapshot_a.config))
    validation_a = validate_chart_config_dto(dto_a, registry=DEFAULT_REGISTRY)
    if not validation_a.is_valid:
        return ()

    baseline_runs = _runs_for_chart_context_dto(player=player, context=dto_a.context)
    baseline_count, baseline_value = _coins_per_hour_sample(baseline_runs)

    comparison_label = "Current filters"
    comparison_count = 0
    comparison_value: float | None = None
    if mode == "snapshot_vs_snapshot":
        if snapshot_b_id is None:
            return ()
        try:
            snapshot_b = ChartSnapshot.objects.filter(player=player, id=int(snapshot_b_id)).first()
        except (TypeError, ValueError):
            snapshot_b = None
        if snapshot_b is None or not snapshot_b.config:
            return ()
        dto_b = decode_chart_config_dto(dict(snapshot_b.config))
        validation_b = validate_chart_config_dto(dto_b, registry=DEFAULT_REGISTRY)
        if not validation_b.is_valid:
            return ()
        comparison_label = snapshot_b.name
        comparison_runs = _runs_for_chart_context_dto(player=player, context=dto_b.context)
        comparison_count, comparison_value = _coins_per_hour_sample(comparison_runs)
    else:
        comparison_count, comparison_value = _coins_per_hour_sample(runs_current)

    return generate_snapshot_delta_advice(
        SnapshotDeltaInput(
            metric_key="coins_per_hour",
            baseline_label=snapshot_a.name,
            baseline_runs=baseline_count,
            baseline_value=baseline_value,
            comparison_label=comparison_label,
            comparison_runs=comparison_count,
            comparison_value=comparison_value,
        )
    )


def _runs_for_chart_context_dto(*, player: Player, context: ChartContextDTO) -> QuerySet[BattleReport]:
    """Build a BattleReport queryset filtered by a ChartContextDTO.

    Args:
        player: Active Player owning the runs.
        context: ChartContextDTO containing the filter values.

    Returns:
        QuerySet of BattleReport rows matching the context.
    """

    runs = (
        BattleReport.objects.filter(player=player)
        .select_related("run_progress", "run_progress__preset")
        .order_by("run_progress__battle_date")
    )
    if context.start_date:
        runs = runs.filter(run_progress__battle_date__date__gte=context.start_date)
    if context.end_date:
        runs = runs.filter(run_progress__battle_date__date__lte=context.end_date)
    if context.tier:
        runs = runs.filter(run_progress__tier=context.tier)
    if context.preset_id:
        runs = runs.filter(run_progress__preset_id=context.preset_id)
    return runs


def _coins_per_hour_sample(runs: QuerySet[BattleReport]) -> tuple[int, float | None]:
    """Return run count and average coins/hour for a filtered queryset.

    Args:
        runs: Filtered BattleReport queryset.

    Returns:
        Tuple of (count, average_coins_per_hour), where count includes only runs
        that have a non-null coins/hour value.
    """

    analyzed = analyze_runs(runs).runs
    values = [run.coins_per_hour for run in analyzed if run.coins_per_hour is not None]
    if not values:
        return 0, None
    return len(values), sum(values) / len(values)

@login_required
def battle_history(request: HttpRequest) -> HttpResponse:
    """Render the Battle History dashboard with filters and pagination."""

    player = _request_player(request)

    if request.method == "POST":
        action = (request.POST.get("action") or "").strip()
        if action == "update_run_preset":
            update_form = BattleHistoryPresetUpdateForm(request.POST, player=player)
            if not update_form.is_valid():
                messages.error(request, "Could not update preset for that run.")
                return redirect("core:battle_history")

            progress_id = update_form.cleaned_data["progress_id"]
            if not BattleReportProgress.objects.filter(player=player, id=progress_id).exists():
                messages.error(request, "Run row not found.")
                return redirect("core:battle_history")

            preset = update_form.cleaned_data.get("preset")
            if preset is None:
                updated = BattleReportProgress.objects.filter(player=player, id=progress_id).update(
                    preset=None,
                    preset_name_snapshot="",
                    preset_color_snapshot="",
                )
            else:
                updated = BattleReportProgress.objects.filter(player=player, id=progress_id).update(
                    preset=preset,
                    preset_name_snapshot=preset.name,
                    preset_color_snapshot=preset.badge_color(),
                )

            if updated:
                messages.success(request, "Saved preset for run.")
            else:
                messages.error(request, "Could not update preset for that run.")

            redirect_to = update_form.cleaned_data.get("next") or reverse("core:battle_history")
            return redirect(redirect_to)

        import_form = BattleReportImportForm(request.POST)
        if import_form.is_valid():
            raw_text = import_form.cleaned_data["raw_text"]
            preset_name = import_form.cleaned_data.get("preset_name") or None
            _, created = ingest_battle_report(raw_text, player=player, preset_name=preset_name)
            if created:
                messages.success(request, "Battle Report imported.")
            else:
                messages.warning(request, "Duplicate Battle Report ignored.")
            return redirect("core:battle_history")
    else:
        import_form = BattleReportImportForm()

    filter_form = BattleHistoryFilterForm(request.GET, player=player)
    filter_form.is_valid()

    sort_key = filter_form.cleaned_data.get("sort") or "-run_progress__battle_date"
    runs = BattleReport.objects.filter(player=player).select_related("run_progress", "run_progress__preset")
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

    preset = filter_form.cleaned_data.get("preset") if filter_form.is_valid() else None
    if preset:
        runs = runs.filter(run_progress__preset=preset)

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
            "player_presets": Preset.objects.filter(player=player).order_by("name"),
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


def _build_sort_querystrings_default_asc(
    query_params: QueryDict, *, current_sort: str, sortable_keys: dict[str, str]
) -> dict[str, str]:
    """Build encoded querystrings for clickable column sorting (default asc).

    The Battle History default sort behavior is "first click sorts descending"
    (useful for newest-first timestamps). The Cards dashboard is primarily a
    catalog view, so it defaults to ascending on the first click.

    Args:
        query_params: A QueryDict-like object (e.g. request.GET).
        current_sort: Current validated sort key.
        sortable_keys: Mapping of template keys to base sort expressions.

    Returns:
        A mapping of template keys to urlencoded querystrings (without leading `?`).
    """

    base = query_params.copy()

    def _toggle(sort_expr: str) -> str:
        asc = sort_expr.lstrip("-")
        desc = f"-{asc}"
        if current_sort == asc:
            return desc
        return asc

    querystrings: dict[str, str] = {}
    for template_key, sort_expr in sortable_keys.items():
        params = base.copy()
        params["sort"] = _toggle(sort_expr)
        querystrings[template_key] = params.urlencode()
    return querystrings


def _render_card_parameters_text(*, description: str, effect_raw: str, level: int) -> str:
    """Render a readable parameter string that includes the current effective value.

    Args:
        description: Wiki-derived description text for the card.
        effect_raw: Wiki-derived effect value text for the card.
        level: Current displayed card level (0 when unowned).

    Returns:
        A multi-line string suitable for `white-space: pre-line` rendering.
    """

    cleaned_description = (description or "").strip()
    cleaned_effect = (effect_raw or "").strip()
    if not cleaned_description and not cleaned_effect:
        return ""

    effect_with_level = cleaned_effect
    if cleaned_effect and level > 0:
        effect_with_level = f"{cleaned_effect} (Level {level})"

    if cleaned_description and "#" in cleaned_description and effect_with_level:
        # Prefer replacing placeholders when present (common in wiki text like "x #").
        return cleaned_description.replace("#", effect_with_level)

    if cleaned_description and effect_with_level:
        return f"{cleaned_description}\n{effect_with_level}"

    return cleaned_description or effect_with_level


def _sort_card_rows(rows: list[dict[str, object]], *, sort_key: str) -> list[dict[str, object]]:
    """Sort Cards dashboard rows using the validated sort key.

    Args:
        rows: Cards dashboard row dictionaries.
        sort_key: A validated sort key (with optional leading '-' for desc).

    Returns:
        A new list of rows in the requested order.
    """

    normalized = (sort_key or "name").strip()
    descending = normalized.startswith("-")
    base_key = normalized.lstrip("-")

    def _as_str(value: object) -> str:
        return str(value or "").casefold()

    def _as_int(value: object) -> int:
        try:
            return int(str(value).strip() or "0")
        except (TypeError, ValueError):
            return 0

    rarity_order = {
        "common": 1,
        "rare": 2,
        "epic": 3,
        "legendary": 4,
        "mythic": 5,
    }

    def key_fn(r: dict[str, object]) -> Any:
        if base_key == "name":
            return _as_str(r.get("name"))
        if base_key == "rarity":
            return (rarity_order.get(_as_str(r.get("rarity")), 999), _as_str(r.get("name")))
        if base_key == "level":
            return (_as_int(r.get("level")), _as_str(r.get("name")))
        if base_key == "progress":
            inventory = _as_int(r.get("inventory_count"))
            threshold = _as_int(r.get("inventory_threshold"))
            ratio = float(inventory) / float(threshold) if threshold > 0 else 0.0
            return (ratio, _as_str(r.get("name")))
        if base_key == "maxed":
            return (bool(r.get("is_maxed")), _as_str(r.get("name")))
        return _as_str(r.get("name"))

    return sorted(rows, key=key_fn, reverse=descending)


def _preset_filter_querystring(query_params: QueryDict, *, preset_id: int) -> str:
    """Build a querystring that sets the preset filter to a single preset.

    Args:
        query_params: A QueryDict-like object (e.g. request.GET).
        preset_id: The preset id to select.

    Returns:
        A urlencoded querystring (without leading `?`).
    """

    params = query_params.copy()
    params.setlist("presets", [str(preset_id)])
    return params.urlencode()


@login_required
def cards(request: HttpRequest) -> HttpResponse:
    """Render the Cards dashboard (slots + inventory + preset tagging)."""

    player = _request_player(request)
    definitions = list(CardDefinition.objects.order_by("name"))

    for definition in definitions:
        PlayerCard.objects.get_or_create(
            player=player,
            card_slug=definition.slug,
            defaults={
                "card_definition": definition,
                "stars_unlocked": 0,
                "inventory_count": 0,
            },
        )

    if request.method == "POST":
        action = (request.POST.get("action") or "").strip()
        redirect_to = request.POST.get("next") or request.path

        if action == "unlock_slot":
            max_slots = card_slot_max_slots()
            next_cost = next_card_slot_unlock_cost_raw(unlocked=player.card_slots_unlocked)
            if max_slots is None:
                messages.warning(request, "Card slot limits are not available yet.")
                return redirect(redirect_to)
            if player.card_slots_unlocked < max_slots:
                with transaction.atomic():
                    can_afford, parsed_cost = enforce_and_deduct_gems_if_tracked(
                        player=player,
                        cost_raw=next_cost,
                    )
                    if can_afford is False:
                        messages.error(
                            request,
                            f"Not enough gems to unlock the next slot (cost: {parsed_cost}).",
                        )
                        return redirect(redirect_to)
                    player.card_slots_unlocked += 1
                    player.save(update_fields=["card_slots_unlocked"])
                if next_cost:
                    messages.success(request, f"Unlocked the next card slot (cost: {next_cost}).")
                else:
                    messages.success(request, "Unlocked the next card slot.")
            else:
                messages.warning(request, "No additional card slots are available.")
            return redirect(redirect_to)

        if action == "update_inventory":
            form = CardInventoryUpdateForm(request.POST)
            if not form.is_valid():
                messages.error(request, "Could not save card inventory.")
                return redirect(redirect_to)

            card = PlayerCard.objects.filter(player=player, id=form.cleaned_data["card_id"]).first()
            if card is None:
                messages.error(request, "Card row not found.")
                return redirect(redirect_to)

            inventory_input = int(form.cleaned_data["inventory_count"])
            if card.stars_unlocked <= 0 and inventory_input <= 0:
                card.inventory_count = 0
                card.save(update_fields=["inventory_count", "updated_at"])
            else:
                new_level, new_inventory = apply_inventory_rollover(
                    level=card.stars_unlocked,
                    inventory=inventory_input,
                )
                card.stars_unlocked = new_level
                card.inventory_count = new_inventory
                card.save(update_fields=["stars_unlocked", "inventory_count", "updated_at"])
            messages.success(request, "Saved card inventory.")
            return redirect(redirect_to)

        if action == "update_presets":
            form = CardPresetUpdateForm(request.POST, player=player)
            if not form.is_valid():
                messages.error(request, "Could not save card presets.")
                return redirect(redirect_to)

            card = PlayerCard.objects.filter(player=player, id=form.cleaned_data["card_id"]).first()
            if card is None:
                messages.error(request, "Card row not found.")
                return redirect(redirect_to)

            chosen_presets = list(form.cleaned_data["presets"])
            new_name = form.cleaned_data["new_preset_name"]
            if new_name:
                preset, _ = Preset.objects.get_or_create(player=player, name=new_name)
                chosen_presets.append(preset)
            card.presets.set(chosen_presets, through_defaults={"player": player})
            messages.success(request, "Saved card presets.")
            return redirect(redirect_to)

        messages.error(request, "Unknown cards action.")
        return redirect(redirect_to)

    filter_form = CardsFilterForm(request.GET, player=player)
    filter_form.is_valid()
    selected_presets = tuple(filter_form.cleaned_data.get("presets") or ())
    selected_maxed = (filter_form.cleaned_data.get("maxed") or "").strip()
    requested_sort = (filter_form.cleaned_data.get("sort") or "").strip()

    card_qs = (
        PlayerCard.objects.filter(player=player)
        .select_related("card_definition")
        .prefetch_related("presets")
        .order_by("card_definition__name", "card_slug")
    )
    if selected_presets:
        card_qs = card_qs.filter(presets__in=selected_presets).distinct()

    cards = list(card_qs)

    rows = []
    for card in cards:
        definition = card.card_definition
        name = definition.name if definition is not None else card.card_slug
        progress = derive_card_progress(
            stars_unlocked=card.stars_unlocked,
            inventory_count=card.inventory_count,
        )
        is_unowned = card.stars_unlocked <= 0 and card.inventory_count <= 0
        display_level = 0 if is_unowned else progress.level
        display_inventory = 0 if is_unowned else progress.inventory
        display_threshold = 0 if is_unowned else progress.threshold
        parameters_text = _render_card_parameters_text(
            description=(definition.description if definition is not None else ""),
            effect_raw=(definition.effect_raw if definition is not None else ""),
            level=display_level,
        )
        rows.append(
            {
                "id": card.id,
                "name": name,
                "level": display_level,
                "inventory_count": display_inventory,
                "inventory_threshold": display_threshold,
                "is_maxed": (not is_unowned and progress.is_maxed),
                "rarity": (definition.rarity if definition is not None else ""),
                "parameters_text": parameters_text,
                "presets": tuple(card.presets.all()),
                "updated_at": card.updated_at,
            }
        )

    if selected_maxed == "maxed":
        rows = [row for row in rows if row.get("is_maxed")]
    elif selected_maxed == "unmaxed":
        rows = [row for row in rows if not row.get("is_maxed")]

    allowed_sort_keys = {"name", "rarity", "level", "progress", "maxed"}
    current_sort = requested_sort if requested_sort.lstrip("-") in allowed_sort_keys else "name"
    rows = _sort_card_rows(rows, sort_key=current_sort)

    max_slots = card_slot_max_slots()
    next_cost = next_card_slot_unlock_cost_raw(unlocked=player.card_slots_unlocked)
    card_slots = {
        "unlocked": player.card_slots_unlocked,
        "max": max_slots,
        "next_cost": next_cost,
    }

    presets = Preset.objects.filter(player=player).order_by("name")
    preset_links = [
        {
            "preset": preset,
            "querystring": _preset_filter_querystring(request.GET, preset_id=preset.id),
        }
        for preset in presets
    ]
    sort_querystrings = _build_sort_querystrings_default_asc(
        request.GET,
        current_sort=current_sort,
        sortable_keys={
            "name": "name",
            "rarity": "rarity",
            "level": "level",
            "progress": "progress",
            "maxed": "maxed",
        },
    )
    return render(
        request,
        "core/cards.html",
        {
            "card_slots": card_slots,
            "filter_form": filter_form,
            "presets": presets,
            "preset_links": preset_links,
            "rows": rows,
            "sort_querystrings": sort_querystrings,
            "current_sort": current_sort,
        },
    )


@login_required
def ultimate_weapon_progress(request: HttpRequest) -> HttpResponse:
    """Render the Ultimate Weapon progress page."""
    player = _request_player(request)
    player_cards = tuple(
        PlayerCard.objects.filter(player=player, stars_unlocked__gt=0).select_related("card_definition")
    )

    uw_definitions = list(UltimateWeaponDefinition.objects.order_by("name"))
    for uw_def in uw_definitions:
        uw, created = PlayerUltimateWeapon.objects.get_or_create(
            player=player,
            ultimate_weapon_slug=uw_def.slug,
            defaults={"ultimate_weapon_definition": uw_def, "unlocked": False},
        )
        if not created and uw.ultimate_weapon_definition_id is None:
            uw.ultimate_weapon_definition = uw_def
            uw.save(update_fields=["ultimate_weapon_definition"])

    if request.method == "POST":
        action = (request.POST.get("action") or "").strip()
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
        redirect_to = request.POST.get("next") or request.path

        if action == "unlock_uw":
            uw_id = int(request.POST.get("entity_id") or request.POST.get("uw_id") or 0)
            uw = (
                PlayerUltimateWeapon.objects.filter(player=player, id=uw_id)
                .select_related("ultimate_weapon_definition")
                .first()
            )
            if uw is None or uw.ultimate_weapon_definition is None:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Ultimate Weapon not found."}, status=404)
                messages.error(request, "Ultimate Weapon not found.")
                return redirect(redirect_to)

            try:
                validate_uw_parameter_definitions(uw_definition=uw.ultimate_weapon_definition)
            except ValueError as exc:
                if settings.DEBUG:
                    raise
                messages.warning(request, f"Skipping {uw.ultimate_weapon_definition.name}: {exc}")
                if is_ajax:
                    return JsonResponse({"ok": False, "error": str(exc)}, status=400)
                return redirect(redirect_to)

            with transaction.atomic():
                uw.unlocked = True
                uw.save(update_fields=["unlocked", "updated_at"])
                for param_def in uw.ultimate_weapon_definition.parameter_definitions.all():
                    min_level = (
                        param_def.levels.order_by("level").values_list("level", flat=True).first() or 0
                    )
                    player_param, created_param = PlayerUltimateWeaponParameter.objects.get_or_create(
                        player=player,
                        player_ultimate_weapon=uw,
                        parameter_definition=param_def,
                        defaults={"level": min_level},
                    )
                    if not created_param and player_param.level <= 0 and min_level > 0:
                        player_param.level = min_level
                        player_param.save(update_fields=["level", "updated_at"])

            if is_ajax:
                uw = (
                    PlayerUltimateWeapon.objects.filter(player=player, id=uw.id)
                    .select_related("ultimate_weapon_definition")
                    .prefetch_related("parameters__parameter_definition__levels")
                    .first()
                )
                if uw is None or uw.ultimate_weapon_definition is None:
                    return JsonResponse({"ok": False, "error": "Ultimate Weapon not found."}, status=404)

                parameters = []
                total_stones = 0
                for player_param in uw.parameters.all().select_related("parameter_definition"):
                    param_def = player_param.parameter_definition
                    if param_def is None:
                        continue
                    levels = [
                        ParameterLevelRow(level=row.level, value_raw=row.value_raw, cost_raw=row.cost_raw)
                        for row in param_def.levels.order_by("level")
                    ]
                    param_view = build_uw_parameter_view(
                        player=player,
                        player_param=player_param,
                        levels=levels,
                        unit_kind=param_def.unit_kind,
                        player_cards=player_cards,
                    )
                    total_stones += total_stones_invested_for_parameter(
                        parameter_definition=param_def,
                        level=player_param.level,
                    )
                    parameters.append(param_view)
                return JsonResponse(
                    {
                        "ok": True,
                        "uw": {
                            "id": uw.id,
                            "unlocked": True,
                            "parameters": parameters,
                            "total_invested": total_stones,
                            "total_stones_invested": total_stones,
                        },
                    }
                )

            messages.success(request, f"Unlocked {uw.ultimate_weapon_definition.name}.")
            return redirect(redirect_to)

        if action == "level_up_uw_param":
            player_param_id = int(request.POST.get("param_id") or 0)
            player_param = (
                PlayerUltimateWeaponParameter.objects.filter(id=player_param_id)
                .select_related(
                    "player_ultimate_weapon",
                    "player_ultimate_weapon__ultimate_weapon_definition",
                    "parameter_definition",
                )
                .first()
            )
            if (
                player_param is None
                or player_param.parameter_definition is None
                or player_param.player_ultimate_weapon.player_id != player.id
            ):
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Parameter not found."}, status=404)
                messages.error(request, "Ultimate Weapon parameter not found.")
                return redirect(redirect_to)

            if not player_param.player_ultimate_weapon.unlocked:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Ultimate Weapon is locked."}, status=400)
                messages.error(request, "Cannot upgrade a locked Ultimate Weapon.")
                return redirect(redirect_to)

            param_def = player_param.parameter_definition
            levels_qs = param_def.levels.order_by("level")
            max_level = levels_qs.values_list("level", flat=True).last() or 0
            if player_param.level >= max_level:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Already at max level."}, status=400)
                messages.warning(request, "That parameter is already maxed.")
                return redirect(redirect_to)

            with transaction.atomic():
                player_param.level += 1
                player_param.save(update_fields=["level", "updated_at"])

            if is_ajax:
                levels = [
                    ParameterLevelRow(level=row.level, value_raw=row.value_raw, cost_raw=row.cost_raw)
                    for row in levels_qs
                ]
                param_view = build_uw_parameter_view(
                    player=player,
                    player_param=player_param,
                    levels=levels,
                    unit_kind=param_def.unit_kind,
                    player_cards=player_cards,
                )
                total_stones = total_stones_invested_for_parameter(
                    parameter_definition=param_def,
                    level=player_param.level,
                )
                return JsonResponse(
                    {
                        "ok": True,
                        "param": param_view,
                        "total_stones_invested_for_param": total_stones,
                    }
                )

            messages.success(request, f"Upgraded {param_def.display_name}.")
            return redirect(redirect_to)

        if is_ajax:
            return JsonResponse({"ok": False, "error": "Unknown action."}, status=400)
        messages.error(request, "Unknown action.")
        return redirect(redirect_to)

    filter_form = UltimateWeaponProgressFilterForm(request.GET)
    filter_form.is_valid()
    status = (filter_form.cleaned_data.get("status") or "").strip()


    unlocked_rows = (
        PlayerUltimateWeapon.objects.filter(player=player, unlocked=True)
        .select_related("ultimate_weapon_definition")
        .prefetch_related("ultimate_weapon_definition__parameter_definitions__levels")
    )
    for uw in unlocked_rows:
        uw_def = uw.ultimate_weapon_definition
        if uw_def is None:
            continue
        try:
            validate_uw_parameter_definitions(uw_definition=uw_def)
        except ValueError:
            continue
        for param_def in uw_def.parameter_definitions.all():
            min_level = param_def.levels.order_by("level").values_list("level", flat=True).first() or 0
            player_param, created_param = PlayerUltimateWeaponParameter.objects.get_or_create(
                player=player,
                player_ultimate_weapon=uw,
                parameter_definition=param_def,
                defaults={"level": min_level},
            )
            if not created_param and player_param.level <= 0 and min_level > 0:
                player_param.level = min_level
                player_param.save(update_fields=["level", "updated_at"])

    ultimate_weapons_qs = (
        PlayerUltimateWeapon.objects.filter(player=player)
        .select_related("ultimate_weapon_definition")
        .prefetch_related(
            "parameters__parameter_definition__levels",
            "ultimate_weapon_definition__parameter_definitions__levels",
        )
        .order_by("-unlocked", "ultimate_weapon_definition__name", "ultimate_weapon_slug")
    )
    if status == "unlocked":
        ultimate_weapons_qs = ultimate_weapons_qs.filter(unlocked=True)
    elif status == "locked":
        ultimate_weapons_qs = ultimate_weapons_qs.filter(unlocked=False)

    any_battles = BattleReport.objects.filter(player=player).exists()

    tiles: list[dict[str, object]] = []
    for uw in ultimate_weapons_qs:
        uw_def = uw.ultimate_weapon_definition
        if uw_def is None:
            if settings.DEBUG:
                raise ValueError(f"PlayerUltimateWeapon {uw.id} is missing its definition.")
            messages.warning(request, f"Skipping unknown UW slug={uw.ultimate_weapon_slug!r}.")
            continue

        try:
            validate_uw_parameter_definitions(uw_definition=uw_def)
        except ValueError as exc:
            if settings.DEBUG:
                raise
            messages.warning(request, f"Skipping {uw_def.name}: {exc}")
            continue

        player_params_by_def_id = {
            p.parameter_definition_id: p for p in uw.parameters.all() if p.parameter_definition_id
        }
        parameters = []
        total_stones_invested = 0
        for param_def in uw_def.parameter_definitions.all().order_by("id"):
            player_param = player_params_by_def_id.get(param_def.id)
            if player_param is None:
                if uw.unlocked:
                    if settings.DEBUG:
                        raise ValueError(
                            f"Missing PlayerUltimateWeaponParameter for uw={uw_def.slug} param={param_def.key}."
                        )
                continue
            levels = [
                ParameterLevelRow(level=row.level, value_raw=row.value_raw, cost_raw=row.cost_raw)
                for row in param_def.levels.order_by("level")
            ]
            view = build_uw_parameter_view(
                player=player,
                player_param=player_param,
                levels=levels,
                unit_kind=param_def.unit_kind,
                player_cards=player_cards,
            )
            total_stones_invested += total_stones_invested_for_parameter(
                parameter_definition=param_def,
                level=player_param.level,
            )
            parameters.append(view)

        if uw.unlocked and len(parameters) != 3:
            if settings.DEBUG:
                raise ValueError(
                    f"UW {uw_def.slug!r} rendered with {len(parameters)} parameters; expected 3."
                )
            messages.warning(request, f"Skipping {uw_def.name}: missing parameter rows.")
            continue

        runs_using = (
            BattleReport.objects.filter(player=player, run_combat_uws__ultimate_weapon_definition=uw_def)
            | BattleReport.objects.filter(player=player, run_utility_uws__ultimate_weapon_definition=uw_def)
        ).distinct()
        runs_count = runs_using.count() if any_battles else 0

        tiles.append(
            {
                "id": uw.id,
                "name": uw_def.name,
                "slug": uw_def.slug,
                "description": ((uw_def.description or "").splitlines() or [""])[0].strip(),
                "unlocked": uw.unlocked,
                "unlock_cost_raw": None,
                "summary": {
                    "total_invested": total_stones_invested,
                    "total_stones_invested": total_stones_invested,
                    "headline_label": (
                        "Runs used (observed)"
                        if uw.unlocked
                        else "Runs used while locked (observed)"
                    ),
                    "headline_value": runs_count,
                    "headline_empty": (not any_battles),
                },
                "parameters": parameters,
            }
        )

    uw_sync = build_uw_sync_payload(player=player)
    uw_snapshots = ChartSnapshot.objects.filter(player=player, target="ultimate_weapons").order_by("-created_at")
    uw_snapshot_id = request.GET.get("uw_snapshot_id")
    uw_snapshot_chart_json = None
    uw_snapshot_name = None
    if uw_snapshot_id:
        try:
            snapshot = uw_snapshots.filter(id=int(uw_snapshot_id)).first()
        except (TypeError, ValueError):
            snapshot = None
        if snapshot is not None and snapshot.config:
            dto = decode_chart_config_dto(dict(snapshot.config))
            validation = validate_chart_config_dto(dto, registry=DEFAULT_REGISTRY)
            if validation.is_valid:
                runs_qs = BattleReport.objects.select_related("run_progress", "run_progress__preset").order_by(
                    "run_progress__battle_date"
                )
                if dto.context.start_date:
                    runs_qs = runs_qs.filter(run_progress__battle_date__date__gte=dto.context.start_date)
                if dto.context.end_date:
                    runs_qs = runs_qs.filter(run_progress__battle_date__date__lte=dto.context.end_date)
                if dto.context.tier:
                    runs_qs = runs_qs.filter(run_progress__tier=dto.context.tier)
                if dto.context.preset_id:
                    runs_qs = runs_qs.filter(run_progress__preset_id=dto.context.preset_id)

                analyzed = analyze_chart_config_dto(
                    runs_qs,
                    config=dto,
                    registry=DEFAULT_REGISTRY,
                    moving_average_window=None,
                    entity_selections={},
                )
                palette = ["#3366CC", "#DC3912", "#FF9900", "#109618", "#990099", "#0099C6"]
                if analyzed.chart_type == "donut":
                    slice_colors = [palette[idx % len(palette)] for idx in range(len(analyzed.labels))]
                    unit = analyzed.datasets[0].unit if analyzed.datasets else ""
                    datasets = [
                        {
                            "label": snapshot.name,
                            "unit": unit,
                            "data": analyzed.datasets[0].values if analyzed.datasets else [],
                            "borderColor": "#ffffff",
                            "backgroundColor": slice_colors,
                        }
                    ]
                    payload = {"labels": analyzed.labels, "datasets": datasets, "chart_type": "donut"}
                else:
                    datasets = []
                    for idx, ds in enumerate(analyzed.datasets):
                        color = palette[idx % len(palette)]
                        datasets.append(
                            {
                                "label": ds.label,
                                "unit": ds.unit,
                                "data": ds.values,
                                "borderColor": color,
                                "backgroundColor": color,
                                "borderWidth": 2,
                                "pointRadius": 0,
                                "tension": 0.15,
                            }
                        )
                    payload = {"labels": analyzed.labels, "datasets": datasets, "chart_type": analyzed.chart_type}
                uw_snapshot_chart_json = json.dumps(payload)
                uw_snapshot_name = snapshot.name
    return render(
        request,
        "core/ultimate_weapon_progress.html",
        {
            "filter_form": filter_form,
            "ultimate_weapons": tiles,
            "has_battles": any_battles,
            "uw_sync_chart_json": json.dumps(uw_sync.chart_data) if uw_sync else None,
            "uw_sync_summary": uw_sync.summary if uw_sync else None,
            "uw_snapshots": uw_snapshots,
            "uw_snapshot_id": uw_snapshot_id,
            "uw_snapshot_chart_json": uw_snapshot_chart_json,
            "uw_snapshot_name": uw_snapshot_name,
        },
    )


@login_required
def guardian_progress(request: HttpRequest) -> HttpResponse:
    """Render the Guardian Chips progress dashboard."""

    player = _request_player(request)
    player_cards = tuple(
        PlayerCard.objects.filter(player=player, stars_unlocked__gt=0).select_related("card_definition")
    )

    orphaned_guardian_params_deleted, _ = PlayerGuardianChipParameter.objects.filter(
        player_guardian_chip__player=player,
        parameter_definition__isnull=True,
    ).delete()
    if orphaned_guardian_params_deleted and not request.headers.get("x-requested-with") == "XMLHttpRequest":
        messages.warning(request, "Removed guardian chip parameter rows that no longer match known definitions.")

    guardian_definitions = list(GuardianChipDefinition.objects.order_by("name"))
    for guardian_def in guardian_definitions:
        chip, created = PlayerGuardianChip.objects.get_or_create(
            player=player,
            guardian_chip_slug=guardian_def.slug,
            defaults={
                "guardian_chip_definition": guardian_def,
                "unlocked": False,
                "active": False,
            },
        )
        if not created and chip.guardian_chip_definition_id is None:
            chip.guardian_chip_definition = guardian_def
            chip.save(update_fields=["guardian_chip_definition"])

    if request.method == "POST":
        action = (request.POST.get("action") or "").strip()
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
        redirect_to = request.POST.get("next") or request.path

        if action == "unlock_guardian_chip":
            chip_id = int(request.POST.get("entity_id") or 0)
            chip = (
                PlayerGuardianChip.objects.filter(player=player, id=chip_id)
                .select_related("guardian_chip_definition")
                .first()
            )
            if chip is None or chip.guardian_chip_definition is None:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Guardian chip not found."}, status=404)
                messages.error(request, "Guardian chip not found.")
                return redirect(redirect_to)

            try:
                validate_parameter_definitions(
                    parameter_definitions=chip.guardian_chip_definition.parameter_definitions,
                    expected_count=3,
                    entity_kind="guardian chip",
                    entity_slug=chip.guardian_chip_definition.slug,
                )
            except ValueError as exc:
                if settings.DEBUG:
                    raise
                messages.warning(request, f"Skipping {chip.guardian_chip_definition.name}: {exc}")
                if is_ajax:
                    return JsonResponse({"ok": False, "error": str(exc)}, status=400)
                return redirect(redirect_to)

            with transaction.atomic():
                chip.unlocked = True
                chip.save(update_fields=["unlocked", "updated_at"])
                for param_def in chip.guardian_chip_definition.parameter_definitions.all():
                    min_level = (
                        param_def.levels.order_by("level").values_list("level", flat=True).first() or 0
                    )
                    player_param, created_param = PlayerGuardianChipParameter.objects.get_or_create(
                        player=player,
                        player_guardian_chip=chip,
                        parameter_definition=param_def,
                        defaults={"level": min_level},
                    )
                    if not created_param and player_param.level <= 0 and min_level > 0:
                        player_param.level = min_level
                        player_param.save(update_fields=["level", "updated_at"])

            if is_ajax:
                chip = (
                    PlayerGuardianChip.objects.filter(player=player, id=chip.id)
                    .select_related("guardian_chip_definition")
                    .prefetch_related("parameters__parameter_definition__levels")
                    .first()
                )
                if chip is None or chip.guardian_chip_definition is None:
                    return JsonResponse({"ok": False, "error": "Guardian chip not found."}, status=404)

                parameters = []
                total_bits = 0
                for player_param in chip.parameters.all().select_related("parameter_definition"):
                    param_def = player_param.parameter_definition
                    if param_def is None:
                        continue
                    levels = [
                        ParameterLevelRow(level=row.level, value_raw=row.value_raw, cost_raw=row.cost_raw)
                        for row in param_def.levels.order_by("level")
                    ]
                    param_view = build_upgradeable_parameter_view(
                        player=player,
                        entity_kind="guardian_chip",
                        player_param=player_param,
                        levels=levels,
                        unit_kind=param_def.unit_kind,
                        player_cards=player_cards,
                    )
                    total_bits += total_currency_invested_for_parameter(
                        parameter_definition=param_def,
                        level=player_param.level,
                    )
                    parameters.append(param_view)

                return JsonResponse(
                    {
                        "ok": True,
                        "guardian_chip": {
                            "id": chip.id,
                            "unlocked": True,
                            "active": chip.active,
                            "parameters": parameters,
                            "total_invested": total_bits,
                        },
                    }
                )

            messages.success(request, f"Unlocked {chip.guardian_chip_definition.name}.")
            return redirect(redirect_to)

        if action == "level_up_guardian_param":
            player_param_id = int(request.POST.get("param_id") or 0)
            player_param = (
                PlayerGuardianChipParameter.objects.filter(id=player_param_id)
                .select_related(
                    "player_guardian_chip",
                    "player_guardian_chip__guardian_chip_definition",
                    "parameter_definition",
                )
                .first()
            )
            if (
                player_param is None
                or player_param.parameter_definition is None
                or player_param.player_guardian_chip.player_id != player.id
            ):
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Parameter not found."}, status=404)
                messages.error(request, "Guardian chip parameter not found.")
                return redirect(redirect_to)

            if not player_param.player_guardian_chip.unlocked:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Guardian chip is locked."}, status=400)
                messages.error(request, "Cannot upgrade a locked Guardian Chip.")
                return redirect(redirect_to)

            param_def = player_param.parameter_definition
            levels_qs = param_def.levels.order_by("level")
            max_level = levels_qs.values_list("level", flat=True).last() or 0
            if player_param.level >= max_level:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Already at max level."}, status=400)
                messages.warning(request, "That parameter is already maxed.")
                return redirect(redirect_to)

            with transaction.atomic():
                player_param.level += 1
                player_param.save(update_fields=["level", "updated_at"])

            if is_ajax:
                levels = [
                    ParameterLevelRow(level=row.level, value_raw=row.value_raw, cost_raw=row.cost_raw)
                    for row in levels_qs
                ]
                param_view = build_upgradeable_parameter_view(
                    player=player,
                    entity_kind="guardian_chip",
                    player_param=player_param,
                    levels=levels,
                    unit_kind=param_def.unit_kind,
                    player_cards=player_cards,
                )
                total_bits = total_currency_invested_for_parameter(
                    parameter_definition=param_def,
                    level=player_param.level,
                )
                return JsonResponse(
                    {
                        "ok": True,
                        "param": param_view,
                        "total_invested_for_param": total_bits,
                    }
                )

            messages.success(request, f"Upgraded {param_def.display_name}.")
            return redirect(redirect_to)

        if action == "set_guardian_active":
            chip_id = int(request.POST.get("entity_id") or 0)
            desired_active = "1" in {(value or "").strip() for value in request.POST.getlist("active")}
            chip = PlayerGuardianChip.objects.filter(player=player, id=chip_id).first()
            if chip is None:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Guardian chip not found."}, status=404)
                messages.error(request, "Guardian chip not found.")
                return redirect(redirect_to)

            if desired_active and not chip.unlocked:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Guardian chip is locked."}, status=400)
                messages.error(request, "Cannot activate a locked Guardian Chip.")
                return redirect(redirect_to)

            chip.active = desired_active
            try:
                chip.save(update_fields=["active", "updated_at"])
            except ValidationError as exc:
                message = "; ".join(exc.messages) if getattr(exc, "messages", None) else str(exc)
                if is_ajax:
                    return JsonResponse({"ok": False, "error": message}, status=400)
                messages.error(request, message)
                return redirect(redirect_to)

            if is_ajax:
                return JsonResponse({"ok": True, "active": chip.active})
            messages.success(request, "Saved active guardian chip selection.")
            return redirect(redirect_to)

        if is_ajax:
            return JsonResponse({"ok": False, "error": "Unknown action."}, status=400)
        messages.error(request, "Unknown action.")
        return redirect(redirect_to)

    filter_form = UpgradeableEntityProgressFilterForm(request.GET, entity_label_plural="guardian chips")
    filter_form.is_valid()
    status = (filter_form.cleaned_data.get("status") or "").strip()

    unlocked_rows = (
        PlayerGuardianChip.objects.filter(player=player, unlocked=True)
        .select_related("guardian_chip_definition")
        .prefetch_related("guardian_chip_definition__parameter_definitions__levels")
    )
    for chip in unlocked_rows:
        chip_def = chip.guardian_chip_definition
        if chip_def is None:
            continue
        try:
            validate_parameter_definitions(
                parameter_definitions=chip_def.parameter_definitions,
                expected_count=3,
                entity_kind="guardian chip",
                entity_slug=chip_def.slug,
            )
        except ValueError:
            continue
        for param_def in chip_def.parameter_definitions.all():
            min_level = param_def.levels.order_by("level").values_list("level", flat=True).first() or 0
            player_param, created_param = PlayerGuardianChipParameter.objects.get_or_create(
                player=player,
                player_guardian_chip=chip,
                parameter_definition=param_def,
                defaults={"level": min_level},
            )
            if not created_param and player_param.level <= 0 and min_level > 0:
                player_param.level = min_level
                player_param.save(update_fields=["level", "updated_at"])

    chips_qs = (
        PlayerGuardianChip.objects.filter(player=player)
        .select_related("guardian_chip_definition")
        .prefetch_related(
            "parameters__parameter_definition__levels",
            "guardian_chip_definition__parameter_definitions__levels",
        )
        .order_by("-unlocked", "guardian_chip_definition__name", "guardian_chip_slug")
    )
    if status == "unlocked":
        chips_qs = chips_qs.filter(unlocked=True)
    elif status == "locked":
        chips_qs = chips_qs.filter(unlocked=False)

    any_battles = BattleReport.objects.filter(player=player).exists()
    active_count = PlayerGuardianChip.objects.filter(player=player, active=True).count()
    activation_limit_reached = active_count >= MAX_ACTIVE_GUARDIAN_CHIPS

    active_chip_rows = (
        PlayerGuardianChip.objects.filter(player=player, active=True)
        .select_related("guardian_chip_definition")
        .order_by("guardian_chip_definition__name", "guardian_chip_slug")
    )
    active_chip_hero = [
        {
            "name": row.guardian_chip_definition.name
            if row.guardian_chip_definition
            else row.guardian_chip_slug,
            "subtitle": "Active",
        }
        for row in active_chip_rows[:MAX_ACTIVE_GUARDIAN_CHIPS]
    ]

    tiles: list[dict[str, object]] = []
    for chip in chips_qs:
        chip_def = chip.guardian_chip_definition
        if chip_def is None:
            if settings.DEBUG:
                raise ValueError(f"PlayerGuardianChip {chip.id} is missing its definition.")
            messages.warning(request, f"Skipping unknown guardian chip slug={chip.guardian_chip_slug!r}.")
            continue

        try:
            validate_parameter_definitions(
                parameter_definitions=chip_def.parameter_definitions,
                expected_count=3,
                entity_kind="guardian chip",
                entity_slug=chip_def.slug,
            )
        except ValueError as exc:
            if settings.DEBUG:
                raise
            messages.warning(request, f"Skipping {chip_def.name}: {exc}")
            continue

        player_params_by_def_id = {
            p.parameter_definition_id: p for p in chip.parameters.all() if p.parameter_definition_id
        }
        parameters = []
        total_bits_invested = 0
        for param_def in chip_def.parameter_definitions.all().order_by("id"):
            player_param = player_params_by_def_id.get(param_def.id)
            if player_param is None:
                if chip.unlocked and settings.DEBUG:
                    raise ValueError(
                        f"Missing PlayerGuardianChipParameter for chip={chip_def.slug} param={param_def.key}."
                    )
                continue
            levels = [
                ParameterLevelRow(level=row.level, value_raw=row.value_raw, cost_raw=row.cost_raw)
                for row in param_def.levels.order_by("level")
            ]
            view = build_upgradeable_parameter_view(
                player=player,
                entity_kind="guardian_chip",
                player_param=player_param,
                levels=levels,
                unit_kind=param_def.unit_kind,
                player_cards=player_cards,
            )
            total_bits_invested += total_currency_invested_for_parameter(
                parameter_definition=param_def,
                level=player_param.level,
            )
            parameters.append(view)

        if chip.unlocked and len(parameters) != 3:
            if settings.DEBUG:
                raise ValueError(
                    f"Guardian chip {chip_def.slug!r} rendered with {len(parameters)} parameters; expected 3."
                )
            messages.warning(request, f"Skipping {chip_def.name}: missing parameter rows.")
            continue

        runs_using = BattleReport.objects.filter(
            player=player,
            run_guardians__guardian_chip_definition=chip_def,
        ).distinct()
        runs_count = runs_using.count() if any_battles else 0

        tiles.append(
            {
                "id": chip.id,
                "name": chip_def.name,
                "slug": chip_def.slug,
                "description": ((chip_def.description or "").splitlines() or [""])[0].strip(),
                "unlocked": chip.unlocked,
                "active": chip.active,
                "toggle_disabled": (not chip.unlocked) or (activation_limit_reached and not chip.active),
                "unlock_cost_raw": None,
                "summary": {
                    "total_invested": total_bits_invested,
                    "headline_label": "Runs used",
                    "headline_value": runs_count,
                    "headline_empty": (not any_battles),
                },
                "parameters": parameters,
            }
        )

    return render(
        request,
        "core/guardian_progress.html",
        {
            "filter_form": filter_form,
            "guardian_chips": tiles,
            "activation_limit_reached": activation_limit_reached,
            "active_chip_hero": active_chip_hero,
        },
    )


@login_required
def bots_progress(request: HttpRequest) -> HttpResponse:
    """Render the Bots progress dashboard."""

    player = _request_player(request)
    player_cards = tuple(
        PlayerCard.objects.filter(player=player, stars_unlocked__gt=0).select_related("card_definition")
    )

    orphaned_bot_params_deleted, _ = PlayerBotParameter.objects.filter(
        player_bot__player=player,
        parameter_definition__isnull=True,
    ).delete()
    if orphaned_bot_params_deleted and not request.headers.get("x-requested-with") == "XMLHttpRequest":
        messages.warning(request, "Removed bot parameter rows that no longer match known definitions.")

    bot_definitions = list(BotDefinition.objects.order_by("name"))
    for bot_def in bot_definitions:
        bot, created = PlayerBot.objects.get_or_create(
            player=player,
            bot_slug=bot_def.slug,
            defaults={"bot_definition": bot_def, "unlocked": False},
        )
        if not created and bot.bot_definition_id is None:
            bot.bot_definition = bot_def
            bot.save(update_fields=["bot_definition"])

    if request.method == "POST":
        action = (request.POST.get("action") or "").strip()
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
        redirect_to = request.POST.get("next") or request.path

        if action == "unlock_bot":
            bot_id = int(request.POST.get("entity_id") or 0)
            bot = (
                PlayerBot.objects.filter(player=player, id=bot_id)
                .select_related("bot_definition")
                .first()
            )
            if bot is None or bot.bot_definition is None:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Bot not found."}, status=404)
                messages.error(request, "Bot not found.")
                return redirect(redirect_to)

            try:
                validate_parameter_definitions(
                    parameter_definitions=bot.bot_definition.parameter_definitions,
                    expected_count=4,
                    entity_kind="bot",
                    entity_slug=bot.bot_definition.slug,
                )
            except ValueError as exc:
                if settings.DEBUG:
                    raise
                messages.warning(request, f"Skipping {bot.bot_definition.name}: {exc}")
                if is_ajax:
                    return JsonResponse({"ok": False, "error": str(exc)}, status=400)
                return redirect(redirect_to)

            with transaction.atomic():
                bot.unlocked = True
                bot.save(update_fields=["unlocked", "updated_at"])
                for param_def in bot.bot_definition.parameter_definitions.all():
                    min_level = (
                        param_def.levels.order_by("level").values_list("level", flat=True).first() or 0
                    )
                    player_param, created_param = PlayerBotParameter.objects.get_or_create(
                        player=player,
                        player_bot=bot,
                        parameter_definition=param_def,
                        defaults={"level": min_level},
                    )
                    if not created_param and player_param.level <= 0 and min_level > 0:
                        player_param.level = min_level
                        player_param.save(update_fields=["level", "updated_at"])

            if is_ajax:
                bot = (
                    PlayerBot.objects.filter(player=player, id=bot.id)
                    .select_related("bot_definition")
                    .prefetch_related("parameters__parameter_definition__levels")
                    .first()
                )
                if bot is None or bot.bot_definition is None:
                    return JsonResponse({"ok": False, "error": "Bot not found."}, status=404)

                parameters = []
                total_medals = 0
                for player_param in bot.parameters.all().select_related("parameter_definition"):
                    param_def = player_param.parameter_definition
                    if param_def is None:
                        continue
                    levels = [
                        ParameterLevelRow(level=row.level, value_raw=row.value_raw, cost_raw=row.cost_raw)
                        for row in param_def.levels.order_by("level")
                    ]
                    param_view = build_upgradeable_parameter_view(
                        player=player,
                        entity_kind="bot",
                        player_param=player_param,
                        levels=levels,
                        unit_kind=param_def.unit_kind,
                        player_cards=player_cards,
                    )
                    total_medals += total_currency_invested_for_parameter(
                        parameter_definition=param_def,
                        level=player_param.level,
                    )
                    parameters.append(param_view)
                return JsonResponse(
                    {
                        "ok": True,
                        "bot": {
                            "id": bot.id,
                            "unlocked": True,
                            "parameters": parameters,
                            "total_invested": total_medals,
                        },
                    }
                )

            messages.success(request, f"Unlocked {bot.bot_definition.name}.")
            return redirect(redirect_to)

        if action == "level_up_bot_param":
            player_param_id = int(request.POST.get("param_id") or 0)
            player_param = (
                PlayerBotParameter.objects.filter(id=player_param_id)
                .select_related("player_bot", "player_bot__bot_definition", "parameter_definition")
                .first()
            )
            if (
                player_param is None
                or player_param.parameter_definition is None
                or player_param.player_bot.player_id != player.id
            ):
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Parameter not found."}, status=404)
                messages.error(request, "Bot parameter not found.")
                return redirect(redirect_to)

            if not player_param.player_bot.unlocked:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Bot is locked."}, status=400)
                messages.error(request, "Cannot upgrade a locked Bot.")
                return redirect(redirect_to)

            param_def = player_param.parameter_definition
            levels_qs = param_def.levels.order_by("level")
            max_level = levels_qs.values_list("level", flat=True).last() or 0
            if player_param.level >= max_level:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Already at max level."}, status=400)
                messages.warning(request, "That parameter is already maxed.")
                return redirect(redirect_to)

            with transaction.atomic():
                player_param.level += 1
                player_param.save(update_fields=["level", "updated_at"])

            if is_ajax:
                levels = [
                    ParameterLevelRow(level=row.level, value_raw=row.value_raw, cost_raw=row.cost_raw)
                    for row in levels_qs
                ]
                param_view = build_upgradeable_parameter_view(
                    player=player,
                    entity_kind="bot",
                    player_param=player_param,
                    levels=levels,
                    unit_kind=param_def.unit_kind,
                    player_cards=player_cards,
                )
                total_medals = total_currency_invested_for_parameter(
                    parameter_definition=param_def,
                    level=player_param.level,
                )
                return JsonResponse(
                    {
                        "ok": True,
                        "param": param_view,
                        "total_invested_for_param": total_medals,
                    }
                )

            messages.success(request, f"Upgraded {param_def.display_name}.")
            return redirect(redirect_to)

        if is_ajax:
            return JsonResponse({"ok": False, "error": "Unknown action."}, status=400)
        messages.error(request, "Unknown action.")
        return redirect(redirect_to)

    filter_form = UpgradeableEntityProgressFilterForm(request.GET, entity_label_plural="bots")
    filter_form.is_valid()
    status = (filter_form.cleaned_data.get("status") or "").strip()

    unlocked_rows = (
        PlayerBot.objects.filter(player=player, unlocked=True)
        .select_related("bot_definition")
        .prefetch_related("bot_definition__parameter_definitions__levels")
    )
    for bot in unlocked_rows:
        bot_def = bot.bot_definition
        if bot_def is None:
            continue
        try:
            validate_parameter_definitions(
                parameter_definitions=bot_def.parameter_definitions,
                expected_count=4,
                entity_kind="bot",
                entity_slug=bot_def.slug,
            )
        except ValueError:
            continue
        for param_def in bot_def.parameter_definitions.all():
            min_level = param_def.levels.order_by("level").values_list("level", flat=True).first() or 0
            player_param, created_param = PlayerBotParameter.objects.get_or_create(
                player=player,
                player_bot=bot,
                parameter_definition=param_def,
                defaults={"level": min_level},
            )
            if not created_param and player_param.level <= 0 and min_level > 0:
                player_param.level = min_level
                player_param.save(update_fields=["level", "updated_at"])

    bots_qs = (
        PlayerBot.objects.filter(player=player)
        .select_related("bot_definition")
        .prefetch_related(
            "parameters__parameter_definition__levels",
            "bot_definition__parameter_definitions__levels",
        )
        .order_by("-unlocked", "bot_definition__name", "bot_slug")
    )
    if status == "unlocked":
        bots_qs = bots_qs.filter(unlocked=True)
    elif status == "locked":
        bots_qs = bots_qs.filter(unlocked=False)

    any_battles = BattleReport.objects.filter(player=player).exists()

    tiles: list[dict[str, object]] = []
    for bot in bots_qs:
        bot_def = bot.bot_definition
        if bot_def is None:
            if settings.DEBUG:
                raise ValueError(f"PlayerBot {bot.id} is missing its definition.")
            messages.warning(request, f"Skipping unknown bot slug={bot.bot_slug!r}.")
            continue

        try:
            validate_parameter_definitions(
                parameter_definitions=bot_def.parameter_definitions,
                expected_count=4,
                entity_kind="bot",
                entity_slug=bot_def.slug,
            )
        except ValueError as exc:
            if settings.DEBUG:
                raise
            messages.warning(request, f"Skipping {bot_def.name}: {exc}")
            continue

        if bot.unlocked and bot.parameters.filter(parameter_definition__isnull=True).exists():
            if settings.DEBUG:
                raise ValueError(f"Bot {bot_def.slug!r} has unknown parameter rows.")
            messages.warning(request, f"Skipping {bot_def.name}: unknown parameter rows present.")
            continue

        player_params_by_def_id = {
            p.parameter_definition_id: p for p in bot.parameters.all() if p.parameter_definition_id
        }
        parameters = []
        total_medals_invested = 0
        for param_def in bot_def.parameter_definitions.all().order_by("id"):
            player_param = player_params_by_def_id.get(param_def.id)
            if player_param is None:
                if bot.unlocked and settings.DEBUG:
                    raise ValueError(
                        f"Missing PlayerBotParameter for bot={bot_def.slug} param={param_def.key}."
                    )
                continue

            levels = [
                ParameterLevelRow(level=row.level, value_raw=row.value_raw, cost_raw=row.cost_raw)
                for row in param_def.levels.order_by("level")
            ]
            view = build_upgradeable_parameter_view(
                player=player,
                entity_kind="bot",
                player_param=player_param,
                levels=levels,
                unit_kind=param_def.unit_kind,
                player_cards=player_cards,
            )
            total_medals_invested += total_currency_invested_for_parameter(
                parameter_definition=param_def,
                level=player_param.level,
            )
            parameters.append(view)

        if bot.unlocked and len(parameters) != 4:
            if settings.DEBUG:
                raise ValueError(f"Bot {bot_def.slug!r} rendered with {len(parameters)} parameters; expected 4.")
            messages.warning(request, f"Skipping {bot_def.name}: missing parameter rows.")
            continue

        runs_using = BattleReport.objects.filter(player=player, run_bots__bot_definition=bot_def).distinct()
        runs_count = runs_using.count() if any_battles else 0

        tiles.append(
            {
                "id": bot.id,
                "name": bot_def.name,
                "slug": bot_def.slug,
                "description": ((bot_def.description or "").splitlines() or [""])[0].strip(),
                "unlocked": bot.unlocked,
                "unlock_cost_raw": None,
                "summary": {
                    "total_invested": total_medals_invested,
                    "headline_label": "Runs used",
                    "headline_value": runs_count,
                    "headline_empty": (not any_battles),
                },
                "parameters": parameters,
            }
        )

    return render(
        request,
        "core/bots_progress.html",
        {"filter_form": filter_form, "bots": tiles},
    )


def _filtered_runs(filter_form: ChartContextForm, *, player: Player) -> QuerySet[BattleReport]:
    """Return a filtered BattleReport queryset based on validated form data."""

    runs = BattleReport.objects.filter(player=player).select_related(
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
    window_kind = filter_form.cleaned_data.get("window_kind")
    window_n = filter_form.cleaned_data.get("window_n")
    if start_date:
        runs = runs.filter(run_progress__battle_date__date__gte=start_date)
    if end_date:
        runs = runs.filter(run_progress__battle_date__date__lte=end_date)
    if tier:
        runs = runs.filter(run_progress__tier=tier)
    if preset:
        runs = runs.filter(run_progress__preset=preset)
    if window_kind and window_n:
        runs = _apply_rolling_window(runs, kind=str(window_kind), n=int(window_n), end_date=end_date)
    return runs


def _apply_rolling_window(
    runs: QuerySet[BattleReport],
    *,
    kind: str,
    n: int,
    end_date: date | None,
) -> QuerySet[BattleReport]:
    """Apply a rolling window to an already context-filtered queryset.

    Args:
        runs: BattleReport queryset already scoped by date/preset/tier.
        kind: Either "last_runs" or "last_days".
        n: Window size.
        end_date: Optional explicit end date (inclusive) from the context filter.

    Returns:
        QuerySet additionally filtered to the requested rolling window.
    """

    if n <= 0:
        return runs

    dated = runs.exclude(run_progress__battle_date__isnull=True)
    if kind == "last_runs":
        ids = list(
            dated.order_by("-run_progress__battle_date")
            .values_list("id", flat=True)[:n]
        )
        if not ids:
            return runs.none()
        return runs.filter(id__in=ids).order_by("run_progress__battle_date")

    if kind == "last_days":
        if end_date is not None:
            window_end = end_date
        else:
            latest = dated.aggregate(latest=Max("run_progress__battle_date"))["latest"]
            if latest is None:
                return runs.none()
            window_end = latest.date()
        window_start = window_end - timedelta(days=max(n - 1, 0))
        return runs.filter(run_progress__battle_date__date__gte=window_start)

    return runs


def _context_filtered_runs(filter_form: ChartContextForm, *, player: Player) -> QuerySet[BattleReport]:
    """Return a queryset filtered only by tier/preset context.

    This is used for comparisons where the selected windows should remain
    independent of any chart date filters.
    """

    runs = BattleReport.objects.filter(player=player).select_related(
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
