"""Views for Phase 1 ingestion and Phase 3 navigation structure."""

from __future__ import annotations

import json
import csv
import io
import math
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone as dt_timezone
from typing import Any, Literal, TypedDict, cast
from collections.abc import Iterable, Sequence

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, DateTimeField, Max, Q, QuerySet
from django.db.models import Min
from django.db.models.functions import Coalesce
from django.http import HttpRequest, HttpResponse, JsonResponse, QueryDict
from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils import timezone

from analysis.aggregations import summarize_window
from analysis.battle_report_extract import extract_numeric_value
from analysis.chart_config_dto import ChartContextDTO
from analysis.chart_config_engine import analyze_chart_config_dto
from analysis.chart_config_validator import validate_chart_config_dto
from analysis.deltas import delta
from analysis.event_windows import (
    DEFAULT_EVENT_WINDOW_ANCHOR,
    coerce_window_bounds,
    current_event_window,
    shift_event_window,
)
from analysis.engine import analyze_metric_series, analyze_runs
from analysis.explore_dsl import build_explore_autocomplete, format_explore_dsl, parse_explore_dsl
from analysis.explore_engine import execute_explore_query
from analysis.explore_registry import (
    DEFAULT_BREAKDOWNS,
    ExploreBreakdownDefinition,
    ExploreMetricDefinition,
    build_explore_metric_registry,
)
from analysis.explore_schema import (
    FilterOperator,
    SCHEMA_VERSION,
    ExploreBreakdown,
    ExploreFilter,
    ExploreMetricSelection,
    ExploreQuery,
    ExploreScope,
    VisualizationHint,
    build_query_payload,
    validate_explore_query,
)
from analysis.dto import RunAnalysis
from analysis.metrics import MetricComputeConfig, compute_metric_value, get_metric_definition
from analysis.quantity import UnitType
from analysis.rates import coins_per_hour as coins_per_hour_rate
from analysis.series_registry import DEFAULT_REGISTRY, allowed_chart_builder_aggregations
from core.demo import DEMO_USERNAME, demo_mode_enabled, get_demo_player, set_demo_mode
from core.changelog import latest_changelog_summary
from core.dissonance import effective_multiplier, tier_bonus_rows
from core.dissonance import rebuild_dissonance_progression
from core.parsers.battle_report import battle_date_is_fallback
from core.advice import (
    AdviceItem,
    GoalScopeSample,
    GoalWeights,
    MIN_RUNS_FOR_ADVICE,
    SnapshotDeltaInput,
    generate_goal_weighted_advice,
    generate_optimization_advice,
    generate_snapshot_delta_advice,
)
from core.charting.configs import (
    CHART_CONFIG_BY_ID,
    default_selected_chart_ids,
    list_selectable_chart_configs,
)
from core.charting.dto_builder import build_chart_config_dto
from core.charting.flagging import flag_reasons, incomplete_run_labels
from core.charting.render import render_charts
from core.charting.snapshot_codec import decode_chart_config_dto, encode_chart_config_dto
from core.calculators import (
    LAB_GOALS,
    LAB_UNLOCK_COSTS,
    build_game_speed_result,
    format_duration_dhms,
    format_duration,
    lab_speedup_rows,
    progress_seconds_from_parts,
    wave_accelerator_reduction_percent,
)
from core.forms import (
    BattleHistoryColumnPreferenceForm,
    BattleHistoryFilterForm,
    BattleHistoryPresetUpdateForm,
    BattleReportSpecialRunUpdateForm,
    BattleReportImportForm,
    CardInventoryUpdateForm,
    CardPresetBulkUpdateForm,
    CardPresetUpdateForm,
    ChartBuilderSavedConfigForm,
    ChartFavoritesForm,
    ChartBuilderForm,
    ChartContextForm,
    CardsFilterForm,
    ComparisonForm,
    ExploreQueryForm,
    GameSpeedCalculatorForm,
    GoalTargetUpdateForm,
    GoalsFilterForm,
    LabsSpeedupCalculatorForm,
    LifetimeStatsFilterForm,
    UpgradeableEntityProgressFilterForm,
    UltimateWeaponProgressFilterForm,
)
from core.goals import (
    GoalCandidate,
    GoalRow,
    goal_candidates_for_modal,
    goal_rows_for_dashboard,
    goals_widget_rows,
)
from core.upgradeables import (
    ParameterLevelRow,
    build_upgradeable_parameter_view,
    build_uw_parameter_view,
    total_currency_invested_for_parameter,
    total_currency_invested_from_level_zero,
    total_stones_invested_for_parameter,
    levels_with_baseline_zero,
    validate_parameter_definitions,
    validate_uw_parameter_definitions,
)
from core.lifetime_stats import build_lifetime_stat_groups
from definitions.models import (
    BotDefinition,
    CardDefinition,
    GuardianChipDefinition,
    PatchBoundary,
    UltimateWeaponDefinition,
)
from gamedata.models import (
    BattleReport,
    BattleReportDerivedMetrics,
    BattleReportProgress,
    DISSONANCE_TYPE_CHOICES,
    DISSONANCE_TYPE_KEYS,
    TOURNAMENT_RANK_CHOICES,
)
from player_state.card_slots import card_slot_max_slots, next_card_slot_unlock_cost_raw
from player_state.cards import apply_inventory_rollover, derive_card_progress, derive_total_cards_progress
from player_state.economy import enforce_and_deduct_gems_if_tracked
from player_state.guardian_chip_slots import (
    guardian_chip_max_slots,
    next_guardian_chip_slot_unlock_cost_raw,
)
from player_state.models import (
    BattleHistoryColumnPreference,
    ChartBuilderSavedConfig,
    ChartDashboardPreference,
    ChartSnapshot,
    ExploreQuery as ExploreQueryModel,
    ExploreQueryTemplate,
    GoalTarget,
    GoalType,
    MAX_ACTIVE_GUARDIAN_CHIPS,
    Player,
    PlayerBot,
    PlayerBotRespecWindow,
    PlayerBotParameter,
    PlayerCard,
    PlayerGuardianChip,
    PlayerGuardianChipParameter,
    PlayerUltimateWeapon,
    PlayerUltimateWeaponParameter,
    Preset,
)
from core.tournament import (
    is_tournament,
    tier_filter_value,
    tournament_bracket,
    tournament_filter_value,
)
from core.search import build_search_items
from core.uw_sync import build_uw_sync_payload
from core.uw_usage import count_observed_uw_runs
from core.redirects import safe_redirect
from core.services import ingest_battle_report
from core.session_keys import MOTD_LAST_LOGIN_SESSION_KEY

WALKTHROUGH_FIRST_LOGIN_SESSION_KEY = "tts_walkthrough_first_login"
WALKTHROUGH_CHANGELOG_URL = "https://github.com/mahbam42/theTowerStats/blob/main/CHANGELOG.md"
DISS_NO_CONTEXT_NOTE = "Dissonance runs are excluded unless you enable the Dissonance toggle."


def _request_player(request: HttpRequest) -> Player:
    """Return the Player associated with the authenticated user."""

    player, _ = Player.objects.get_or_create(
        user=request.user,
        defaults={"display_name": getattr(request.user, "username", "Player")},
    )
    if demo_mode_enabled(request):
        return get_demo_player()
    return player


def _reject_demo_write(request: HttpRequest) -> HttpResponse:
    """Reject write actions while demo mode is enabled.

    Args:
        request: Incoming request.

    Returns:
        Redirect response back to the current page with an error message.
    """

    messages.error(request, "Demo mode is read-only. Exit demo mode to make changes.")
    return safe_redirect(
        request,
        candidates=[request.POST.get("next"), request.META.get("HTTP_REFERER")],
        fallback=request.path,
    )


def search(request: HttpRequest) -> HttpResponse:
    """Render the global search page."""

    query = (request.GET.get("q") or "").strip()
    results = build_search_items(request=request, query=query, limit=30) if query else []
    return render(
        request,
        "core/search.html",
        {
            "query": query,
            "results": results,
            "demo_mode": demo_mode_enabled(request),
        },
    )


def search_api(request: HttpRequest) -> JsonResponse:
    """Return JSON search results for the global typeahead."""

    query = (request.GET.get("q") or "").strip()
    if not query:
        return JsonResponse({"query": "", "results": []})
    results = build_search_items(request=request, query=query, limit=10)
    return JsonResponse({"query": query, "results": [item.as_json() for item in results]})


@login_required
def enable_demo_mode(request: HttpRequest) -> HttpResponse:
    """Enable demo mode for the current session."""

    if request.method != "POST":
        return redirect("core:dashboard")

    _ = get_demo_player()
    set_demo_mode(request, enabled=True)
    messages.success(request, "Demo mode enabled.")
    return safe_redirect(
        request,
        candidates=[request.POST.get("next"), request.META.get("HTTP_REFERER")],
        fallback=reverse("core:dashboard"),
    )


@login_required
def disable_demo_mode(request: HttpRequest) -> HttpResponse:
    """Disable demo mode for the current session."""

    if request.method != "POST":
        return redirect("core:dashboard")

    set_demo_mode(request, enabled=False)
    messages.success(request, "Demo mode disabled.")
    return safe_redirect(
        request,
        candidates=[request.POST.get("next"), request.META.get("HTTP_REFERER")],
        fallback=reverse("core:dashboard"),
    )


def login_view(request: HttpRequest) -> HttpResponse:
    """Render a combined sign-in + account creation page.

    This view replaces Django's default LoginView so new users can create an
    account directly from the sign-in page.
    """

    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    next_url = request.GET.get("next", "")
    login_form = AuthenticationForm(request)
    signup_form = UserCreationForm()

    if request.method == "POST":
        next_url = request.POST.get("next", next_url)
        if "signup_submit" in request.POST:
            signup_form = UserCreationForm(request.POST)
            if signup_form.is_valid():
                if (signup_form.cleaned_data.get("username") or "").strip() == DEMO_USERNAME:
                    signup_form.add_error("username", "That username is reserved.")
                    return render(
                        request,
                        "registration/login.html",
                        {
                            "login_form": login_form,
                            "signup_form": signup_form,
                            "next": next_url,
                        },
                    )
                user = signup_form.save()
                request.session[MOTD_LAST_LOGIN_SESSION_KEY] = (
                    user.last_login.isoformat() if user.last_login else ""
                )
                request.session[WALKTHROUGH_FIRST_LOGIN_SESSION_KEY] = True
                auth_login(request, user)
                return safe_redirect(
                    request,
                    candidates=[request.POST.get("next"), request.GET.get("next")],
                    fallback=settings.LOGIN_REDIRECT_URL,
                )
        else:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                request.session[MOTD_LAST_LOGIN_SESSION_KEY] = (
                    user.last_login.isoformat() if user.last_login else ""
                )
                if user.last_login is None:
                    request.session[WALKTHROUGH_FIRST_LOGIN_SESSION_KEY] = True
                else:
                    request.session.pop(WALKTHROUGH_FIRST_LOGIN_SESSION_KEY, None)
                auth_login(request, user)
                return safe_redirect(
                    request,
                    candidates=[request.POST.get("next"), request.GET.get("next")],
                    fallback=settings.LOGIN_REDIRECT_URL,
                )

    return render(
        request,
        "registration/login.html",
        {
            "login_form": login_form,
            "signup_form": signup_form,
            "next": next_url,
        },
    )


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Render the Charts dashboard driven by ChartConfig definitions."""

    player = _request_player(request)
    walkthrough_first_login = bool(request.session.pop(WALKTHROUGH_FIRST_LOGIN_SESSION_KEY, False))
    walkthrough_enabled = demo_mode_enabled(request) or walkthrough_first_login
    selectable_configs = list_selectable_chart_configs()
    available_chart_ids = {cfg.id for cfg in selectable_configs}
    favorite_chart_ids = _favorite_chart_ids(player=player, available_ids=available_chart_ids)
    if request.method == "POST" and demo_mode_enabled(request):
        return _reject_demo_write(request)

    if request.method == "GET" and (shift_value := (request.GET.get("event_shift") or "").strip()):
        if shift_value == "all":
            redirected = request.GET.copy()
            redirected.pop("event_shift", None)

            earliest = (
                BattleReport.objects.filter(player=player)
                .annotate(
                    effective_battle_date=Coalesce(
                        "run_progress__battle_date",
                        "parsed_at",
                        output_field=DateTimeField(),
                    )
                )
                .aggregate(earliest=Min("effective_battle_date"))["earliest"]
            )
            if earliest is not None:
                redirected["start_date"] = earliest.date().isoformat()
                redirected["end_date"] = date.today().isoformat()

            qs = redirected.urlencode()
            target = reverse("core:dashboard")
            return redirect(f"{target}?{qs}" if qs else target)

        try:
            shift = int(shift_value)
        except ValueError:
            shift = 0
        if shift in (-1, 1):
            parsed_start: date | None = None
            parsed_end: date | None = None
            try:
                if request.GET.get("start_date"):
                    parsed_start = date.fromisoformat(str(request.GET.get("start_date")))
            except ValueError:
                parsed_start = None
            try:
                if request.GET.get("end_date"):
                    parsed_end = date.fromisoformat(str(request.GET.get("end_date")))
            except ValueError:
                parsed_end = None

            if parsed_start is None and parsed_end is None:
                base = current_event_window(target=date.today())
            else:
                base = coerce_window_bounds(start=parsed_start, end=parsed_end)

            shifted = shift_event_window(base, shift=shift)
            redirected = request.GET.copy()
            redirected.pop("event_shift", None)
            redirected["start_date"] = shifted.start.isoformat()
            redirected["end_date"] = shifted.end.isoformat()
            qs = redirected.urlencode()
            target = reverse("core:dashboard")
            return redirect(f"{target}?{qs}" if qs else target)

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
                merged["aggregation"] = config_dto.aggregation or ""
                merged["x_axis"] = config_dto.x_axis
                if config_dto.scopes is not None:
                    merged["run_a"] = str(config_dto.scopes[0].run_id or "")
                    merged["run_b"] = str(config_dto.scopes[1].run_id or "")
                    merged["window_a_start"] = (config_dto.scopes[0].start_date.isoformat() if config_dto.scopes[0].start_date else "")
                    merged["window_a_end"] = (config_dto.scopes[0].end_date.isoformat() if config_dto.scopes[0].end_date else "")
                    merged["window_b_start"] = (config_dto.scopes[1].start_date.isoformat() if config_dto.scopes[1].start_date else "")
                    merged["window_b_end"] = (config_dto.scopes[1].end_date.isoformat() if config_dto.scopes[1].end_date else "")
                merged["start_date"] = config_dto.context.start_date.isoformat() if config_dto.context.start_date else ""
                merged["end_date"] = config_dto.context.end_date.isoformat() if config_dto.context.end_date else ""
                if config_dto.context.tournament_filter:
                    merged["tier"] = tournament_filter_value(config_dto.context.tournament_filter)
                else:
                    merged["tier"] = (
                        tier_filter_value(config_dto.context.tier)
                        if config_dto.context.tier
                        else ""
                    )
                merged["preset"] = str(config_dto.context.preset_id or "")
                merged["include_tournaments"] = "on" if config_dto.context.include_tournaments else ""
                merged["include_dissonance"] = "on" if config_dto.context.include_dissonance else ""
                merged["include_hidden"] = "on" if config_dto.context.include_hidden else ""
            else:
                builder_payload = dict(snapshot.chart_builder or {})
                context_payload = dict(snapshot.chart_context or {})
                merged["builder"] = "1"
                for key, value in builder_payload.items():
                    if key == "metric_keys" and isinstance(value, list):
                        merged.setlist("metric_keys", [str(v) for v in value])
                    else:
                        merged[key] = str(value) if value is not None else ""
                if "x_axis" not in builder_payload:
                    merged["x_axis"] = "time"
                for key, value in context_payload.items():
                    merged[key] = str(value) if value is not None else ""

            effective_get = merged
    if request.method == "POST":
        action = (request.POST.get("action") or "").strip()
        if action == "update_chart_favorites":
            favorites_form = ChartFavoritesForm(
                request.POST,
                available_chart_ids=available_chart_ids,
            )
            if favorites_form.is_valid():
                ChartDashboardPreference.objects.update_or_create(
                    player=player,
                    defaults={"favorite_chart_ids": list(favorites_form.cleaned_data["favorite_chart_ids"])},
                )
                messages.success(request, "Saved favorite charts.")
            else:
                messages.error(request, "Could not save favorite charts.")
            return redirect("core:dashboard")
        if action == "save_chart_builder_creation":
            metadata_form = ChartBuilderSavedConfigForm(request.POST)
            chart_form = ChartContextForm(effective_get, player=player, today=date.today())  # type: ignore[arg-type]
            chart_form.is_valid()
            context_runs = _context_filtered_runs(chart_form, player=player)
            builder_form = ChartBuilderForm(request.POST, runs_queryset=context_runs)
            if not metadata_form.is_valid() or not builder_form.is_valid():
                messages.error(request, "Could not save the chart builder entry.")
                return redirect("core:dashboard")
            config_dto = build_chart_config_dto(context_form=chart_form, builder_form=builder_form)
            validation = validate_chart_config_dto(config_dto, registry=DEFAULT_REGISTRY)
            if not validation.is_valid:
                messages.error(request, "Could not save the chart builder entry: validation failed.")
                return redirect("core:dashboard")
            payload = _chart_builder_payload(builder_form)
            saved_id = metadata_form.cleaned_data.get("saved_id")
            name = metadata_form.cleaned_data["name"]
            if saved_id:
                updated = ChartBuilderSavedConfig.objects.filter(player=player, id=saved_id).update(
                    name=name,
                    config=encode_chart_config_dto(config_dto),
                    chart_builder=payload,
                )
                if updated:
                    messages.success(request, "Updated saved chart.")
                else:
                    messages.error(request, "Saved chart not found.")
                return redirect("core:dashboard")
            try:
                ChartBuilderSavedConfig.objects.create(
                    player=player,
                    name=name,
                    config=encode_chart_config_dto(config_dto),
                    chart_builder=payload,
                )
            except Exception as exc:
                if settings.DEBUG:
                    raise
                messages.error(request, f"Could not save the chart builder entry: {exc}")
                return redirect("core:dashboard")
            messages.success(request, "Saved chart builder entry.")
            return redirect("core:dashboard")
        if action == "delete_chart_builder_creation":
            saved_id = request.POST.get("saved_id")
            try:
                saved_pk = int(saved_id or "")
            except ValueError:
                saved_pk = None
            if not saved_pk:
                messages.error(request, "Saved chart not found.")
                return redirect("core:dashboard")
            deleted, _ = ChartBuilderSavedConfig.objects.filter(player=player, id=saved_pk).delete()
            if deleted:
                messages.success(request, "Deleted saved chart.")
            else:
                messages.error(request, "Saved chart not found.")
            return redirect("core:dashboard")
        if action == "create_chart_snapshot":
            name = (request.POST.get("snapshot_name") or "").strip()
            if not name:
                messages.error(request, "Snapshot name is required.")
                return redirect("core:dashboard")
            target = (request.POST.get("snapshot_target") or "charts").strip() or "charts"

            chart_form = ChartContextForm(effective_get, player=player, today=date.today())  # type: ignore[arg-type]
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

        import_form = BattleReportImportForm(request.POST, player=player)
        if import_form.is_valid():
            raw_text = import_form.cleaned_data["raw_text"]
            preset_name = import_form.cleaned_data.get("preset_name") or None
            is_tournament_override = bool(import_form.cleaned_data.get("is_tournament") or False)
            tournament_rank = (import_form.cleaned_data.get("tournament_rank") or None)
            is_dissonance_override = bool(import_form.cleaned_data.get("is_dissonance") or False)
            dissonance_type = (import_form.cleaned_data.get("dissonance_type") or None)
            try:
                _, created = ingest_battle_report(
                    raw_text,
                    player=player,
                    preset_name=preset_name,
                    is_tournament=is_tournament_override,
                    tournament_rank=tournament_rank,
                    is_dissonance=is_dissonance_override,
                    dissonance_type=dissonance_type,
                )
            except Exception:
                if settings.DEBUG:
                    raise
                import_form.add_error(None, "Import failed. Review the pasted report and try again.")
                messages.error(request, "Could not import Battle Report.")
            else:
                if created:
                    messages.success(request, "Battle Report imported.")
                else:
                    messages.warning(request, "Duplicate Battle Report ignored.")
                return redirect("core:dashboard")
    else:
        import_form = BattleReportImportForm(player=player)

    defaulted_get = (
        effective_get.copy()
        if isinstance(effective_get, QueryDict)
        else QueryDict("", mutable=True)
    )
    if not isinstance(effective_get, QueryDict):
        for key, value in effective_get.items():
            defaulted_get[key] = str(value)

    if not defaulted_get.get("start_date") and not defaulted_get.get("end_date"):
        if demo_mode_enabled(request):
            defaulted_get["start_date"] = DEFAULT_EVENT_WINDOW_ANCHOR.isoformat()
            defaulted_get["end_date"] = date(2025, 12, 22).isoformat()
        else:
            window = current_event_window(target=date.today())
            defaulted_get["start_date"] = window.start.isoformat()
            defaulted_get["end_date"] = window.end.isoformat()

    if not defaulted_get.get("charts"):
        if favorite_chart_ids:
            defaulted_get.setlist("charts", [str(cid) for cid in favorite_chart_ids])
        else:
            defaulted_get.setlist("charts", [str(cid) for cid in default_selected_chart_ids()])

    if not defaulted_get.get("granularity"):
        defaulted_get["granularity"] = "per_run"

    chart_form = ChartContextForm(defaulted_get, player=player, today=date.today())  # type: ignore[arg-type]
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
        context_runs=context_runs,
    )
    (
        tier_options,
        preset_options,
        tournament_options,
        patch_options,
        compare_run_map,
    ) = _comparison_scope_options(context_runs)
    compare_run_map_json = json.dumps(compare_run_map)
    comparison_scope_warning = None
    scope_average = bool(comparison_form.cleaned_data.get("scope_average") or False)
    if comparison_result and comparison_result.get("kind") == "run_sets":
        comparison_scope_warning = _comparison_scope_size_warning(
            scope_a_count=cast(int | None, comparison_result.get("scope_a_run_count")),
            scope_b_count=cast(int | None, comparison_result.get("scope_b_run_count")),
            scope_average=scope_average,
        )
    advice_items = generate_optimization_advice(comparison_result)

    advice_snapshot_a = getattr(effective_get, "get", lambda _k: None)("advice_snapshot_a")
    advice_snapshot_b = getattr(effective_get, "get", lambda _k: None)("advice_snapshot_b")
    advice_mode = getattr(effective_get, "get", lambda _k: None)("advice_mode") or "snapshot_vs_current"
    goal_intent = (getattr(effective_get, "get", lambda _k: None)("goal_intent") or "hybrid").strip()
    goal_label, goal_weights = _goal_weights_from_query(
        goal_intent=goal_intent,
        query=effective_get,
    )

    if comparison_result and comparison_result.get("goal_aware_supported"):
        kind = str(comparison_result.get("kind") or "")
        has_sufficient_scopes = False
        if kind == "run_sets":
            a_count = comparison_result.get("scope_a_run_count")
            b_count = comparison_result.get("scope_b_run_count")
            has_sufficient_scopes = isinstance(a_count, int) and isinstance(b_count, int) and a_count >= MIN_RUNS_FOR_ADVICE and b_count >= MIN_RUNS_FOR_ADVICE
        elif kind == "windows":
            window_a = comparison_result.get("window_a")
            window_b = comparison_result.get("window_b")
            a_count = getattr(window_a, "run_count", None)
            b_count = getattr(window_b, "run_count", None)
            has_sufficient_scopes = isinstance(a_count, int) and isinstance(b_count, int) and a_count >= MIN_RUNS_FOR_ADVICE and b_count >= MIN_RUNS_FOR_ADVICE

        if has_sufficient_scopes and comparison_result.get("focus_metrics_sufficient") is not False:
            baseline_sample = comparison_result.get("goal_baseline")
            comparison_sample = comparison_result.get("goal_comparison")
            if isinstance(baseline_sample, GoalScopeSample) and isinstance(comparison_sample, GoalScopeSample):
                goal_items = generate_goal_weighted_advice(
                    goal_label=goal_label,
                    baseline=baseline_sample,
                    comparison=comparison_sample,
                    weights=goal_weights,
                )
                advice_items = tuple(advice_items) + tuple(goal_items)

    snapshot_advice_items: tuple[AdviceItem, ...] = ()
    if advice_snapshot_a:
        snapshot_advice_items = _build_snapshot_delta_advice(
            player=player,
            runs_current=runs,
            snapshot_a_id=str(advice_snapshot_a),
            snapshot_b_id=(str(advice_snapshot_b) if advice_snapshot_b else None),
            mode=str(advice_mode),
        )
        goal_items = _build_goal_weighted_advice(
            player=player,
            runs_current=runs,
            snapshot_a_id=str(advice_snapshot_a),
            snapshot_b_id=(str(advice_snapshot_b) if advice_snapshot_b else None),
            mode=str(advice_mode),
            goal_label=goal_label,
            weights=goal_weights,
        )
        snapshot_advice_items = tuple(snapshot_advice_items) + tuple(goal_items)
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
                        "x_axis": analyzed.x_axis,
                    }
                elif analyzed.x_axis == "metric":
                    for idx, ds in enumerate(analyzed.datasets):
                        color = palette[idx % len(palette)]
                        metric_dataset = {
                            "label": ds.label,
                            "metricKey": ds.metric_key,
                            "metricKind": "observed",
                            "unit": ds.unit,
                            "seriesKind": "metric",
                            "data": ds.values,
                            "borderColor": color,
                            "backgroundColor": color,
                            "pointRadius": 4,
                            "pointHoverRadius": 6,
                            "borderWidth": 2,
                        }
                        datasets.append(metric_dataset)
                    unit = analyzed.datasets[0].unit if analyzed.datasets else ""
                    builder_panel = {
                        "id": "chart_builder_custom",
                        "title": "Chart Builder",
                        "description": "Runtime chart (not persisted).",
                        "unit": unit,
                        "chart_type": analyzed.chart_type,
                        "labels": analyzed.labels,
                        "datasets": datasets,
                        "run_ids": analyzed.run_ids,
                        "x_label": analyzed.x_label,
                        "x_unit": analyzed.x_unit,
                        "y_label": analyzed.y_label,
                        "y_unit": analyzed.y_unit,
                        "x_axis": analyzed.x_axis,
                    }
                else:
                    for idx, ds in enumerate(analyzed.datasets):
                        color = palette[idx % len(palette)]
                        values = cast(list[float | None], ds.values)
                        reasons = flag_reasons(
                            analyzed.labels,
                            values=values,
                            incomplete_labels=incomplete_labels,
                            patch_boundaries=patch_boundaries,
                        )
                        chart_dataset: dict[str, Any] = {
                            "label": ds.label,
                            "metricKey": ds.metric_key,
                            "metricKind": "observed",
                            "unit": ds.unit,
                            "seriesKind": "raw",
                            "data": values,
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
                        datasets.append(chart_dataset)
                    unit = analyzed.datasets[0].unit if analyzed.datasets else ""
                    builder_panel = {
                        "id": "chart_builder_custom",
                        "title": "Chart Builder",
                        "description": "Runtime chart (not persisted).",
                        "unit": unit,
                        "chart_type": analyzed.chart_type,
                        "labels": analyzed.labels,
                        "datasets": datasets,
                        "x_axis": analyzed.x_axis,
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
    run_numbers_by_report_id = _run_numbers_by_report_id(player=player)
    rendered = render_charts(
        configs=configs_to_render,
        records=runs,
        registry=DEFAULT_REGISTRY,
        granularity=str(chart_form.cleaned_data.get("granularity") or "daily"),
        moving_average_window=chart_form.cleaned_data.get("moving_average_window"),
        entity_selections={
            "uw": getattr(chart_form.cleaned_data.get("ultimate_weapon"), "name", None),
            "guardian": getattr(chart_form.cleaned_data.get("guardian_chip"), "name", None),
            "bot": getattr(chart_form.cleaned_data.get("bot"), "name", None),
        },
        patch_boundaries=tuple(PatchBoundary.objects.values_list("boundary_date", flat=True)),
        run_numbers_by_report_id=run_numbers_by_report_id,
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
                "stacked": entry.config.stacked,
                "labels": entry.data["labels"],
                "datasets": entry.data["datasets"],
                "run_ids": entry.data.get("run_ids"),
                "totals": entry.data.get("totals"),
                "x_label": entry.data.get("x_label"),
                "x_unit": entry.data.get("x_unit"),
                "y_label": entry.data.get("y_label"),
                "y_unit": entry.data.get("y_unit"),
                "x_axis": "metric" if entry.config.chart_type == "scatter" else "time",
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
                "run_ids": builder_panel.get("run_ids"),
                "x_label": builder_panel.get("x_label"),
                "x_unit": builder_panel.get("x_unit"),
                "y_label": builder_panel.get("y_label"),
                "y_unit": builder_panel.get("y_unit"),
                "x_axis": builder_panel.get("x_axis"),
            }
        )
        combined = [json.loads(builder_json)] + json.loads(chart_panels_json)
        chart_panels_json = json.dumps(combined)

    config_by_id = {cfg.id: cfg for cfg in selectable_configs}
    favorite_charts = [config_by_id[cid] for cid in favorite_chart_ids if cid in config_by_id]
    available_favorite_charts = [
        cfg for cfg in selectable_configs if cfg.id not in favorite_chart_ids
    ]
    favorite_chart_ids_json = json.dumps(list(favorite_chart_ids))
    saved_chart_builder_configs = (
        ChartBuilderSavedConfig.objects.filter(player=player).order_by("name")
    )
    saved_chart_builder_configs_json = json.dumps(
        [
            {"id": cfg.id, "name": cfg.name, "chart_builder": cfg.chart_builder}
            for cfg in saved_chart_builder_configs
        ]
    )

    chart_context = _chart_context_summary(chart_form, selectable_configs=selectable_configs)
    has_filters = _form_has_filters(chart_form)
    chartable_points = sum(
        1
        for panel in rendered
        for dataset in panel.data["datasets"]
        for value in dataset.get("data", [])
        if value is not None
    )
    chart_empty_state = _chart_empty_state_message(
        total_filtered_runs=total_filtered_runs,
        chartable_runs=chartable_points,
        has_filters=has_filters,
    )
    scope_summary = _chart_scope_summary_payload(
        chart_context=chart_context,
        total_filtered_runs=total_filtered_runs,
        chartable_points=chartable_points,
        has_filters=has_filters,
        chart_empty_state=chart_empty_state,
    )
    why_panel = _why_am_i_seeing_this_payload(
        chart_context=chart_context,
        total_filtered_runs=total_filtered_runs,
        chartable_points=chartable_points,
        has_filters=has_filters,
        chart_empty_state=chart_empty_state,
    )
    explore_modal_scope = ExploreScope(
        start_date=chart_form.cleaned_data.get("start_date"),
        end_date=chart_form.cleaned_data.get("end_date"),
        tier=chart_form.cleaned_data.get("tier"),
        preset_id=getattr(chart_form.cleaned_data.get("preset"), "id", None),
        snapshot_id=getattr(chart_form.cleaned_data.get("context_snapshot"), "id", None),
        past_n_runs=chart_form.cleaned_data.get("past_runs"),
        include_hidden=bool(chart_form.cleaned_data.get("include_hidden") or False),
    )
    explore_modal_dsl = _explore_modal_dsl_text(
        player_id=str(player.id),
        scope=explore_modal_scope,
    )

    context = {
        "import_form": import_form,
        "chart_form": chart_form,
        "comparison_form": comparison_form,
        "comparison_result": comparison_result,
        "comparison_scope_warning": comparison_scope_warning,
        "compare_scope_tier_options": tier_options,
        "compare_scope_preset_options": preset_options,
        "compare_scope_tournament_options": tournament_options,
        "compare_scope_patch_options": patch_options,
        "compare_scope_run_map_json": compare_run_map_json,
        "advice_items": advice_items,
        "snapshot_id": snapshot_id,
        "advice_snapshot_a": advice_snapshot_a,
        "advice_snapshot_b": advice_snapshot_b,
        "advice_mode": advice_mode,
        "goal_intent": goal_intent,
        "goal_label": goal_label,
        "goal_weight_coins_per_hour": goal_weights.coins_per_hour,
        "goal_weight_coins_per_wave": goal_weights.coins_per_wave,
        "goal_weight_waves_reached": goal_weights.waves_reached,
        "chart_builder_form": chart_builder_form,
        "chart_builder_errors": builder_errors,
        "chart_snapshots": ChartSnapshot.objects.filter(player=player, target="charts").order_by("-created_at"),
        "favorite_charts": favorite_charts,
        "available_favorite_charts": available_favorite_charts,
        "favorite_chart_ids_json": favorite_chart_ids_json,
        "chart_builder_saved_configs": saved_chart_builder_configs,
        "chart_builder_saved_configs_json": saved_chart_builder_configs_json,
        "chart_builder_metric_meta_json": json.dumps(
            {
                spec.key: {
                    "unit": spec.unit,
                    "category": str(spec.category),
                    "supports_rolling_avg": ("moving_average" in spec.allowed_transforms),
                    "default_aggregation": spec.aggregation,
                    "allowed_aggregations": list(allowed_chart_builder_aggregations(spec)),
                }
                for spec in DEFAULT_REGISTRY.list()
            }
        ),
        "chart_panels": chart_panels,
        "chart_panels_json": chart_panels_json,
        "chart_context_json": json.dumps(chart_context),
        "chart_empty_state": chart_empty_state,
        "scope_summary": scope_summary,
        "why_panel": why_panel,
        "explore_modal": {
            "start_date": chart_form.cleaned_data.get("start_date"),
            "end_date": chart_form.cleaned_data.get("end_date"),
            "tier": chart_form.cleaned_data.get("tier"),
            "preset_id": getattr(chart_form.cleaned_data.get("preset"), "id", None),
            "snapshot_id": getattr(chart_form.cleaned_data.get("context_snapshot"), "id", None),
            "past_n_runs": chart_form.cleaned_data.get("past_runs"),
        },
        "explore_modal_dsl": explore_modal_dsl,
        "event_window_start": chart_form.cleaned_data.get("start_date"),
        "event_window_end": chart_form.cleaned_data.get("end_date"),
        "walkthrough_enabled": walkthrough_enabled,
        "walkthrough_changelog_url": WALKTHROUGH_CHANGELOG_URL,
        "battle_report_special_run_options_json": json.dumps(
            _battle_report_special_run_options_payload()
        ),
    }
    return render(request, "core/dashboard.html", context)


def _landing_page_demo_chart_payload() -> dict[str, object] | None:
    """Return a demo chart payload for the landing page.

    Returns:
        Chart.js payload dictionary or None when no demo data is available.
    """

    config = CHART_CONFIG_BY_ID.get("coins_earned")
    if config is None:
        return None
    demo_player = get_demo_player()
    runs = _with_effective_battle_date(
        BattleReport.objects.filter(player=demo_player).select_related(
            "run_progress",
            "run_progress__preset",
            "derived_metrics",
        )
    ).order_by("effective_battle_date")
    run_numbers_by_report_id = _run_numbers_by_report_id(player=demo_player)
    rendered = render_charts(
        configs=(config,),
        records=runs,
        registry=DEFAULT_REGISTRY,
        granularity="daily",
        moving_average_window=None,
        entity_selections={"uw": None, "guardian": None, "bot": None},
        patch_boundaries=tuple(PatchBoundary.objects.values_list("boundary_date", flat=True)),
        run_numbers_by_report_id=run_numbers_by_report_id,
    )
    if not rendered:
        return None
    entry = rendered[0]
    if not entry.data.get("labels"):
        return None
    return {
        "chart_type": entry.config.chart_type,
        "labels": entry.data["labels"],
        "datasets": entry.data["datasets"],
    }


def getting_started(request: HttpRequest) -> HttpResponse:
    """Render the public landing page and onboarding summary."""

    has_imported_runs = False
    if request.user.is_authenticated:
        player = _request_player(request)
        has_imported_runs = BattleReport.objects.filter(player=player).exists()
    demo_chart_payload = _landing_page_demo_chart_payload()
    changelog_summary = latest_changelog_summary(max_items=3)
    return render(
        request,
        "core/getting_started.html",
        {
            "has_imported_runs": has_imported_runs,
            "demo_chart_json": json.dumps(demo_chart_payload) if demo_chart_payload else None,
            "changelog_summary": changelog_summary,
            "changelog_url": getattr(settings, "CHANGELOG_GITHUB_URL", ""),
        },
    )


@login_required
def export_derived_metrics_csv(request: HttpRequest) -> HttpResponse:
    """Export derived chart datasets as a CSV snapshot.

    The export is scoped to the active player (or demo player when demo mode is enabled),
    and includes only datasets marked as derived by the chart renderer.
    """

    player = _request_player(request)
    chart_form = ChartContextForm(request.GET, player=player, today=date.today())
    chart_form.is_valid()
    runs = _filtered_runs(chart_form, player=player)

    selected_chart_ids = tuple(chart_form.cleaned_data.get("charts") or ())
    selected_configs = tuple(
        CHART_CONFIG_BY_ID[chart_id] for chart_id in selected_chart_ids if chart_id in CHART_CONFIG_BY_ID
    )
    rendered = render_charts(
        configs=selected_configs,
        records=runs,
        registry=DEFAULT_REGISTRY,
        granularity=str(chart_form.cleaned_data.get("granularity") or "daily"),
        moving_average_window=chart_form.cleaned_data.get("moving_average_window"),
        entity_selections={
            "uw": getattr(chart_form.cleaned_data.get("ultimate_weapon"), "name", None),
            "guardian": getattr(chart_form.cleaned_data.get("guardian_chip"), "name", None),
            "bot": getattr(chart_form.cleaned_data.get("bot"), "name", None),
        },
        patch_boundaries=tuple(PatchBoundary.objects.values_list("boundary_date", flat=True)),
        run_numbers_by_report_id=_run_numbers_by_report_id(player=player),
    )

    columns: list[tuple[str, dict[str, float | None]]] = []
    all_labels: set[str] = set()
    for entry in rendered:
        labels = list(entry.data.get("labels") or [])
        datasets = list(entry.data.get("datasets") or [])
        for dataset in datasets:
            if dataset.get("metricKind") != "derived":
                continue
            series = list(dataset.get("data") or [])
            label_to_value: dict[str, float | None] = {}
            for idx, label in enumerate(labels):
                value = series[idx] if idx < len(series) else None
                if isinstance(value, (int, float)):
                    label_to_value[label] = float(value)
                else:
                    label_to_value[label] = None
            header = f"{entry.config.id}:{dataset.get('label') or entry.config.title}"
            columns.append((header, label_to_value))
            all_labels.update(label_to_value.keys())

    if not columns:
        return HttpResponse(
            "No derived metrics are selected for export. Select at least one derived chart and try again.\n",
            content_type="text/plain; charset=utf-8",
            status=400,
        )

    ordered_labels = sorted(all_labels)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["date", *[name for name, _mapping in columns]])
    for label in ordered_labels:
        row: list[str] = [label]
        for _name, mapping in columns:
            value = mapping.get(label)
            row.append("" if value is None else str(value))
        writer.writerow(row)

    response = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="theTowerStats-derived-metrics.csv"'
    return response


def _exclude_special_runs(runs: QuerySet[BattleReport], *, include_tournaments: bool, include_dissonance: bool) -> QuerySet[BattleReport]:
    """Apply the default tournament and Dissonance exclusions to a queryset.

    Args:
        runs: BattleReport queryset already scoped to a player.
        include_tournaments: Whether tournament runs should remain in scope.
        include_dissonance: Whether only Dissonance runs should remain in scope.

    Returns:
        Filtered BattleReport queryset.
    """

    if include_dissonance:
        return runs.filter(run_progress__is_dissonance=True)
    exclusions = Q(run_progress__tier__isnull=True) | Q(run_progress__is_dissonance=True)
    if not include_tournaments:
        exclusions |= Q(run_progress__is_tournament=True)
    return runs.exclude(exclusions)


def _dissonance_label(dissonance_type: str | None) -> str:
    """Return the display label for a Dissonance type key."""

    choices = dict(DISSONANCE_TYPE_CHOICES)
    return choices.get(str(dissonance_type or ""), "Dissonance")


def _goal_weights_from_query(*, goal_intent: str, query: QueryDict) -> tuple[str, GoalWeights]:
    """Return the effective goal label and weights from GET parameters.

    Args:
        goal_intent: Selected goal preset key.
        query: QueryDict containing optional weight override values.

    Returns:
        Tuple of (goal_label, GoalWeights) using defaults and user overrides.
    """

    presets: dict[str, tuple[str, GoalWeights]] = {
        "economy": ("Economy / Farming", GoalWeights(coins_per_hour=1.0, coins_per_wave=0.5, waves_reached=0.25)),
        "progression": ("Progression / Wave Push", GoalWeights(coins_per_hour=0.25, coins_per_wave=0.25, waves_reached=1.0)),
        "hybrid": ("Hybrid", GoalWeights(coins_per_hour=0.75, coins_per_wave=0.5, waves_reached=0.75)),
    }
    label, weights = presets.get(goal_intent, presets["hybrid"])

    def override_float(name: str, current: float) -> float:
        """Parse a float override from the query string."""

        raw = (query.get(name) or "").strip()
        if raw == "":
            return current
        try:
            return float(raw)
        except (TypeError, ValueError):
            return current

    return (
        label,
        GoalWeights(
            coins_per_hour=override_float("goal_weight_coins_per_hour", weights.coins_per_hour),
            coins_per_wave=override_float("goal_weight_coins_per_wave", weights.coins_per_wave),
            waves_reached=override_float("goal_weight_waves_reached", weights.waves_reached),
        ),
    )


def _metric_average_sample(*, runs: QuerySet[BattleReport], metric_key: str) -> tuple[int, float | None]:
    """Return non-null count and average for a selected metric key.

    Args:
        runs: Filtered BattleReport queryset for a scope.
        metric_key: Metric key registered in the analysis engine.

    Returns:
        Tuple of (count, average) based on non-null metric values.
    """

    series = analyze_metric_series(runs, metric_key=metric_key)
    values = [point.value for point in series.points if point.value is not None]
    if not values:
        return 0, None
    return len(values), sum(values) / len(values)


def _build_goal_weighted_advice(
    *,
    player: Player,
    runs_current: QuerySet[BattleReport],
    snapshot_a_id: str,
    snapshot_b_id: str | None,
    mode: str,
    goal_label: str,
    weights: GoalWeights,
) -> tuple[AdviceItem, ...]:
    """Build goal-aware advice comparing a baseline snapshot to another scope.

    Args:
        player: Active Player owning the snapshots.
        runs_current: QuerySet already filtered by the current dashboard filters.
        snapshot_a_id: Snapshot id used as the baseline scope.
        snapshot_b_id: Optional snapshot id used as the comparison scope.
        mode: Either "snapshot_vs_current" or "snapshot_vs_snapshot".
        goal_label: User-selected goal label for framing.
        weights: User-controlled weights for percent-change scoring.

    Returns:
        A tuple of AdviceItem values (0–1).
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

    comparison_label = "Current filters"
    comparison_runs = runs_current
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

    baseline_cph_count, baseline_cph = _metric_average_sample(runs=baseline_runs, metric_key="coins_per_hour")
    baseline_cpw_count, baseline_cpw = _metric_average_sample(runs=baseline_runs, metric_key="coins_per_wave")
    baseline_waves_count, baseline_waves = _metric_average_sample(runs=baseline_runs, metric_key="waves_reached")

    comparison_cph_count, comparison_cph = _metric_average_sample(runs=comparison_runs, metric_key="coins_per_hour")
    comparison_cpw_count, comparison_cpw = _metric_average_sample(runs=comparison_runs, metric_key="coins_per_wave")
    comparison_waves_count, comparison_waves = _metric_average_sample(runs=comparison_runs, metric_key="waves_reached")

    return generate_goal_weighted_advice(
        goal_label=goal_label,
        baseline=GoalScopeSample(
            label=snapshot_a.name,
            runs_coins_per_hour=baseline_cph_count,
            runs_coins_per_wave=baseline_cpw_count,
            runs_waves_reached=baseline_waves_count,
            coins_per_hour=baseline_cph,
            coins_per_wave=baseline_cpw,
            waves_reached=baseline_waves,
        ),
        comparison=GoalScopeSample(
            label=comparison_label,
            runs_coins_per_hour=comparison_cph_count,
            runs_coins_per_wave=comparison_cpw_count,
            runs_waves_reached=comparison_waves_count,
            coins_per_hour=comparison_cph,
            coins_per_wave=comparison_cpw,
            waves_reached=comparison_waves,
        ),
        weights=weights,
    )

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

    runs = _with_effective_battle_date(
        BattleReport.objects.filter(player=player).select_related(
            "run_progress",
            "run_progress__preset",
            "derived_metrics",
        )
    ).order_by("effective_battle_date")
    force_tournaments = bool(context.tournament_filter)
    runs = _exclude_special_runs(
        runs,
        include_tournaments=bool(context.include_tournaments or force_tournaments),
        include_dissonance=bool(context.include_dissonance),
    )
    if not context.include_hidden:
        runs = runs.filter(is_hidden=False)
    if context.start_date:
        runs = runs.filter(effective_battle_date__date__gte=context.start_date)
    if context.end_date:
        runs = runs.filter(effective_battle_date__date__lte=context.end_date)
    if context.tier:
        runs = runs.filter(run_progress__tier=context.tier)
    if context.preset_id:
        runs = runs.filter(run_progress__preset_id=context.preset_id)
    if context.excluded_preset_ids:
        runs = runs.exclude(run_progress__preset_id__in=context.excluded_preset_ids)
    if context.patch_boundaries:
        runs = _apply_patch_boundary_filters(
            runs,
            boundary_dates=context.patch_boundaries,
        )
    runs = _apply_tournament_filter(runs, tournament_filter=context.tournament_filter)
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


@dataclass(frozen=True, slots=True)
class BattleHistoryColumn:
    """Battle History column definition used for rendering and preferences."""

    key: str
    label: str
    sort_key: str | None = None
    default_visible: bool = False


def _battle_history_columns() -> tuple[BattleHistoryColumn, ...]:
    """Return the supported Battle History columns in display order."""

    return (
        BattleHistoryColumn("run_number", "Run #", default_visible=True),
        BattleHistoryColumn("battle_date", "Battle date", sort_key="run_progress__battle_date", default_visible=True),
        BattleHistoryColumn("tier", "Tier", sort_key="run_progress__tier", default_visible=True),
        BattleHistoryColumn("tournament", "Tournament", sort_key="run_progress__is_tournament"),
        BattleHistoryColumn("hidden", "Hidden", sort_key="is_hidden", default_visible=True),
        BattleHistoryColumn("wave", "Highest wave", sort_key="run_progress__wave", default_visible=True),
        BattleHistoryColumn("real_time", "Real time", sort_key="run_progress__real_time_seconds"),
        BattleHistoryColumn("killed_by", "Killed by", sort_key="run_progress__killed_by", default_visible=True),
        BattleHistoryColumn("coins_earned", "Coins earned", sort_key="run_progress__coins_earned", default_visible=True),
        BattleHistoryColumn("coins_per_hour", "Coins/real hour", sort_key="coins_per_hour", default_visible=True),
        BattleHistoryColumn("cash_earned", "Cash earned", sort_key="run_progress__cash_earned", default_visible=True),
        BattleHistoryColumn("interest_earned", "Interest earned", sort_key="run_progress__interest_earned", default_visible=True),
        BattleHistoryColumn("gem_blocks", "Gem blocks", sort_key="run_progress__gem_blocks_tapped", default_visible=True),
        BattleHistoryColumn("cells_earned", "Cells earned", sort_key="run_progress__cells_earned", default_visible=True),
        BattleHistoryColumn("reroll_shards", "Reroll shards", sort_key="run_progress__reroll_shards_earned", default_visible=True),
        BattleHistoryColumn(
            "recovery_packages",
            "Recovery packages",
            sort_key="derived_metrics__values__recovery_packages",
        ),
        BattleHistoryColumn("preset", "Preset", sort_key="run_progress__preset__name", default_visible=True),
    )


def _battle_history_visible_columns(
    *,
    player: Player,
    columns: tuple[BattleHistoryColumn, ...],
) -> tuple[str, ...]:
    """Return the active column keys for a player's Battle History table."""

    default_keys = tuple(col.key for col in columns if col.default_visible)
    stored = BattleHistoryColumnPreference.objects.filter(player=player).first()
    if stored is None:
        return default_keys
    selected = [key for key in stored.columns if key in {col.key for col in columns}]
    return tuple(selected) if selected else default_keys


def _run_numbers_by_report_id(*, player: Player) -> dict[int, int]:
    """Return chronological run numbers for a player's Battle Reports."""

    runs = _with_effective_battle_date(
        BattleReport.objects.filter(player=player).select_related("run_progress")
    ).order_by("effective_battle_date", "id")
    return {run.id: idx + 1 for idx, run in enumerate(runs)}


def _format_real_time(seconds: int | None) -> str:
    """Render a human-friendly real-time duration from seconds."""

    if seconds is None:
        return "—"
    remaining = max(int(seconds), 0)
    hours, remaining = divmod(remaining, 3600)
    minutes, secs = divmod(remaining, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


_COMPACT_COUNT_SUFFIXES: tuple[tuple[int, str], ...] = (
    (1_000_000_000_000_000_000, "Q"),
    (1_000_000_000_000_000, "q"),
    (1_000_000_000_000, "T"),
    (1_000_000_000, "B"),
    (1_000_000, "M"),
    (1_000, "k"),
)


def _format_compact_count(value: int | None) -> str | None:
    """Format a count value using compact lowercase suffixes."""

    if value is None:
        return None
    abs_value = abs(int(value))
    for threshold, suffix in _COMPACT_COUNT_SUFFIXES:
        if abs_value >= threshold:
            return f"{value / threshold:.2f}{suffix}"
    return f"{value}"


def _order_battle_history_runs(
    *, runs: QuerySet[BattleReport], sort_key: str
) -> QuerySet[BattleReport] | list[BattleReport]:
    """Return ordered BattleReport rows for Battle History.

    This helper keeps ordering logic out of the view body and ensures that
    computed ordering (coins/hour) is derived via the analysis engine's rate
    helper rather than view-layer arithmetic.

    Args:
        runs: Filtered BattleReport queryset, already scoped to the requesting player.
        sort_key: Validated sort key from the BattleHistoryFilterForm.

    Returns:
        Either a queryset (for database-orderable fields) or a sorted list
        (for computed ordering like coins/hour).
    """

    ordering = [sort_key]
    if sort_key.lstrip("-") != "parsed_at":
        ordering.append("-parsed_at")

    if sort_key.lstrip("-") != "coins_per_hour":
        return runs.order_by(*ordering)

    descending = sort_key.startswith("-")
    evaluated = list(runs.order_by("-parsed_at", "-id"))

    coins_per_hour_by_id: dict[int, float | None] = {}
    for run in evaluated:
        progress = getattr(run, "run_progress", None)
        if progress is None:
            coins_per_hour_by_id[run.id] = None
            continue
        coins = getattr(progress, "coins_earned", None)
        real_time_seconds = getattr(progress, "real_time_seconds", None)
        if coins is None or real_time_seconds is None:
            coins_per_hour_by_id[run.id] = None
            continue
        coins_per_hour_by_id[run.id] = coins_per_hour_rate(coins=coins, real_time_seconds=real_time_seconds)

    def _sort_tuple(run: BattleReport) -> tuple[bool, float, float, int]:
        metric = coins_per_hour_by_id.get(run.id)
        metric_value = metric or 0.0
        # Always keep missing metrics last, regardless of ascending/descending.
        missing = metric is None
        primary = -metric_value if descending else metric_value
        return (missing, primary, -run.parsed_at.timestamp(), -run.id)

    return sorted(evaluated, key=_sort_tuple)


def _ordered_battle_report_ids(runs: QuerySet[BattleReport] | list[BattleReport]) -> list[int]:
    """Return BattleReport ids in the same order as the Battle History list."""

    if isinstance(runs, QuerySet):
        return list(runs.values_list("id", flat=True))
    return [run.id for run in runs]


def _battle_report_modal_metrics(progress: BattleReportProgress | None) -> list[dict[str, object]]:
    """Build metric rows for the Battle Report modal with optional chart links."""

    if progress is None:
        return []

    chart_links = {
        "coins_earned": "coins_earned",
        "coins_per_hour": "coins_per_hour",
        "cash_earned": "cash_earned",
        "interest_earned": "cash_by_source",
        "cells_earned": "cells_earned",
        "reroll_shards_earned": "reroll_shards_earned",
    }

    def _format_int(value: int | None) -> str | None:
        if value is None:
            return None
        return f"{value:,}"

    coins_per_hour_value: str | None = None
    coins_per_hour_numeric: float | None = None
    if progress.coins_earned is not None and progress.real_time_seconds:
        coins_per_hour_numeric = coins_per_hour_rate(
            coins=progress.coins_earned,
            real_time_seconds=progress.real_time_seconds,
        )
        coins_per_hour_value = f"{coins_per_hour_numeric:,.2f}"

    def _display(value: str | None) -> str:
        if value is None or value == "":
            return "—"
        return value

    metrics: list[dict[str, object]] = [
        {
            "key": "coins_earned",
            "label": "Coins earned",
            "value": _display(progress.coins_earned_raw),
            "numeric_value": progress.coins_earned,
            "unit": "coins",
            "chart_id": chart_links.get("coins_earned"),
        },
        {
            "key": "coins_per_hour",
            "label": "Coins per real hour",
            "value": _display(coins_per_hour_value),
            "numeric_value": coins_per_hour_numeric,
            "unit": "coins/hour",
            "chart_id": chart_links.get("coins_per_hour"),
        },
        {
            "key": "cash_earned",
            "label": "Cash earned",
            "value": _display(progress.cash_earned_raw),
            "numeric_value": progress.cash_earned,
            "unit": "cash",
            "chart_id": chart_links.get("cash_earned"),
        },
        {
            "key": "interest_earned",
            "label": "Interest earned",
            "value": _display(progress.interest_earned_raw),
            "numeric_value": progress.interest_earned,
            "unit": "cash",
            "chart_id": chart_links.get("interest_earned"),
        },
        {
            "key": "gem_blocks_tapped",
            "label": "Gem blocks",
            "value": _display(_format_int(progress.gem_blocks_tapped)),
            "numeric_value": progress.gem_blocks_tapped,
            "unit": "",
            "chart_id": None,
        },
        {
            "key": "cells_earned",
            "label": "Cells earned",
            "value": _display(_format_compact_count(progress.cells_earned)),
            "numeric_value": progress.cells_earned,
            "unit": "cells",
            "chart_id": chart_links.get("cells_earned"),
        },
        {
            "key": "reroll_shards_earned",
            "label": "Reroll shards",
            "value": _display(_format_int(progress.reroll_shards_earned)),
            "numeric_value": progress.reroll_shards_earned,
            "unit": "shards",
            "chart_id": chart_links.get("reroll_shards_earned"),
        },
    ]

    if progress.is_tournament or progress.tournament_rank:
        rank_value = progress.tournament_rank.title() if progress.tournament_rank else None
        metrics.append(
            {
                "key": "tournament_rank",
                "label": "Tournament rank",
                "value": _display(rank_value),
                "numeric_value": None,
                "unit": "",
                "chart_id": None,
            }
        )

    if progress.tier is not None:
        levels_snapshot = {
            **{key: 1 for key in DISSONANCE_TYPE_KEYS},
            **(
                progress.dissonance_levels_snapshot
                if isinstance(progress.dissonance_levels_snapshot, dict)
                else {}
            ),
        }
        for key in DISSONANCE_TYPE_KEYS:
            level = int(levels_snapshot.get(key) or 1)
            label = _dissonance_label(key)
            multiplier = effective_multiplier(multiplier_level=level, wave=progress.wave)
            metrics.append(
                {
                    "key": f"dissonance_{key}",
                    "label": f"Dissonance {label}",
                    "value": f"x{multiplier:.4f}",
                    "numeric_value": float(multiplier),
                    "unit": "multiplier",
                    "chart_id": None,
                }
            )

    return metrics


def _battle_report_special_run_options_payload() -> dict[str, object]:
    """Return special-run option metadata for the Battle Report modal."""

    return {
        "special_runs": [
            {"value": str(value), "label": str(label)}
            for value, label in (
                ("", "None"),
                ("tournament", "Tournament"),
                ("dissonance", "Dissonance"),
            )
        ],
        "details": {
            "tournament": [
                {"value": str(value), "label": str(label)}
                for value, label in TOURNAMENT_RANK_CHOICES
            ],
            "dissonance": [
                {"value": str(value), "label": str(label)}
                for value, label in DISSONANCE_TYPE_CHOICES
            ],
        },
    }


def _battle_report_modal_payload(*, player: Player, report: BattleReport) -> dict[str, object]:
    """Serialize one Battle Report for the modal API response."""

    run_numbers = _run_numbers_by_report_id(player=player)
    progress = getattr(report, "run_progress", None)
    battle_date_fallback = battle_date_is_fallback(report.raw_text or "")
    special_run = ""
    special_run_detail = ""
    if progress is not None:
        if progress.is_tournament:
            special_run = "tournament"
            special_run_detail = str(progress.tournament_rank or "")
        elif progress.is_dissonance:
            special_run = "dissonance"
            special_run_detail = str(progress.dissonance_type or "")

    return {
        "id": report.id,
        "run_number": run_numbers.get(report.id),
        "raw_text": report.raw_text,
        "battle_date": progress.battle_date.isoformat() if progress and progress.battle_date else None,
        "battle_date_fallback": battle_date_fallback,
        "parsed_at": report.parsed_at.isoformat() if report.parsed_at else None,
        "tier": progress.tier if progress else None,
        "is_tournament": bool(progress.is_tournament) if progress else False,
        "tournament_rank": progress.tournament_rank if progress else None,
        "tournament_rank_label": (
            dict(TOURNAMENT_RANK_CHOICES).get(str(progress.tournament_rank or ""), "")
            if progress
            else ""
        ),
        "is_dissonance": bool(progress.is_dissonance) if progress else False,
        "dissonance_type": progress.dissonance_type if progress else None,
        "dissonance_type_label": _dissonance_label(progress.dissonance_type) if progress else "",
        "special_run": special_run,
        "special_run_detail": special_run_detail,
        "metrics": _battle_report_modal_metrics(progress),
    }


def _favorite_chart_ids(*, player: Player, available_ids: set[str]) -> list[str]:
    """Return ordered favorite chart ids scoped to the player."""

    preferences = ChartDashboardPreference.objects.filter(player=player).first()
    if preferences is None:
        return []
    return [cid for cid in preferences.favorite_chart_ids if str(cid) in available_ids]


def _chart_builder_payload(builder_form: ChartBuilderForm) -> dict[str, object]:
    """Serialize Chart Builder selections for saved configs."""

    if not builder_form.is_valid():
        raise ValueError("ChartBuilderForm must be valid before serialization.")

    run_a = builder_form.cleaned_data.get("run_a")
    run_b = builder_form.cleaned_data.get("run_b")
    window_a_start = builder_form.cleaned_data.get("window_a_start")
    window_a_end = builder_form.cleaned_data.get("window_a_end")
    window_b_start = builder_form.cleaned_data.get("window_b_start")
    window_b_end = builder_form.cleaned_data.get("window_b_end")

    return {
        "metric_keys": list(builder_form.cleaned_data.get("metric_keys") or []),
        "chart_type": builder_form.cleaned_data.get("chart_type"),
        "x_axis": builder_form.cleaned_data.get("x_axis"),
        "group_by": builder_form.cleaned_data.get("group_by"),
        "comparison": builder_form.cleaned_data.get("comparison"),
        "smoothing": builder_form.cleaned_data.get("smoothing"),
        "aggregation": builder_form.cleaned_data.get("aggregation") or "",
        "run_a": getattr(run_a, "id", None) or "",
        "run_b": getattr(run_b, "id", None) or "",
        "window_a_start": window_a_start.isoformat() if window_a_start else "",
        "window_a_end": window_a_end.isoformat() if window_a_end else "",
        "window_b_start": window_b_start.isoformat() if window_b_start else "",
        "window_b_end": window_b_end.isoformat() if window_b_end else "",
    }


FARMING_EFFICIENCY_QUERY_NAME = "Farming Efficiency by Tier"
FARMING_MIN_RUNS = 3
FARMING_PLATEAU_THRESHOLD = 0.05
FARMING_VARIANCE_THRESHOLD = 0.4


@dataclass(frozen=True, slots=True)
class FarmingTierStats:
    """Per-tier statistics for farming efficiency summaries."""

    tier: int
    avg: float
    count: int
    cv: float | None


class ExploreResultRowPayload(TypedDict):
    """Serialized Explore result row payload for templates."""

    breakdown: tuple[str, ...]
    value: float | None
    values: list[float | None]
    sample_count: int
    sample_counts: list[int]
    sample_count_mismatch: bool
    metric_cells: list[dict[str, object]]
    run_id: int | None


def farming_efficiency_template_dsl() -> str:
    """Return the DSL text for the default Farming Efficiency template."""

    lines = [
        f'name "{FARMING_EFFICIENCY_QUERY_NAME}"',
        "scope date [date:YYYY-MM-DD]..[date:YYYY-MM-DD]",
        "scope tier all not tournament",
        "scope preset [preset:—]",
        "scope snapshot [snapshot:—]",
        "scope past_n_runs [runs:—]",
        "breakdown by tier",
        "metric coins_per_hour avg",
        "# Optional secondary metrics (avg):",
        "# metric coins_earned avg",
        "# metric real_time_hours avg",
        "# metric cells_earned avg",
        "# metric reroll_shards_earned avg",
        "# metric waves_reached avg",
        "output table",
    ]
    return "\n".join(lines)


def _explore_metric_value(record: BattleReport, *, metric_key: str) -> float | None:
    """Return a computed Explore metric value for a BattleReport record."""

    progress = getattr(record, "run_progress", record)
    coins = getattr(progress, "coins_earned", None)
    cash = getattr(progress, "cash_earned", None)
    interest_earned = getattr(progress, "interest_earned", None)
    cells = getattr(progress, "cells_earned", None)
    reroll_shards = getattr(progress, "reroll_shards_earned", None)
    wave = getattr(progress, "wave", None)
    real_time_seconds = getattr(progress, "real_time_seconds", None)

    value, _used, _assumptions = compute_metric_value(
        metric_key,
        record=record,
        coins=coins,
        cash=cash,
        interest_earned=interest_earned,
        cells=cells,
        reroll_shards=reroll_shards,
        wave=wave,
        real_time_seconds=real_time_seconds,
        context=None,
        entity_type=None,
        entity_name=None,
        config=MetricComputeConfig(monte_carlo=None),
    )
    return value


def _is_farming_efficiency_query(query: ExploreQuery) -> bool:
    """Return True when a query matches the farming efficiency template."""

    breakdowns = tuple(sorted(query.breakdowns, key=lambda entry: entry.order))
    return (
        bool(query.metrics)
        and query.metrics[0].key == "coins_per_hour"
        and query.metrics[0].aggregation == "avg"
        and query.visualization_hint == "table"
        and len(breakdowns) == 1
        and breakdowns[0].dimension == "tier"
    )


def _farming_efficiency_analysis(
    runs: Iterable[BattleReport],
    *,
    metric_key: str,
    min_runs: int,
    plateau_threshold: float,
    variance_threshold: float,
) -> dict[str, object]:
    """Return summary, warnings, and rows for farming efficiency output."""

    tier_values: dict[int, list[float]] = {}
    for run in runs:
        progress = getattr(run, "run_progress", run)
        tier = getattr(progress, "tier", None)
        if tier is None:
            continue
        value = _explore_metric_value(run, metric_key=metric_key)
        if value is None:
            continue
        tier_values.setdefault(int(tier), []).append(float(value))

    tiers = sorted(tier_values.keys())
    rows: list[dict[str, object]] = []
    warnings: list[str] = []
    if not tiers:
        return {
            "rows": (),
            "warnings": (),
            "best_tier": None,
            "plateau_tier": None,
            "insufficient": True,
        }

    tier_stats: list[FarmingTierStats] = []
    for tier in tiers:
        values = tier_values[tier]
        count = len(values)
        avg_value = sum(values) / count if count else 0.0
        variance = sum((value - avg_value) ** 2 for value in values) / count if count else 0.0
        stddev = math.sqrt(variance)
        cv = (stddev / avg_value) if avg_value else None
        tier_stats.append(FarmingTierStats(tier=tier, avg=avg_value, count=count, cv=cv))

    low_sample = [stat for stat in tier_stats if stat.count < min_runs]
    if low_sample:
        low_labels = ", ".join(
            f"Tier {stat.tier} ({stat.count} runs)" for stat in low_sample
        )
        warnings.append(f"Low sample size: {low_labels}. Minimum is {min_runs} runs.")

    high_variance = [stat for stat in tier_stats if stat.cv is not None and stat.cv > variance_threshold]
    if high_variance:
        variance_labels = ", ".join(
            f"Tier {stat.tier} (CV {stat.cv:.2f})" for stat in high_variance
        )
        warnings.append(
            f"High variance: {variance_labels}. Threshold is {variance_threshold:.0%}."
        )

    missing_tiers = [
        tier for tier in range(tiers[0], tiers[-1] + 1) if tier not in tier_values
    ]
    if missing_tiers:
        gap_labels = ", ".join(f"Tier {tier}" for tier in missing_tiers)
        warnings.append(f"Tier gaps detected: missing {gap_labels}.")

    eligible = [stat for stat in tier_stats if stat.count >= min_runs]
    best_tier = None
    if eligible:
        best_tier = max(eligible, key=lambda entry: entry.avg).tier

    plateau_tier = None
    for idx, current in enumerate(eligible[:-1]):
        next_stat = eligible[idx + 1]
        current_avg = current.avg
        next_avg = next_stat.avg
        plateau_delta_value = next_avg - current_avg
        plateau_delta_percent = (plateau_delta_value / current_avg) if current_avg else None
        if plateau_delta_value < 0 or (
            plateau_delta_percent is not None and plateau_delta_percent < plateau_threshold
        ):
            plateau_tier = next_stat.tier
            break

    previous_avg: float | None = None
    for stat in tier_stats:
        tier = stat.tier
        avg_value = stat.avg
        delta_value: float | None = None
        delta_percent: float | None = None
        delta_prefix = ""
        delta_percent_display: str | None = None
        if previous_avg is not None:
            delta_value = avg_value - previous_avg
            delta_prefix = "+" if delta_value > 0 else ""
            if previous_avg:
                delta_percent = (delta_value / previous_avg) * 100.0
                delta_percent_display = f"{delta_percent:+.1f}%"

        rows.append(
            {
                "tier": tier,
                "tier_label": f"Tier {tier}",
                "avg": avg_value,
                "run_count": stat.count,
                "delta_value": delta_value,
                "delta_prefix": delta_prefix,
                "delta_percent_display": delta_percent_display,
                "is_best": best_tier == tier if best_tier is not None else False,
                "is_plateau": plateau_tier == tier if plateau_tier is not None else False,
            }
        )

        previous_avg = avg_value
    return {
        "rows": tuple(rows),
        "warnings": tuple(warnings),
        "best_tier": best_tier,
        "plateau_tier": plateau_tier,
        "insufficient": not bool(eligible),
    }


@login_required
def explore_dashboard(request: HttpRequest) -> HttpResponse:
    """Render the Explore dashboard for player-authored queries."""

    player = _request_player(request)
    if request.method == "POST" and demo_mode_enabled(request):
        return _reject_demo_write(request)
    if request.method == "POST" and request.POST.get("action") == "delete_explore_query":
        saved_id = request.POST.get("query_id")
        existing = (
            ExploreQueryModel.objects.filter(player=player, id=saved_id).first()
            if saved_id
            else None
        )
        if existing is None:
            messages.error(request, "Select a saved query to delete.")
        else:
            existing.delete()
            just_saved = request.session.get(_EXPLORE_JUST_SAVED_SESSION_KEY)
            if just_saved == existing.id:
                request.session.pop(_EXPLORE_JUST_SAVED_SESSION_KEY, None)
            messages.success(request, "Explore query deleted.")
        return safe_redirect(request, candidates=(), fallback=reverse("core:explore"))

    explore_registry = build_explore_metric_registry()
    saved_queries = ExploreQueryModel.objects.filter(player=player).order_by("name", "id")
    query_templates = ExploreQueryTemplate.objects.filter(is_active=True).order_by("name", "id")
    loaded_query: ExploreQueryModel | None = None
    loaded_payload: dict[str, object] | None = None
    loaded_template: ExploreQueryTemplate | None = None
    prefill_scope = _explore_prefill_scope_from_request(request.GET)
    if request.method == "GET" and request.GET.get("template_id"):
        try:
            template_id = int(request.GET.get("template_id") or 0)
        except ValueError:
            template_id = 0
        if template_id:
            loaded_template = query_templates.filter(id=template_id).first()
    if loaded_template is None and request.method == "GET" and request.GET.get("query_id"):
        try:
            query_id = int(request.GET.get("query_id") or 0)
        except ValueError:
            query_id = 0
        if query_id:
            loaded_query = saved_queries.filter(id=query_id).first()
            if loaded_query is not None:
                loaded_payload = dict(loaded_query.query or {})
    just_saved_id = None
    if request.method == "GET":
        just_saved_id = _consume_explore_just_saved_query_id(request)
    if request.method == "GET" and not request.GET.get("query_id") and just_saved_id:
        loaded_query = saved_queries.filter(id=just_saved_id).first()
        if loaded_query is not None:
            loaded_payload = dict(loaded_query.query or {})

    form_data: QueryDict | None = None
    initial: dict[str, object] = {}
    if loaded_payload:
        initial = _explore_form_initial_from_payload(loaded_payload)
        if loaded_query is not None:
            initial["query_id"] = loaded_query.id
    if not initial and request.method == "GET" and request.GET and not request.GET.get("run"):
        initial = _explore_form_initial_from_request(request.GET)
    dsl_input = request.POST.get("dsl_query") if request.method == "POST" else ""
    uses_dsl = bool(dsl_input and dsl_input.strip())
    if request.method == "POST" and not uses_dsl:
        form_data = request.POST
    elif request.method == "GET" and request.GET.get("run"):
        form_data = request.GET

    form = ExploreQueryForm(form_data, player=player, initial=initial)

    validation_errors: list[str] = []
    validation_warnings: list[str] = []
    results: dict[str, object] | None = None
    query_payload: dict[str, object] | None = None
    dsl_text = ""
    executed_query: ExploreQuery | None = None
    farming_summary: dict[str, object] | None = None
    autocomplete_payload = _explore_autocomplete_payload(
        registry=explore_registry,
        player=player,
    )

    if not form.is_bound and loaded_payload:
        loaded_query_data = _explore_query_from_payload(loaded_payload)
        validation = validate_explore_query(
            loaded_query_data,
            metric_registry=explore_registry,
            breakdown_registry=DEFAULT_BREAKDOWNS,
        )
        validation_errors.extend(validation.errors)
        validation_warnings.extend(validation.warnings)
        query_payload = loaded_payload
        if not validation.errors:
            results = _explore_execute_query(loaded_query_data, player=player, registry=explore_registry)
            executed_query = loaded_query_data
            if results["run_count"] == 0:
                validation_warnings.append("Empty scope: no runs match the current scope and filters.")
            if not results["rows"]:
                validation_warnings.append("Missing data: no matching metric values were found.")
            _append_explore_missing_warnings(results, validation_warnings)

        payload_dsl_text = _explore_payload_dsl_text(loaded_payload)
        dsl_text = payload_dsl_text or format_explore_dsl(loaded_query_data, default_scope=prefill_scope)

    if loaded_template is not None and not form.is_bound:
        dsl_text = loaded_template.dsl_text

    if uses_dsl:
        dsl_text = dsl_input
        parse_result = parse_explore_dsl(
            dsl_input,
            player_id=str(player.id),
            default_scope=prefill_scope,
        )
        validation_errors.extend(parse_result.errors)
        validation_warnings.extend(parse_result.warnings)
        if parse_result.query is not None and not parse_result.errors:
            validation = validate_explore_query(
                parse_result.query,
                metric_registry=explore_registry,
                breakdown_registry=DEFAULT_BREAKDOWNS,
            )
            validation_errors.extend(validation.errors)
            validation_warnings.extend(validation.warnings)
            query_payload = _explore_payload_with_dsl(
                build_query_payload(parse_result.query),
                dsl_input,
            )

            if not validation.errors:
                execution_query = parse_result.query
                if parse_result.query.visualization_hint == "kpi":
                    execution_query = ExploreQuery(
                        schema_version=parse_result.query.schema_version,
                        player_id=parse_result.query.player_id,
                        name=parse_result.query.name,
                        scope=parse_result.query.scope,
                        filters=parse_result.query.filters,
                        breakdowns=(),
                        metrics=parse_result.query.metrics,
                        visualization_hint=parse_result.query.visualization_hint,
                    )
                results = _explore_execute_query(
                    execution_query,
                    player=player,
                    registry=explore_registry,
                )
                executed_query = execution_query
                if results["run_count"] == 0:
                    validation_warnings.append(
                        "Empty scope: no runs match the current scope and filters."
                    )
                if not results["rows"]:
                    validation_warnings.append(
                        "Missing data: no matching metric values were found."
                    )
                _append_explore_missing_warnings(results, validation_warnings)

            if request.method == "POST" and request.POST.get("action") == "save_explore_query":
                if validation_errors:
                    messages.error(request, "Could not save query: validation failed.")
                else:
                    saved_id = request.POST.get("query_id")
                    existing = (
                        ExploreQueryModel.objects.filter(player=player, id=saved_id).first()
                        if saved_id
                        else None
                    )
                    name = parse_result.query.name
                    conflict = ExploreQueryModel.objects.filter(player=player, name=name)
                    if existing is not None:
                        conflict = conflict.exclude(id=existing.id)
                    conflict_existing = conflict.order_by("id").first()
                    if conflict_existing is not None and existing is not None:
                        messages.error(request, "A query with this name already exists.")
                    else:
                        if existing is None and conflict_existing is not None:
                            existing = conflict_existing
                        if existing is None:
                            existing = ExploreQueryModel(player=player, name=name)
                        existing.schema_version = SCHEMA_VERSION
                        existing.name = name
                        existing.query = query_payload or {}
                        existing.save()
                        messages.success(request, "Explore query saved.")
                        request.session[_EXPLORE_JUST_SAVED_SESSION_KEY] = existing.id
                        target = f"{reverse('core:explore')}?query_id={existing.id}"
                        return safe_redirect(
                            request,
                            candidates=[request.POST.get("next")],
                            fallback=target,
                        )

    if form.is_bound and form.is_valid():
        query = _explore_query_from_form(form, player=player)
        validation = validate_explore_query(
            query,
            metric_registry=explore_registry,
            breakdown_registry=DEFAULT_BREAKDOWNS,
        )
        validation_errors.extend(validation.errors)
        validation_warnings.extend(validation.warnings)
        formatted_dsl = format_explore_dsl(query, default_scope=prefill_scope)
        query_payload = _explore_payload_with_dsl(
            build_query_payload(query),
            formatted_dsl,
        )

        if not validation.errors:
            execution_query = query
            if query.visualization_hint == "kpi":
                execution_query = ExploreQuery(
                    schema_version=query.schema_version,
                    player_id=query.player_id,
                    name=query.name,
                    scope=query.scope,
                    filters=query.filters,
                    breakdowns=(),
                    metrics=query.metrics,
                    visualization_hint=query.visualization_hint,
                )
            results = _explore_execute_query(execution_query, player=player, registry=explore_registry)
            executed_query = execution_query
            if results["run_count"] == 0:
                validation_warnings.append("Empty scope: no runs match the current scope and filters.")
            if not results["rows"]:
                validation_warnings.append("Missing data: no matching metric values were found.")
            _append_explore_missing_warnings(results, validation_warnings)

        if request.method == "POST" and request.POST.get("action") == "save_explore_query":
            if validation.errors:
                messages.error(request, "Could not save query: validation failed.")
            else:
                saved_id = form.cleaned_data.get("query_id")
                existing = (
                    ExploreQueryModel.objects.filter(player=player, id=saved_id).first()
                    if saved_id
                    else None
                )
                name = query.name
                conflict = ExploreQueryModel.objects.filter(player=player, name=name)
                if existing is not None:
                    conflict = conflict.exclude(id=existing.id)
                conflict_existing = conflict.order_by("id").first()
                if conflict_existing is not None and existing is not None:
                    messages.error(request, "A query with this name already exists.")
                else:
                    if existing is None and conflict_existing is not None:
                        existing = conflict_existing
                    if existing is None:
                        existing = ExploreQueryModel(player=player, name=name)
                    existing.schema_version = SCHEMA_VERSION
                    existing.name = name
                    existing.query = query_payload or {}
                    existing.save()
                    messages.success(request, "Explore query saved.")
                    request.session[_EXPLORE_JUST_SAVED_SESSION_KEY] = existing.id
                    target = f"{reverse('core:explore')}?query_id={existing.id}"
                    return safe_redirect(request, candidates=[request.POST.get("next")], fallback=target)

        if not dsl_text:
            dsl_text = formatted_dsl

    if not dsl_text:
        default_metric = sorted(explore_registry.keys())[0]
        default_query = ExploreQuery(
            schema_version=SCHEMA_VERSION,
            player_id=str(player.id),
            name="New Explore Query",
            scope=prefill_scope,
            filters=(),
            breakdowns=(ExploreBreakdown(dimension="run", order=1),),
            metrics=(ExploreMetricSelection(key=default_metric, aggregation="sum"),),
            visualization_hint="table",
        )
        dsl_text = format_explore_dsl(default_query, default_scope=prefill_scope)

    if executed_query and results and _is_farming_efficiency_query(executed_query):
        farming_runs = _explore_runs_queryset(player=player)
        farming_runs = _apply_explore_scope(
            farming_runs,
            scope=executed_query.scope,
            snapshot_id=executed_query.scope.snapshot_id,
        )
        farming_runs = _apply_explore_filters(farming_runs, filters=executed_query.filters)
        farming_summary = _farming_efficiency_analysis(
            farming_runs,
            metric_key=executed_query.metrics[0].key if executed_query.metrics else "",
            min_runs=FARMING_MIN_RUNS,
            plateau_threshold=FARMING_PLATEAU_THRESHOLD,
            variance_threshold=FARMING_VARIANCE_THRESHOLD,
        )

    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            _explore_preview_payload(
                results,
                errors=validation_errors,
                warnings=validation_warnings,
            )
        )

    context = {
        "form": form,
        "saved_queries": saved_queries,
        "query_templates": query_templates,
        "loaded_query": loaded_query,
        "loaded_template_id": loaded_template.id if loaded_template is not None else "",
        "query_payload": query_payload,
        "explore_dsl_text": dsl_text,
        "explore_dsl_autocomplete": autocomplete_payload,
        "explore_results": results,
        "explore_errors": tuple(validation_errors),
        "explore_warnings": tuple(validation_warnings),
        "explore_farming": farming_summary,
        "collapse_query_templates": (
            request.method == "POST"
            and request.POST.get("action") == "run_explore_query"
            and not validation_errors
            and results is not None
        ),
    }
    return render(request, "core/explore.html", context)


def _explore_autocomplete_payload(
    *,
    registry: dict[str, ExploreMetricDefinition],
    player: Player,
) -> dict[str, list[dict[str, str]]]:
    """Build server-backed autocomplete payloads for Explore."""

    payload = build_explore_autocomplete(registry, DEFAULT_BREAKDOWNS)
    presets = Preset.objects.filter(player=player).order_by("name")
    payload["presets"] = [
        {
            "label": _explore_token_label(preset.name),
            "detail": f"Preset #{preset.id}",
            "type": "preset",
        }
        for preset in presets
    ]
    return payload


def _explore_token_label(value: str) -> str:
    """Return a DSL-safe label for a token."""

    token = value.strip()
    if not token:
        return token
    if " " in token or "," in token:
        return f"\"{token}\""
    return token


@login_required
def explore_autocomplete(request: HttpRequest) -> JsonResponse:
    """Return Explore DSL autocomplete payloads and validation output."""

    if request.method not in {"GET", "POST"}:
        return JsonResponse({"ok": False, "error": "Method not allowed."}, status=405)

    player = _request_player(request)
    explore_registry = build_explore_metric_registry()
    autocomplete = _explore_autocomplete_payload(registry=explore_registry, player=player)

    if request.method == "POST":
        dsl_text = str(request.POST.get("dsl") or "")
    else:
        dsl_text = str(request.GET.get("dsl") or "")

    validation: dict[str, list[str]] = {"errors": [], "warnings": []}
    if dsl_text.strip():
        prefill_scope = _explore_prefill_scope_from_request(request.GET)
        parse_result = parse_explore_dsl(
            dsl_text,
            player_id=str(player.id),
            default_scope=prefill_scope,
        )
        if parse_result.errors:
            validation["errors"] = list(parse_result.errors)
            validation["warnings"] = list(parse_result.warnings)
        elif parse_result.query is not None:
            result = validate_explore_query(
                parse_result.query,
                metric_registry=explore_registry,
                breakdown_registry=DEFAULT_BREAKDOWNS,
            )
            validation["errors"] = list(result.errors)
            validation["warnings"] = list(result.warnings)

    return JsonResponse({"ok": True, "autocomplete": autocomplete, "validation": validation})


def _explore_modal_dsl_text(*, player_id: str, scope: ExploreScope) -> str:
    """Return default DSL text for Explore modal launchers."""

    explore_registry = build_explore_metric_registry()
    default_metric = sorted(explore_registry.keys())[0]
    default_query = ExploreQuery(
        schema_version=SCHEMA_VERSION,
        player_id=player_id,
        name="New Explore Query",
        scope=scope,
        filters=(),
        breakdowns=(ExploreBreakdown(dimension="run", order=1),),
        metrics=(ExploreMetricSelection(key=default_metric, aggregation="sum"),),
        visualization_hint="table",
    )
    return format_explore_dsl(default_query, default_scope=scope)


def _explore_preview_payload(
    results: dict[str, object] | None,
    *,
    errors: list[str],
    warnings: list[str],
) -> dict[str, object]:
    """Return JSON-friendly preview payload for Explore modal requests."""

    payload: dict[str, object] = {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "results": None,
    }
    if results is None:
        return payload
    payload["results"] = {
        "rows": results.get("rows", []),
        "breakdown_headers": results.get("breakdown_headers", []),
        "metric_label": results.get("metric_label"),
        "metric_unit": results.get("metric_unit"),
        "metric_labels": results.get("metric_labels", []),
        "metric_units": results.get("metric_units", []),
        "metric_aggregations": results.get("metric_aggregations", []),
        "metrics": results.get("metrics", []),
        "aggregation": results.get("aggregation"),
        "visualization": results.get("visualization"),
        "run_count": results.get("run_count"),
        "missing_count": results.get("missing_count"),
        "missing_counts": results.get("missing_counts", []),
        "total_value": results.get("total_value"),
        "total_values": results.get("total_values", []),
        "total_sample_count": results.get("total_sample_count"),
        "total_sample_counts": results.get("total_sample_counts", []),
        "total_cells": results.get("total_cells", []),
        "chart": results.get("chart"),
    }
    return payload


@login_required
def battle_history(request: HttpRequest) -> HttpResponse:
    """Render the Battle History dashboard with filters and pagination."""

    player = _request_player(request)
    column_definitions = _battle_history_columns()
    column_choices = tuple((column.key, column.label) for column in column_definitions)
    if request.method == "POST" and demo_mode_enabled(request):
        return _reject_demo_write(request)

    if request.method == "POST":
        action = (request.POST.get("action") or "").strip()
        if action == "update_column_preferences":
            preference_form = BattleHistoryColumnPreferenceForm(
                request.POST,
                column_choices=column_choices,
            )
            if preference_form.is_valid():
                BattleHistoryColumnPreference.objects.update_or_create(
                    player=player,
                    defaults={"columns": list(preference_form.cleaned_data["columns"])},
                )
                messages.success(request, "Saved column preferences.")
            else:
                messages.error(request, "Could not save column preferences.")
            return safe_redirect(
                request,
                candidates=[request.POST.get("next")],
                fallback=reverse("core:battle_history"),
            )
        if action == "reset_column_preferences":
            BattleHistoryColumnPreference.objects.filter(player=player).delete()
            messages.success(request, "Restored default columns.")
            return safe_redirect(
                request,
                candidates=[request.POST.get("next")],
                fallback=reverse("core:battle_history"),
            )
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

            return safe_redirect(
                request,
                candidates=[update_form.cleaned_data.get("next")],
                fallback=reverse("core:battle_history"),
            )
        if action == "set_report_hidden":
            report_id = int(request.POST.get("report_id") or 0)
            is_hidden = _parse_context_bool(request.POST.get("hidden"))
            updated = BattleReport.objects.filter(player=player, id=report_id).update(
                is_hidden=is_hidden
            )
            if not updated:
                messages.error(request, "Run row not found.")
            return safe_redirect(
                request,
                candidates=[request.POST.get("next")],
                fallback=reverse("core:battle_history"),
            )

        import_form = BattleReportImportForm(request.POST, player=player)
        if import_form.is_valid():
            raw_text = import_form.cleaned_data["raw_text"]
            preset_name = import_form.cleaned_data.get("preset_name") or None
            is_tournament_override = bool(import_form.cleaned_data.get("is_tournament") or False)
            tournament_rank = (import_form.cleaned_data.get("tournament_rank") or None)
            is_dissonance_override = bool(import_form.cleaned_data.get("is_dissonance") or False)
            dissonance_type = (import_form.cleaned_data.get("dissonance_type") or None)
            try:
                _, created = ingest_battle_report(
                    raw_text,
                    player=player,
                    preset_name=preset_name,
                    is_tournament=is_tournament_override,
                    tournament_rank=tournament_rank,
                    is_dissonance=is_dissonance_override,
                    dissonance_type=dissonance_type,
                )
            except Exception:
                if settings.DEBUG:
                    raise
                import_form.add_error(None, "Import failed. Review the pasted report and try again.")
                messages.error(request, "Could not import Battle Report.")
            else:
                if created:
                    messages.success(request, "Battle Report imported.")
                else:
                    messages.warning(request, "Duplicate Battle Report ignored.")
                return redirect("core:battle_history")
    else:
        import_form = BattleReportImportForm(player=player)

    filter_form = BattleHistoryFilterForm(request.GET, player=player)
    filter_form.is_valid()
    visible_columns = _battle_history_visible_columns(player=player, columns=column_definitions)
    columns_by_key = {column.key: column for column in column_definitions}
    visible_column_definitions = [
        columns_by_key[key] for key in visible_columns if key in columns_by_key
    ]
    preference_form = BattleHistoryColumnPreferenceForm(
        column_choices=column_choices,
        initial={"columns": visible_columns},
    )

    progress_qs = BattleReportProgress.objects.filter(player=player)
    highest_wave_by_tier = list(
        progress_qs.filter(tier__isnull=False, wave__isnull=False)
        .exclude(is_tournament=True)
        .exclude(is_dissonance=True)
        .values("tier")
        .annotate(highest_wave=Max("wave"))
        .order_by("tier")
    )
    tournament_summary_rank = (request.GET.get("top_tournament_rank") or "").strip()
    valid_tournament_ranks = {key for key, _label in TOURNAMENT_RANK_CHOICES}
    if tournament_summary_rank not in valid_tournament_ranks:
        tournament_summary_rank = ""
    top_tournament_logs_qs = progress_qs.filter(is_tournament=True, wave__isnull=False)
    if tournament_summary_rank:
        top_tournament_logs_qs = top_tournament_logs_qs.filter(tournament_rank=tournament_summary_rank)
    top_tournament_logs = list(
        top_tournament_logs_qs.order_by("-wave", "-battle_date", "-id")[:3]
    )

    sort_key = filter_form.cleaned_data.get("sort") or "-run_progress__battle_date"
    runs_qs = BattleReport.objects.filter(player=player).select_related(
        "run_progress", "run_progress__preset", "derived_metrics"
    )
    snapshot = filter_form.cleaned_data.get("snapshot") if filter_form.is_valid() else None
    snapshot_context = _snapshot_context_from_filter(snapshot)
    force_tournaments = bool(
        snapshot_context and (snapshot_context.tournament_filter or snapshot_context.include_tournaments)
    )
    include_tournaments = bool(filter_form.cleaned_data.get("include_tournaments") or False)
    if not include_tournaments and not force_tournaments:
        runs_qs = runs_qs.exclude(Q(run_progress__tier__isnull=True) | Q(run_progress__is_tournament=True))

    tier = filter_form.cleaned_data.get("tier") if filter_form.is_valid() else None
    if tier:
        runs_qs = runs_qs.filter(run_progress__tier=tier)

    killed_by = filter_form.cleaned_data.get("killed_by") if filter_form.is_valid() else None
    if killed_by:
        runs_qs = runs_qs.filter(run_progress__killed_by__icontains=killed_by)

    goal = filter_form.cleaned_data.get("goal") if filter_form.is_valid() else None
    if goal:
        runs_qs = runs_qs.filter(run_progress__preset__name__icontains=goal)

    preset = filter_form.cleaned_data.get("preset") if filter_form.is_valid() else None
    if preset:
        runs_qs = runs_qs.filter(run_progress__preset=preset)
    runs_qs = _with_effective_battle_date(runs_qs)
    runs_qs = _apply_snapshot_context_filters(runs_qs, snapshot_context=snapshot_context)

    killed_by_rows = (
        runs_qs.values("run_progress__killed_by")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    killed_by_counts: dict[str, int] = {}
    for row in killed_by_rows:
        label = (row.get("run_progress__killed_by") or "").strip()
        normalized = label if label else "Missing"
        killed_by_counts[normalized] = killed_by_counts.get(normalized, 0) + int(row.get("count") or 0)

    killed_by_labels = list(killed_by_counts.keys())
    killed_by_data = [killed_by_counts[label] for label in killed_by_labels]
    killed_by_donut_json = (
        json.dumps(
            {
                "labels": killed_by_labels,
                "datasets": [
                    {
                        "label": "Runs",
                        "unit": "runs",
                        "data": killed_by_data,
                    }
                ],
            }
        )
        if killed_by_labels
        else None
    )

    runs_for_pagination = _order_battle_history_runs(runs=runs_qs, sort_key=sort_key)
    paginator = Paginator(runs_for_pagination, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    run_numbers = _run_numbers_by_report_id(player=player)
    analyzed_runs = analyze_runs(page_obj.object_list).runs
    run_metrics = {entry.run_id: entry for entry in analyzed_runs}
    page_rows: list[dict[str, object]] = []
    for run in page_obj.object_list:
        metric = run_metrics.get(run.id)
        manual_tournament = bool(getattr(getattr(run, "run_progress", None), "is_tournament", False))
        progress = getattr(run, "run_progress", None)
        tournament_rank = getattr(progress, "tournament_rank", None) if progress else None
        is_dissonance = bool(getattr(progress, "is_dissonance", False)) if progress else False
        dissonance_type = getattr(progress, "dissonance_type", None) if progress else None
        battle_date_fallback = False
        battle_date_display = None
        recovery_packages_raw = None
        cells_earned_display = None
        if progress is not None:
            battle_date_display = getattr(progress, "battle_date", None)
            battle_date_fallback = battle_date_is_fallback(run.raw_text or "")
            cells_earned_display = _format_compact_count(getattr(progress, "cells_earned", None))
        derived = getattr(run, "derived_metrics", None)
        if derived is not None and isinstance(derived.raw_values, dict):
            recovery_packages_raw = derived.raw_values.get("recovery_packages")
        page_rows.append(
            {
                "run": run,
                "metric": metric,
                "run_number": run_numbers.get(run.id),
                "battle_date_display": battle_date_display,
                "battle_date_fallback": battle_date_fallback,
                "real_time_display": _format_real_time(
                    getattr(getattr(run, "run_progress", None), "real_time_seconds", None)
                ),
                "is_tournament": manual_tournament or is_tournament(run),
                "is_dissonance": is_dissonance,
                "dissonance_type": dissonance_type,
                "dissonance_label": _dissonance_label(dissonance_type),
                "tournament_bracket": tournament_bracket(run),
                "tournament_rank": tournament_rank,
                "recovery_packages_raw": recovery_packages_raw,
                "cells_earned_display": cells_earned_display,
            }
        )

    sort_querystrings = _build_sort_querystrings(
        request.GET,
        current_sort=sort_key,
        sortable_keys={
            "battle_date": "run_progress__battle_date",
            "tier": "run_progress__tier",
            "tournament": "run_progress__is_tournament",
            "dissonance": "run_progress__is_dissonance",
            "wave": "run_progress__wave",
            "killed_by": "run_progress__killed_by",
            "real_time": "run_progress__real_time_seconds",
            "hidden": "is_hidden",
            "coins_earned": "run_progress__coins_earned",
            "coins_per_hour": "coins_per_hour",
            "cash_earned": "run_progress__cash_earned",
            "interest_earned": "run_progress__interest_earned",
            "gem_blocks": "run_progress__gem_blocks_tapped",
            "cells_earned": "run_progress__cells_earned",
            "reroll_shards": "run_progress__reroll_shards_earned",
            "recovery_packages": "derived_metrics__values__recovery_packages",
            "preset": "run_progress__preset__name",
            "imported": "parsed_at",
        },
    )
    visible_column_views = [
        {
            "key": column.key,
            "label": column.label,
            "sort_querystring": sort_querystrings.get(column.key),
        }
        for column in visible_column_definitions
    ]

    querystring = request.GET.copy()
    if "page" in querystring:
        querystring.pop("page")
    base_querystring = querystring.urlencode()
    tournament_summary_query_items = [
        (key, value)
        for key, value_list in request.GET.lists()
        if key not in {"top_tournament_rank", "page"}
        for value in value_list
    ]
    battle_report_order_json = json.dumps(_ordered_battle_report_ids(runs_for_pagination))
    modal_preset = filter_form.cleaned_data.get("preset") if filter_form.is_valid() else None
    modal_snapshot = filter_form.cleaned_data.get("snapshot") if filter_form.is_valid() else None
    explore_modal_scope = ExploreScope(
        start_date=None,
        end_date=None,
        tier=filter_form.cleaned_data.get("tier") if filter_form.is_valid() else None,
        preset_id=getattr(modal_preset, "id", None),
        snapshot_id=getattr(modal_snapshot, "id", None),
        past_n_runs=None,
        include_hidden=False,
    )
    explore_modal_dsl = _explore_modal_dsl_text(
        player_id=str(player.id),
        scope=explore_modal_scope,
    )

    return render(
        request,
        "core/battle_history.html",
        {
            "import_form": import_form,
            "filter_form": filter_form,
            "preference_form": preference_form,
            "column_definitions": column_definitions,
            "visible_columns": visible_columns,
            "visible_column_definitions": visible_column_definitions,
            "visible_column_views": visible_column_views,
            "player_presets": Preset.objects.filter(player=player).order_by("name"),
            "highest_wave_by_tier": highest_wave_by_tier,
            "top_tournament_logs": top_tournament_logs,
            "dissonance_bonus_rows": tier_bonus_rows(player=player),
            "tournament_summary_rank": tournament_summary_rank,
            "tournament_rank_choices": TOURNAMENT_RANK_CHOICES,
            "tournament_summary_query_items": tournament_summary_query_items,
            "page_obj": page_obj,
            "page_rows": page_rows,
            "base_querystring": base_querystring,
            "sort_querystrings": sort_querystrings,
            "current_sort": sort_key,
            "killed_by_donut_json": killed_by_donut_json,
            "battle_report_order_json": battle_report_order_json,
            "battle_report_special_run_options_json": json.dumps(
                _battle_report_special_run_options_payload()
            ),
            "explore_modal_dsl": explore_modal_dsl,
        },
    )


@login_required
def battle_report_modal(request: HttpRequest, report_id: int) -> JsonResponse:
    """Return Battle Report modal payload scoped to the requesting player."""

    if request.method not in {"GET", "POST"}:
        return JsonResponse({"ok": False, "error": "Method not allowed."}, status=405)

    if request.method == "POST" and demo_mode_enabled(request):
        return JsonResponse(
            {"ok": False, "error": "Demo mode is read-only. Exit demo mode to make changes."},
            status=403,
        )

    player = _request_player(request)
    try:
        report = BattleReport.objects.select_related("run_progress").get(id=report_id, player=player)
    except BattleReport.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Battle Report not found."}, status=404)

    if request.method == "POST":
        progress = getattr(report, "run_progress", None)
        if progress is None:
            return JsonResponse({"ok": False, "error": "Battle Report progress not found."}, status=404)

        form = BattleReportSpecialRunUpdateForm(request.POST)
        if not form.is_valid():
            return JsonResponse(
                {"ok": False, "errors": form.errors.get_json_data()},
                status=400,
            )

        progress.is_tournament = bool(form.cleaned_data.get("is_tournament") or False)
        progress.tournament_rank = form.cleaned_data.get("tournament_rank") or None
        progress.is_dissonance = bool(form.cleaned_data.get("is_dissonance") or False)
        progress.dissonance_type = form.cleaned_data.get("dissonance_type") or None
        progress.save()
        rebuild_dissonance_progression(player=player)
        report.refresh_from_db()

    return JsonResponse({"ok": True, "report": _battle_report_modal_payload(player=player, report=report)})


@login_required
def lifetime_stats_modal(request: HttpRequest) -> JsonResponse:
    """Return Lifetime Stats modal payload for the requesting player."""

    if request.method != "GET":
        return JsonResponse({"ok": False, "error": "Method not allowed."}, status=405)

    player = _request_player(request)
    filter_form = LifetimeStatsFilterForm(request.GET, today=date.today())
    if not filter_form.is_valid():
        return JsonResponse(
            {"ok": False, "errors": filter_form.errors.get_json_data()},
            status=400,
        )

    mode = str(filter_form.cleaned_data.get("range_mode") or "all")
    start_date = filter_form.cleaned_data.get("start_date")
    end_date = filter_form.cleaned_data.get("end_date")

    runs = BattleReport.objects.filter(player=player).select_related(
        "run_progress",
        "run_progress__preset",
        "derived_metrics",
    )
    runs = _with_effective_battle_date(runs).order_by("effective_battle_date", "id")
    runs = runs.exclude(run_progress__is_dissonance=True)
    if start_date:
        runs = runs.filter(effective_battle_date__date__gte=start_date)
    if end_date:
        runs = runs.filter(effective_battle_date__date__lte=end_date)

    records = tuple(runs)
    groups = build_lifetime_stat_groups(records=records, player=player)

    start_label = start_date.isoformat() if start_date else None
    end_label = end_date.isoformat() if end_date else None
    if mode == "event" and start_label and end_label:
        range_label = f"Event window • {start_label} to {end_label}"
    elif mode == "custom" and start_label and end_label:
        range_label = f"{start_label} to {end_label}"
    else:
        range_label = "All time"

    return JsonResponse(
        {
            "ok": True,
            "groups": groups,
            "run_count": len(records),
            "range": {
                "mode": mode,
                "start_date": start_label,
                "end_date": end_label,
                "label": range_label,
            },
        }
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

    def _effect_value_for_level(effect_value_raw: str, *, level: int) -> str:
        """Pick a best-effort effect value for a given card level.

        The wiki "Effect" field sometimes contains a single value, and
        sometimes a slash-delimited list (ex: "1 / 2 / 3"). This helper keeps
        the dashboard deterministic without making gameplay inferences.

        Args:
            effect_value_raw: Wiki-derived raw "Effect" cell text.
            level: Current displayed card level (0 when unowned).

        Returns:
            A single effect value string for display (may be empty).
        """

        cleaned = (effect_value_raw or "").strip()
        if not cleaned or level <= 0:
            return cleaned
        if "/" not in cleaned:
            return cleaned
        parts = [part.strip() for part in cleaned.split("/") if part.strip()]
        if len(parts) <= 1:
            return cleaned
        idx = min(max(level, 1), len(parts)) - 1
        return parts[idx]

    def _replace_placeholders(description_text: str, *, effect_value: str) -> str | None:
        """Replace common wiki placeholders in a description when possible.

        Args:
            description_text: Wiki-derived description text.
            effect_value: Best-effort effect value for the current level.

        Returns:
            A substituted description string, or None when no substitution was applied.
        """

        cleaned_description = (description_text or "").strip()
        cleaned_effect = (effect_value or "").strip()
        if not cleaned_description or not cleaned_effect:
            return None

        if "[x]" in cleaned_description:
            import re

            match = re.search(r"-?\d+(?:\.\d+)?", cleaned_effect)
            replacement = match.group(0) if match else cleaned_effect
            return cleaned_description.replace("[x]", replacement)

        if "#" not in cleaned_description:
            return None

        lowered = cleaned_description.casefold()
        replacement = cleaned_effect
        if "#%" in lowered or "+#%" in lowered:
            replacement = replacement.replace("%", "").strip()
            if replacement.startswith("+"):
                replacement = replacement[1:].strip()
            if replacement.casefold().startswith("x"):
                replacement = replacement[1:].strip()
        elif "x #" in lowered:
            if replacement.casefold().startswith("x"):
                replacement = replacement[1:].strip()
        return cleaned_description.replace("#", replacement)

    cleaned_description = (description or "").strip()
    cleaned_effect = (effect_raw or "").strip()
    if not cleaned_description and not cleaned_effect:
        return ""

    effect_at_level = _effect_value_for_level(cleaned_effect, level=level)
    substituted = _replace_placeholders(cleaned_description, effect_value=effect_at_level)
    if substituted is not None:
        return substituted

    effect_with_level = effect_at_level
    if effect_at_level and level > 0:
        effect_with_level = f"{effect_at_level} (Level {level})"

    if cleaned_description and effect_with_level:
        return f"{cleaned_description}\n{effect_with_level}"

    return cleaned_description or effect_with_level


def _render_card_parameters_html(*, description: str, effect_raw: str, level: int) -> str:
    """Render an HTML-safe parameters string for the Cards dashboard.

    This renderer replaces placeholder tokens (e.g. `#`, `[x]`) in card
    descriptions with the effective value for the current card level. When
    `level == 0`, placeholders are permitted and no substitution is attempted.

    Args:
        description: Wiki-derived description text for the card.
        effect_raw: Wiki-derived effect value text for the card.
        level: Current displayed card level (0 when unowned).

    Returns:
        A Django SafeString-like object suitable for direct template rendering.
    """

    from dataclasses import dataclass
    from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
    import re

    from django.utils.html import format_html
    from django.utils.html import escape

    @dataclass(frozen=True, slots=True)
    class _Computed:
        kind: str
        value: Decimal

    def _token_kind(token: str) -> str:
        lowered = (token or "").casefold()
        if "%" in lowered:
            return "percent"
        if lowered.lstrip().startswith("x") or "x" in lowered:
            return "multiplier"
        if "sec" in lowered or re.search(r"\b\d+(?:\.\d+)?\s*s\b", lowered):
            return "seconds"
        return "number"

    def _parse_decimal(token: str) -> Decimal | None:
        match = re.search(r"([+-]?[0-9]+(?:\.[0-9]+)?)", (token or "").replace(",", ""))
        if not match:
            return None
        try:
            return Decimal(match.group(1))
        except (InvalidOperation, ValueError):
            return None

    def _parse_level_values(effect_value_raw: str) -> tuple[str, tuple[Decimal, ...]] | None:
        cleaned = (effect_value_raw or "").strip()
        if not cleaned:
            return None
        parts = [part.strip() for part in cleaned.split("/") if part.strip()]
        kind = _token_kind(parts[0])
        parsed: list[Decimal] = []
        for part in parts:
            if _token_kind(part) != kind:
                return None
            value = _parse_decimal(part)
            if value is None:
                return None
            parsed.append(value)
        return kind, tuple(parsed)

    def _effective_value(kind: str, values: tuple[Decimal, ...], *, level: int) -> Decimal:
        clamped_level = max(1, min(int(level), len(values)))
        base = values[0]
        deltas = [values[i] - values[i - 1] for i in range(1, len(values))]
        scaled = base + sum(deltas[: clamped_level - 1], Decimal(0))
        return scaled

    def _format_numeric(kind: str, value: Decimal) -> str:
        if kind == "multiplier":
            return f"{value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):.2f}"
        if kind == "percent":
            rounded = value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            return f"{int(rounded)}"
        if kind == "seconds":
            rounded = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            as_str = f"{rounded:f}"
            return as_str.rstrip("0").rstrip(".") if "." in as_str else as_str
        rounded = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        as_str = f"{rounded:f}"
        return as_str.rstrip("0").rstrip(".") if "." in as_str else as_str

    def _compute(effect_value_raw: str, *, level: int) -> _Computed | None:
        parsed = _parse_level_values(effect_value_raw)
        if parsed is None:
            return None
        kind, values = parsed
        return _Computed(kind=kind, value=_effective_value(kind, values, level=level))

    def _effect_token_for_level(effect_value_raw: str, *, level: int) -> str:
        cleaned = (effect_value_raw or "").strip()
        if not cleaned or level <= 0:
            return cleaned
        if "/" not in cleaned:
            return cleaned
        parts = [part.strip() for part in cleaned.split("/") if part.strip()]
        if len(parts) <= 1:
            return cleaned
        idx = min(max(level, 1), len(parts)) - 1
        return parts[idx]

    def _bold_first_number(text: str, *, replacement: str) -> str:
        match = re.search(r"([0-9]+(?:\.[0-9]+)?)", (text or "").replace(",", ""))
        if not match:
            return escape(text)
        start, end = match.span(1)
        before = escape(text[:start])
        after = escape(text[end:])
        return format_html("{}{}{}", before, format_html("<strong>{}</strong>", replacement), after)

    def _substitute(text: str, *, computed: _Computed) -> str:
        numeric = _format_numeric(computed.kind, computed.value)
        bold = format_html("<strong>{}</strong>", numeric)
        parts = re.split(r"(\[x\]|#)", text)
        rendered: str = ""
        for part in parts:
            if part in ("[x]", "#"):
                rendered = format_html("{}{}", rendered, bold)
            else:
                rendered = format_html("{}{}", rendered, escape(part))
        return rendered

    cleaned_description = (description or "").strip()
    cleaned_effect = (effect_raw or "").strip()
    if not cleaned_description and not cleaned_effect:
        return ""

    if level <= 0:
        if cleaned_description and cleaned_effect:
            return format_html("{}\n{}", escape(cleaned_description), escape(cleaned_effect))
        return escape(cleaned_description or cleaned_effect)

    computed = _compute(cleaned_effect, level=level)
    if computed is None:
        return escape(
            _render_card_parameters_text(description=cleaned_description, effect_raw=cleaned_effect, level=level)
        )

    lines: list[str] = []
    if cleaned_description:
        lines.append(_substitute(cleaned_description, computed=computed))
    elif cleaned_effect:
        lines.append(escape(cleaned_effect))

    effect_token = _effect_token_for_level(cleaned_effect, level=level)
    if effect_token:
        numeric = _format_numeric(computed.kind, computed.value)
        effect_display = _bold_first_number(effect_token, replacement=numeric)
        lines.append(format_html("{} (Level {})", effect_display, level))

    if not lines:
        return ""
    rendered = lines[0]
    for line in lines[1:]:
        rendered = format_html("{}\n{}", rendered, line)
    return rendered


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


def _usage_percentage(*, run_count: int, total_runs: int) -> float:
    """Return the percentage of runs represented by a usage count.

    Args:
        run_count: Matching runs for the row being summarized.
        total_runs: Total visible runs used as the denominator.

    Returns:
        The percentage value in the range 0..100.
    """

    if total_runs <= 0:
        return 0.0
    return (float(run_count) / float(total_runs)) * 100.0


_CARD_USAGE_OBSERVED_METRIC_LABELS: dict[str, str] = {
    "energy_shield": "Energy Shield Hits Absorbed",
    "nuke": "Nuke Uses",
    "second_wind": "Second Wind Uses",
    "demon_mode": "Demon Mode Uses",
    "critical_coin": "Coins From Critical Coin",
    "death_ray": "Death Ray Damage",
}


def _card_usage_observed_metric_label(*, card_slug: str) -> str:
    """Return the observed Battle Report metric label associated with a card."""

    return _CARD_USAGE_OBSERVED_METRIC_LABELS.get(card_slug, "")


def _build_cards_usage_rows(
    *,
    cards: Sequence[PlayerCard],
    preset_usage_counts: dict[int, int],
    total_runs: int,
) -> list[dict[str, object]]:
    """Build Cards dashboard usage rows from preset-tagged run counts.

    Args:
        cards: Player cards to summarize.
        preset_usage_counts: Visible run counts keyed by preset id.
        total_runs: Total visible run count for percentage calculations.

    Returns:
        A list of card usage rows sorted by highest usage first.
    """

    rows: list[dict[str, object]] = []
    for card in cards:
        definition = card.card_definition
        name = definition.name if definition is not None else card.card_slug
        presets = tuple(card.presets.all())
        runs_used = sum(preset_usage_counts.get(preset.id, 0) for preset in presets if preset.id is not None)
        rows.append(
            {
                "name": name,
                "runs_used": runs_used,
                "percentage_used": _usage_percentage(run_count=runs_used, total_runs=total_runs),
                "observed_metric_label": _card_usage_observed_metric_label(card_slug=card.card_slug),
                "presets": presets,
            }
        )
    return sorted(
        rows,
        key=lambda row: (-cast(int, row["runs_used"]), str(row["name"]).lower()),
    )


def _build_preset_usage_rows(
    *,
    presets: Sequence[Preset],
    preset_usage_counts: dict[int, int],
    total_runs: int,
) -> list[dict[str, object]]:
    """Build preset usage rows for the Cards usage modal.

    Args:
        presets: Known presets for the player.
        preset_usage_counts: Visible run counts keyed by preset id.
        total_runs: Total visible run count for percentage calculations.

    Returns:
        A list of preset usage rows sorted by highest usage first.
    """

    rows = [
        {
            "name": preset.name,
            "badge_color": preset.badge_color(),
            "runs_used": preset_usage_counts.get(preset.id, 0) if preset.id is not None else 0,
            "percentage_used": _usage_percentage(
                run_count=preset_usage_counts.get(preset.id, 0) if preset.id is not None else 0,
                total_runs=total_runs,
            ),
        }
        for preset in presets
    ]
    return sorted(
        rows,
        key=lambda row: (-cast(int, row["runs_used"]), str(row["name"]).lower()),
    )


@login_required
def cards(request: HttpRequest) -> HttpResponse:
    """Render the Cards dashboard (slots + inventory + preset tagging)."""

    player = _request_player(request)
    definitions = list(CardDefinition.objects.order_by("name"))

    if not demo_mode_enabled(request):
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

    total_cards_progress = None
    if definitions:
        cards_by_slug = {
            card.card_slug: card
            for card in PlayerCard.objects.filter(player=player).only(
                "card_slug",
                "stars_unlocked",
                "inventory_count",
            )
        }
        card_states = []
        for definition in definitions:
            card = cards_by_slug.get(definition.slug)
            card_states.append((getattr(card, "stars_unlocked", 0) or 0, getattr(card, "inventory_count", 0) or 0))
        total_cards_progress = derive_total_cards_progress(
            definition_count=len(definitions),
            card_states=card_states,
        )

    if request.method == "POST":
        if demo_mode_enabled(request):
            return _reject_demo_write(request)
        action = (request.POST.get("action") or "").strip()
        redirect_response = safe_redirect(
            request,
            candidates=[request.POST.get("next"), request.META.get("HTTP_REFERER")],
            fallback=request.path,
        )

        if action == "unlock_slot":
            max_slots = card_slot_max_slots()
            next_cost = next_card_slot_unlock_cost_raw(unlocked=player.card_slots_unlocked)
            if max_slots is None:
                messages.warning(request, "Card slot limits are not available yet.")
                return redirect_response
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
                        return redirect_response
                    player.card_slots_unlocked += 1
                    player.save(update_fields=["card_slots_unlocked"])
                if next_cost:
                    messages.success(request, f"Unlocked the next card slot (cost: {next_cost}).")
                else:
                    messages.success(request, "Unlocked the next card slot.")
            else:
                messages.warning(request, "No additional card slots are available.")
            return redirect_response

        if action == "update_inventory":
            form = CardInventoryUpdateForm(request.POST)
            if not form.is_valid():
                messages.error(request, "Could not save card inventory.")
                return redirect_response

            card = PlayerCard.objects.filter(player=player, id=form.cleaned_data["card_id"]).first()
            if card is None:
                messages.error(request, "Card row not found.")
                return redirect_response

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
            return redirect_response

        if action == "update_presets":
            form = CardPresetUpdateForm(request.POST, player=player)
            if not form.is_valid():
                messages.error(request, "Could not save card presets.")
                return redirect_response

            card = PlayerCard.objects.filter(player=player, id=form.cleaned_data["card_id"]).first()
            if card is None:
                messages.error(request, "Card row not found.")
                return redirect_response

            chosen_presets = list(form.cleaned_data["presets"])
            new_name = form.cleaned_data["new_preset_name"]
            if new_name:
                preset, _ = Preset.objects.get_or_create(player=player, name=new_name)
                chosen_presets.append(preset)
            card.presets.set(chosen_presets, through_defaults={"player": player})
            messages.success(request, "Saved card presets.")
            return redirect_response

        if action == "bulk_update_presets":
            form = CardPresetBulkUpdateForm(request.POST, player=player)
            if not form.is_valid():
                messages.error(request, "Could not save bulk card presets.")
                return redirect_response

            card_ids: list[int] = list(form.cleaned_data["card_ids"])
            chosen_presets = list(form.cleaned_data["presets"])
            new_name = form.cleaned_data["new_preset_name"]
            if new_name:
                preset, _ = Preset.objects.get_or_create(player=player, name=new_name)
                chosen_presets.append(preset)

            if not chosen_presets:
                messages.error(request, "Select at least one preset or enter a new preset name.")
                return redirect_response

            cards = list(
                PlayerCard.objects.filter(player=player, id__in=card_ids)
                .prefetch_related("presets")
                .order_by("id")
            )
            if len(cards) != len(set(card_ids)):
                messages.error(request, "One or more selected cards were not found.")
                return redirect_response

            with transaction.atomic():
                for card in cards:
                    combined: dict[int, Preset] = {preset.id: preset for preset in card.presets.all()}
                    for preset in chosen_presets:
                        combined[preset.id] = preset
                    card.presets.set(list(combined.values()), through_defaults={"player": player})

            messages.success(request, f"Saved presets for {len(cards)} cards.")
            return redirect_response

        messages.error(request, "Unknown cards action.")
        return redirect_response

    filter_form = CardsFilterForm(request.GET, player=player)
    filter_form.is_valid()
    name_query = (filter_form.cleaned_data.get("q") or "").strip()
    selected_presets = tuple(filter_form.cleaned_data.get("presets") or ())
    selected_maxed = (filter_form.cleaned_data.get("maxed") or "").strip()
    requested_sort = (filter_form.cleaned_data.get("sort") or "").strip()

    card_qs = (
        PlayerCard.objects.filter(player=player)
        .select_related("card_definition")
        .prefetch_related("presets")
        .order_by("card_definition__name", "card_slug")
    )
    if name_query:
        card_qs = card_qs.filter(
            Q(card_definition__name__icontains=name_query) | Q(card_slug__icontains=name_query)
        )
    if selected_presets:
        card_qs = card_qs.filter(presets__in=selected_presets).distinct()

    cards = list(card_qs)
    presets = tuple(Preset.objects.filter(player=player).order_by("name"))
    preset_usage_counts = {
        row["preset_id"]: row["run_count"]
        for row in (
            BattleReportProgress.objects.filter(
                player=player,
                battle_report__is_hidden=False,
                preset_id__isnull=False,
                is_dissonance=False,
            )
            .values("preset_id")
            .annotate(run_count=Count("battle_report_id"))
        )
        if row["preset_id"] is not None
    }
    total_visible_runs = (
        BattleReport.objects.filter(player=player, is_hidden=False)
        .exclude(run_progress__is_dissonance=True)
        .count()
    )

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
        parameters_html = _render_card_parameters_html(
            description=(definition.description if definition is not None else ""),
            effect_raw=(definition.effect_raw if definition is not None else ""),
            level=display_level,
        )
        rows.append(
            {
                "id": card.id,
                "name": name,
                "wiki_page_url": (definition.wiki_page_url if definition is not None else ""),
                "level": display_level,
                "inventory_count": display_inventory,
                "inventory_threshold": display_threshold,
                "is_maxed": (not is_unowned and progress.is_maxed),
                "rarity": (definition.rarity if definition is not None else ""),
                "parameters_html": parameters_html,
                "presets": tuple(card.presets.all()),
                "updated_at": card.updated_at,
            }
        )

    if selected_maxed == "maxed":
        rows = [row for row in rows if row.get("is_maxed")]
    elif selected_maxed == "unmaxed":
        rows = [row for row in rows if not row.get("is_maxed")]

    allowed_sort_keys = {"name", "rarity", "level", "progress", "maxed"}
    current_sort = requested_sort if requested_sort.lstrip("-") in allowed_sort_keys else "rarity"
    rows = _sort_card_rows(rows, sort_key=current_sort)

    max_slots = card_slot_max_slots()
    next_cost = next_card_slot_unlock_cost_raw(unlocked=player.card_slots_unlocked)
    card_slots = {
        "unlocked": player.card_slots_unlocked,
        "max": max_slots,
        "next_cost": next_cost,
    }

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
            "total_cards_progress": total_cards_progress,
            "filter_form": filter_form,
            "presets": presets,
            "preset_links": preset_links,
            "rows": rows,
            "sort_querystrings": sort_querystrings,
            "current_sort": current_sort,
            "card_usage_rows": _build_cards_usage_rows(
                cards=cards,
                preset_usage_counts=preset_usage_counts,
                total_runs=total_visible_runs,
            ),
            "preset_usage_rows": _build_preset_usage_rows(
                presets=presets,
                preset_usage_counts=preset_usage_counts,
                total_runs=total_visible_runs,
            ),
            "card_usage_total_runs": total_visible_runs,
        },
    )


@login_required
def ultimate_weapon_progress(request: HttpRequest) -> HttpResponse:
    """Render the Ultimate Weapon progress page."""
    player = _request_player(request)
    if request.method == "POST" and demo_mode_enabled(request):
        return _reject_demo_write(request)
    player_cards = tuple(
        PlayerCard.objects.filter(player=player, stars_unlocked__gt=0).select_related("card_definition")
    )

    uw_definitions = list(UltimateWeaponDefinition.objects.order_by("name"))
    if not demo_mode_enabled(request):
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
        redirect_response = safe_redirect(
            request,
            candidates=[request.POST.get("next"), request.META.get("HTTP_REFERER")],
            fallback=request.path,
        )

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
                return redirect_response

            try:
                validate_uw_parameter_definitions(uw_definition=uw.ultimate_weapon_definition)
            except ValueError:
                if settings.DEBUG:
                    raise
                messages.warning(
                    request,
                    f"Skipping {uw.ultimate_weapon_definition.name}: invalid parameter definitions.",
                )
                if is_ajax:
                    return JsonResponse(
                        {"ok": False, "error": "Invalid parameter definitions."},
                        status=400,
                    )
                return redirect_response

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
            return redirect_response

        if action == "level_up_uw_param":
            player_param_id = int(request.POST.get("param_id") or 0)
            player_param = (
                PlayerUltimateWeaponParameter.objects.filter(player=player, id=player_param_id)
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
                return redirect_response

            if not player_param.player_ultimate_weapon.unlocked:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Ultimate Weapon is locked."}, status=400)
                messages.error(request, "Cannot upgrade a locked Ultimate Weapon.")
                return redirect_response

            param_def = player_param.parameter_definition
            levels_qs = param_def.levels.order_by("level")
            max_level = levels_qs.values_list("level", flat=True).last() or 0
            if player_param.level >= max_level:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Already at max level."}, status=400)
                messages.warning(request, "That parameter is already maxed.")
                return redirect_response

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
            return redirect_response

        if action == "level_down_uw_param":
            player_param_id = int(request.POST.get("param_id") or 0)
            player_param = (
                PlayerUltimateWeaponParameter.objects.filter(player=player, id=player_param_id)
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
                return redirect_response

            if not player_param.player_ultimate_weapon.unlocked:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Ultimate Weapon is locked."}, status=400)
                messages.error(request, "Cannot change levels on a locked Ultimate Weapon.")
                return redirect_response

            param_def = player_param.parameter_definition
            levels_qs = param_def.levels.order_by("level")
            min_level = levels_qs.values_list("level", flat=True).first() or 0
            if player_param.level <= min_level:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Already at minimum level."}, status=400)
                messages.warning(request, "That parameter is already at its minimum level.")
                return redirect_response

            with transaction.atomic():
                player_param.level -= 1
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

            messages.success(request, f"Decreased {param_def.display_name}.")
            return redirect_response

        if is_ajax:
            return JsonResponse({"ok": False, "error": "Unknown action."}, status=400)
        messages.error(request, "Unknown action.")
        return redirect_response

    filter_form = UltimateWeaponProgressFilterForm(request.GET)
    filter_form.is_valid()
    status = (filter_form.cleaned_data.get("status") or "").strip()
    name_query = (filter_form.cleaned_data.get("q") or "").strip()


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
    if name_query:
        ultimate_weapons_qs = ultimate_weapons_qs.filter(
            ultimate_weapon_definition__name__icontains=name_query
        )

    any_battles = BattleReport.objects.filter(player=player).exists()
    uw_runs_observed_counts = count_observed_uw_runs(player=player) if any_battles else {}

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

        runs_count = int(uw_runs_observed_counts.get(uw_def.id, 0))

        tiles.append(
            {
                "id": uw.id,
                "name": uw_def.name,
                "slug": uw_def.slug,
                "wiki_page_url": (uw_def.wiki_page_url or ""),
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

    show_death_wave_param = request.GET.get("show_death_wave")
    show_golden_bot_param = request.GET.get("show_golden_bot")
    show_death_wave = (
        True
        if show_death_wave_param is None
        else str(show_death_wave_param).strip().casefold() in {"1", "true", "yes", "on"}
    )
    show_golden_bot = (
        True
        if show_golden_bot_param is None
        else str(show_golden_bot_param).strip().casefold() in {"1", "true", "yes", "on"}
    )
    uw_sync = build_uw_sync_payload(
        player=player,
        show_death_wave=show_death_wave,
        show_golden_bot=show_golden_bot,
    )
    uw_snapshots = ChartSnapshot.objects.filter(player=player, target="ultimate_weapons").order_by("-created_at")
    uw_snapshot_id = request.GET.get("snapshot_id") or request.GET.get("uw_snapshot_id")
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
                runs_qs = _with_effective_battle_date(
                    BattleReport.objects.filter(player=player).select_related(
                        "run_progress",
                        "run_progress__preset",
                        "derived_metrics",
                    )
                ).order_by("effective_battle_date")
                force_tournaments = bool(dto.context.tournament_filter)
                runs_qs = _exclude_special_runs(
                    runs_qs,
                    include_tournaments=bool(dto.context.include_tournaments or force_tournaments),
                    include_dissonance=bool(dto.context.include_dissonance),
                )
                if not dto.context.include_hidden:
                    runs_qs = runs_qs.filter(is_hidden=False)
                if dto.context.start_date:
                    runs_qs = runs_qs.filter(effective_battle_date__date__gte=dto.context.start_date)
                if dto.context.end_date:
                    runs_qs = runs_qs.filter(effective_battle_date__date__lte=dto.context.end_date)
                if dto.context.tier:
                    runs_qs = runs_qs.filter(run_progress__tier=dto.context.tier)
                if dto.context.preset_id:
                    runs_qs = runs_qs.filter(run_progress__preset_id=dto.context.preset_id)
                runs_qs = _apply_tournament_filter(
                    runs_qs,
                    tournament_filter=dto.context.tournament_filter,
                )

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
            "snapshot_id": uw_snapshot_id,
            "uw_snapshot_chart_json": uw_snapshot_chart_json,
            "uw_snapshot_name": uw_snapshot_name,
            "goals_widget_rows": goals_widget_rows(player=player, goal_type=str(GoalType.ULTIMATE_WEAPON)),
            "goals_widget_goal_type": str(GoalType.ULTIMATE_WEAPON),
        },
    )


def _guardian_runs_used_counts(*, player: Player) -> dict[str, int]:
    """Return observed guardian chip usage counts keyed by chip slug.

    Args:
        player: Player whose Battle Reports are being summarized.

    Returns:
        Mapping of guardian chip slug to count of runs with a matching guardian
        metric recorded in derived Battle Report values.
    """

    metric_keys = {
        "attack": "guardian_damage",
        "fetch": "guardian_coins_fetched",
        "bounty": "guardian_coins_stolen",
        "summon": "guardian_summoned_enemies",
    }
    counts = {slug: 0 for slug in metric_keys}
    derived_rows = BattleReportDerivedMetrics.objects.filter(player=player).values_list("values", flat=True)
    for values in derived_rows:
        if not isinstance(values, dict):
            continue
        for slug, metric_key in metric_keys.items():
            raw_value = values.get(metric_key)
            if raw_value is None:
                continue
            try:
                numeric = float(raw_value)
            except (TypeError, ValueError):
                continue
            if numeric > 0:
                counts[slug] += 1
    return counts


@login_required
def guardian_progress(request: HttpRequest) -> HttpResponse:
    """Render the Guardian Chips progress dashboard."""

    player = _request_player(request)
    if request.method == "POST" and demo_mode_enabled(request):
        return _reject_demo_write(request)
    player_cards = tuple(
        PlayerCard.objects.filter(player=player, stars_unlocked__gt=0).select_related("card_definition")
    )

    if not demo_mode_enabled(request):
        orphaned_guardian_params_deleted, _ = PlayerGuardianChipParameter.objects.filter(
            player_guardian_chip__player=player,
            parameter_definition__isnull=True,
        ).delete()
        if orphaned_guardian_params_deleted and not request.headers.get("x-requested-with") == "XMLHttpRequest":
            messages.warning(request, "Removed guardian chip parameter rows that no longer match known definitions.")

    guardian_definitions = list(GuardianChipDefinition.objects.order_by("name"))
    if not demo_mode_enabled(request):
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
        redirect_response = safe_redirect(
            request,
            candidates=[request.POST.get("next"), request.META.get("HTTP_REFERER")],
            fallback=request.path,
        )

        if action == "unlock_guardian_slot":
            max_slots = guardian_chip_max_slots()
            unlocked_slots = max(1, int(player.guardian_chip_slots_unlocked or 1))
            next_cost = next_guardian_chip_slot_unlock_cost_raw(unlocked=unlocked_slots)
            if unlocked_slots < max_slots:
                with transaction.atomic():
                    player.guardian_chip_slots_unlocked = unlocked_slots + 1
                    player.save(update_fields=["guardian_chip_slots_unlocked"])
                slot_number = player.guardian_chip_slots_unlocked
                if next_cost:
                    messages.success(
                        request,
                        f"Unlocked guardian chip slot {slot_number} (cost: {next_cost}).",
                    )
                else:
                    messages.success(request, f"Unlocked guardian chip slot {slot_number}.")
            else:
                messages.warning(request, "No additional guardian chip slots are available.")
            return redirect_response

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
                return redirect_response

            try:
                validate_parameter_definitions(
                    parameter_definitions=chip.guardian_chip_definition.parameter_definitions,
                    expected_count=3,
                    entity_kind="guardian chip",
                    entity_slug=chip.guardian_chip_definition.slug,
                )
            except ValueError:
                if settings.DEBUG:
                    raise
                messages.warning(
                    request,
                    f"Skipping {chip.guardian_chip_definition.name}: invalid parameter definitions.",
                )
                if is_ajax:
                    return JsonResponse(
                        {"ok": False, "error": "Invalid parameter definitions."},
                        status=400,
                    )
                return redirect_response

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
            return redirect_response

        if action == "level_up_guardian_param":
            player_param_id = int(request.POST.get("param_id") or 0)
            player_param = (
                PlayerGuardianChipParameter.objects.filter(player=player, id=player_param_id)
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
                return redirect_response

            if not player_param.player_guardian_chip.unlocked:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Guardian chip is locked."}, status=400)
                messages.error(request, "Cannot upgrade a locked Guardian Chip.")
                return redirect_response

            param_def = player_param.parameter_definition
            levels_qs = param_def.levels.order_by("level")
            max_level = levels_qs.values_list("level", flat=True).last() or 0
            if player_param.level >= max_level:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Already at max level."}, status=400)
                messages.warning(request, "That parameter is already maxed.")
                return redirect_response

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
            return redirect_response

        if action == "level_down_guardian_param":
            player_param_id = int(request.POST.get("param_id") or 0)
            player_param = (
                PlayerGuardianChipParameter.objects.filter(player=player, id=player_param_id)
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
                return redirect_response

            if not player_param.player_guardian_chip.unlocked:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Guardian chip is locked."}, status=400)
                messages.error(request, "Cannot change levels on a locked Guardian Chip.")
                return redirect_response

            param_def = player_param.parameter_definition
            levels_qs = param_def.levels.order_by("level")
            min_level = levels_qs.values_list("level", flat=True).first() or 0
            if player_param.level <= min_level:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Already at minimum level."}, status=400)
                messages.warning(request, "That parameter is already at its minimum level.")
                return redirect_response

            with transaction.atomic():
                player_param.level -= 1
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

            messages.success(request, f"Decreased {param_def.display_name}.")
            return redirect_response

        if action == "set_guardian_active":
            chip_id = int(request.POST.get("entity_id") or 0)
            desired_active = "1" in {(value or "").strip() for value in request.POST.getlist("active")}
            chip = PlayerGuardianChip.objects.filter(player=player, id=chip_id).first()
            if chip is None:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Guardian chip not found."}, status=404)
                messages.error(request, "Guardian chip not found.")
                return redirect_response

            if desired_active and not chip.unlocked:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Guardian chip is locked."}, status=400)
                messages.error(request, "Cannot activate a locked Guardian Chip.")
                return redirect_response

            chip.active = desired_active
            try:
                chip.save(update_fields=["active", "updated_at"])
            except ValidationError:
                if is_ajax:
                    return JsonResponse(
                        {"ok": False, "error": "Unable to update guardian chip status."},
                        status=400,
                    )
                messages.error(request, "Unable to update guardian chip status.")
                return redirect_response

            if is_ajax:
                return JsonResponse({"ok": True, "active": chip.active})
            messages.success(request, "Saved active guardian chip selection.")
            return redirect_response

        if is_ajax:
            return JsonResponse({"ok": False, "error": "Unknown action."}, status=400)
        messages.error(request, "Unknown action.")
        return redirect_response

    filter_form = UpgradeableEntityProgressFilterForm(request.GET, entity_label_plural="guardian chips")
    filter_form.is_valid()
    status = (filter_form.cleaned_data.get("status") or "").strip()
    name_query = (filter_form.cleaned_data.get("q") or "").strip()

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
    if name_query:
        chips_qs = chips_qs.filter(guardian_chip_definition__name__icontains=name_query)

    any_battles = BattleReport.objects.filter(player=player).exists()
    guardian_run_counts = _guardian_runs_used_counts(player=player)
    unlocked_slots = max(1, int(player.guardian_chip_slots_unlocked or 1))
    max_slots = guardian_chip_max_slots()
    next_slot_cost = next_guardian_chip_slot_unlock_cost_raw(unlocked=unlocked_slots)
    active_limit = min(MAX_ACTIVE_GUARDIAN_CHIPS, unlocked_slots)
    guardian_hero_note = (
        f"Only {active_limit} chip{'s' if active_limit != 1 else ''} can be active at a time."
    )
    active_count = PlayerGuardianChip.objects.filter(player=player, active=True).count()
    activation_limit_reached = active_count >= active_limit

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
        for row in active_chip_rows[:active_limit]
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

        runs_count = guardian_run_counts.get(chip_def.slug, 0) if any_battles else 0
        runs_muted = chip_def.slug == "ally"
        runs_tooltip = (
            "Runs Used cannot be tracked yet for Ally Chip."
            if runs_muted
            else ""
        )

        tiles.append(
            {
                "id": chip.id,
                "name": chip_def.name,
                "slug": chip_def.slug,
                "wiki_page_url": (chip_def.wiki_page_url or ""),
                "description": ((chip_def.description or "").splitlines() or [""])[0].strip(),
                "unlocked": chip.unlocked,
                "active": chip.active,
                "toggle_disabled": (not chip.unlocked) or (activation_limit_reached and not chip.active),
                "unlock_cost_raw": None,
                "summary": {
                    "total_invested": total_bits_invested,
                    "headline_label": "Runs used",
                    "headline_value": "—" if runs_muted else runs_count,
                    "headline_empty": (not any_battles),
                    "headline_muted": runs_muted,
                    "headline_tooltip": runs_tooltip,
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
            "activation_limit_current": active_count,
            "activation_limit_total": active_limit,
            "active_chip_hero": active_chip_hero,
            "guardian_slots": {
                "unlocked": unlocked_slots,
                "max": max_slots,
                "next_cost": next_slot_cost,
            },
            "guardian_hero_note": guardian_hero_note,
            "goals_widget_rows": goals_widget_rows(player=player, goal_type=str(GoalType.GUARDIAN_CHIP)),
            "goals_widget_goal_type": str(GoalType.GUARDIAN_CHIP),
        },
    )


@login_required
def bots_progress(request: HttpRequest) -> HttpResponse:
    """Render the Bots progress dashboard."""

    player = _request_player(request)
    if request.method == "POST" and demo_mode_enabled(request):
        return _reject_demo_write(request)
    current_window = current_event_window(target=timezone.now().astimezone(dt_timezone.utc).date())
    current_respec = PlayerBotRespecWindow.objects.filter(
        player=player,
        window_start=current_window.start,
        window_end=current_window.end,
    ).first()
    player_cards = tuple(
        PlayerCard.objects.filter(player=player, stars_unlocked__gt=0).select_related("card_definition")
    )

    if not demo_mode_enabled(request):
        orphaned_bot_params_deleted, _ = PlayerBotParameter.objects.filter(
            player_bot__player=player,
            parameter_definition__isnull=True,
        ).delete()
        if orphaned_bot_params_deleted and not request.headers.get("x-requested-with") == "XMLHttpRequest":
            messages.warning(request, "Removed bot parameter rows that no longer match known definitions.")

    bot_definitions = list(BotDefinition.objects.order_by("name"))
    if not demo_mode_enabled(request):
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
        redirect_response = safe_redirect(
            request,
            candidates=[request.POST.get("next"), request.META.get("HTTP_REFERER")],
            fallback=request.path,
        )

        if action == "mark_bot_respec_used":
            if current_respec is None:
                with transaction.atomic():
                    reset_summary = _apply_bot_respec_reset(player=player)
                    current_respec = PlayerBotRespecWindow.objects.create(
                        player=player,
                        window_start=current_window.start,
                        window_end=current_window.end,
                    )
                messages.success(
                    request,
                    (
                        "Bot Respec recorded for the current event window. "
                        f"Locked {reset_summary['bots_locked']} bots, reset "
                        f"{reset_summary['levels_reset']} bot parameter rows, and cleared "
                        f"{reset_summary['goals_cleared']} bot goals."
                    ),
                )
            else:
                messages.warning(
                    request,
                    "Bot Respec is already marked as used for the current event window.",
                )
            return redirect_response

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
                return redirect_response

            try:
                validate_parameter_definitions(
                    parameter_definitions=bot.bot_definition.parameter_definitions,
                    expected_count=4,
                    entity_kind="bot",
                    entity_slug=bot.bot_definition.slug,
                )
            except ValueError:
                if settings.DEBUG:
                    raise
                messages.warning(
                    request,
                    f"Skipping {bot.bot_definition.name}: invalid parameter definitions.",
                )
                if is_ajax:
                    return JsonResponse(
                        {"ok": False, "error": "Invalid parameter definitions."},
                        status=400,
                    )
                return redirect_response

            with transaction.atomic():
                bot.unlocked = True
                bot.save(update_fields=["unlocked", "updated_at"])
                for param_def in bot.bot_definition.parameter_definitions.all():
                    player_param, created_param = PlayerBotParameter.objects.get_or_create(
                        player=player,
                        player_bot=bot,
                        parameter_definition=param_def,
                        defaults={"level": 0},
                    )
                    if not created_param and player_param.level < 0:
                        player_param.level = 0
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
                    levels = levels_with_baseline_zero(
                        [
                        ParameterLevelRow(level=row.level, value_raw=row.value_raw, cost_raw=row.cost_raw)
                        for row in param_def.levels.order_by("level")
                        ]
                    )
                    param_view = build_upgradeable_parameter_view(
                        player=player,
                        entity_kind="bot",
                        player_param=player_param,
                        levels=levels,
                        unit_kind=param_def.unit_kind,
                        player_cards=player_cards,
                    )
                    total_medals += total_currency_invested_from_level_zero(
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
            return redirect_response

        if action == "level_up_bot_param":
            player_param_id = int(request.POST.get("param_id") or 0)
            player_param = (
                PlayerBotParameter.objects.filter(player=player, id=player_param_id)
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
                return redirect_response

            if not player_param.player_bot.unlocked:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Bot is locked."}, status=400)
                messages.error(request, "Cannot upgrade a locked Bot.")
                return redirect_response

            param_def = player_param.parameter_definition
            levels_qs = param_def.levels.order_by("level")
            max_level = levels_qs.values_list("level", flat=True).last() or 0
            if player_param.level >= max_level:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Already at max level."}, status=400)
                messages.warning(request, "That parameter is already maxed.")
                return redirect_response

            with transaction.atomic():
                player_param.level += 1
                player_param.save(update_fields=["level", "updated_at"])

            if is_ajax:
                levels = levels_with_baseline_zero(
                    [
                    ParameterLevelRow(level=row.level, value_raw=row.value_raw, cost_raw=row.cost_raw)
                    for row in levels_qs
                    ]
                )
                param_view = build_upgradeable_parameter_view(
                    player=player,
                    entity_kind="bot",
                    player_param=player_param,
                    levels=levels,
                    unit_kind=param_def.unit_kind,
                    player_cards=player_cards,
                )
                total_medals = total_currency_invested_from_level_zero(
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
            return redirect_response

        if action == "level_down_bot_param":
            player_param_id = int(request.POST.get("param_id") or 0)
            player_param = (
                PlayerBotParameter.objects.filter(player=player, id=player_param_id)
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
                return redirect_response

            if not player_param.player_bot.unlocked:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Bot is locked."}, status=400)
                messages.error(request, "Cannot change levels on a locked Bot.")
                return redirect_response

            param_def = player_param.parameter_definition
            levels_qs = param_def.levels.order_by("level")
            min_level = 0
            if player_param.level <= min_level:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "Already at minimum level."}, status=400)
                messages.warning(request, "That parameter is already at its minimum level.")
                return redirect_response

            with transaction.atomic():
                player_param.level -= 1
                player_param.save(update_fields=["level", "updated_at"])

            if is_ajax:
                levels = levels_with_baseline_zero(
                    [
                    ParameterLevelRow(level=row.level, value_raw=row.value_raw, cost_raw=row.cost_raw)
                    for row in levels_qs
                    ]
                )
                param_view = build_upgradeable_parameter_view(
                    player=player,
                    entity_kind="bot",
                    player_param=player_param,
                    levels=levels,
                    unit_kind=param_def.unit_kind,
                    player_cards=player_cards,
                )
                total_medals = total_currency_invested_from_level_zero(
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

            messages.success(request, f"Decreased {param_def.display_name}.")
            return redirect_response

        if is_ajax:
            return JsonResponse({"ok": False, "error": "Unknown action."}, status=400)
        messages.error(request, "Unknown action.")
        return redirect_response

    filter_form = UpgradeableEntityProgressFilterForm(request.GET, entity_label_plural="bots")
    filter_form.is_valid()
    status = (filter_form.cleaned_data.get("status") or "").strip()
    name_query = (filter_form.cleaned_data.get("q") or "").strip()

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
            player_param, created_param = PlayerBotParameter.objects.get_or_create(
                player=player,
                player_bot=bot,
                parameter_definition=param_def,
                defaults={"level": 0},
            )
            if not created_param and player_param.level < 0:
                player_param.level = 0
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
    if name_query:
        bots_qs = bots_qs.filter(bot_definition__name__icontains=name_query)

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
            levels = levels_with_baseline_zero(levels)
            view = build_upgradeable_parameter_view(
                player=player,
                entity_kind="bot",
                player_param=player_param,
                levels=levels,
                unit_kind=param_def.unit_kind,
                player_cards=player_cards,
            )
            total_medals_invested += total_currency_invested_from_level_zero(
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
        runs_muted = bot_def.slug == "amplify_bot"
        runs_tooltip = (
            "Runs Used cannot be tracked yet for Amplify Bot."
            if runs_muted
            else ""
        )

        tiles.append(
            {
                "id": bot.id,
                "name": bot_def.name,
                "slug": bot_def.slug,
                "wiki_page_url": (bot_def.wiki_page_url or ""),
                "description": ((bot_def.description or "").splitlines() or [""])[0].strip(),
                "unlocked": bot.unlocked,
                "unlock_cost_raw": None,
                "summary": {
                    "total_invested": total_medals_invested,
                    "headline_label": "Runs used",
                    "headline_value": "—" if runs_muted else runs_count,
                    "headline_empty": (not any_battles),
                    "headline_muted": runs_muted,
                    "headline_tooltip": runs_tooltip,
                },
                "parameters": parameters,
            }
        )

    return render(
        request,
        "core/bots_progress.html",
        {
            "filter_form": filter_form,
            "bots": tiles,
            "bot_respec": {
                "available": current_respec is None,
                "used_at": current_respec.used_at if current_respec is not None else None,
                "window_start": current_window.start,
                "window_end": current_window.end,
            },
            "goals_widget_rows": goals_widget_rows(player=player, goal_type=str(GoalType.BOT)),
            "goals_widget_goal_type": str(GoalType.BOT),
        },
    )


def _apply_bot_respec_reset(*, player: Player) -> dict[str, int]:
    """Reset bot progression to the locked baseline used after an in-game respec.

    Args:
        player: Owning player whose bot state should be reset.

    Returns:
        A summary of the rows affected for user-facing confirmation.
    """

    levels_reset = PlayerBotParameter.objects.filter(
        player=player,
    ).exclude(level=0).update(level=0)
    bots_locked = PlayerBot.objects.filter(
        player=player,
        unlocked=True,
    ).update(unlocked=False)
    goals_cleared, _ = GoalTarget.objects.filter(
        player=player,
        goal_type=str(GoalType.BOT),
    ).delete()
    return {
        "levels_reset": levels_reset,
        "bots_locked": bots_locked,
        "goals_cleared": goals_cleared,
    }


def _calculator_run_label(run: BattleReport) -> str:
    """Return a concise run label for calculator dropdowns."""

    progress = getattr(run, "run_progress", None)
    battle_date = getattr(progress, "battle_date", None)
    tier = getattr(progress, "tier", None)
    wave = getattr(progress, "wave", None)
    date_label = getattr(battle_date, "date", lambda: None)()
    time_label = getattr(battle_date, "strftime", lambda _fmt: None)("%H:%M:%S")
    tier_label = f"T{tier}" if tier is not None else "T?"
    wave_label = f"W{wave}" if wave is not None else "W?"
    if date_label is None:
        date_label = run.parsed_at.date()
    if time_label is None:
        time_label = run.parsed_at.strftime("%H:%M:%S")
    return f"{tier_label} • {wave_label} • {date_label.isoformat()} {time_label}"


@login_required
def calculator_tools(request: HttpRequest) -> HttpResponse:
    """Render the Calculator Tools dashboard."""

    player = _request_player(request)
    runs_qs = BattleReport.objects.filter(player=player).select_related("run_progress")
    runs_qs = _with_effective_battle_date(runs_qs).order_by("-effective_battle_date", "-id")
    last_run_ids = list(runs_qs.values_list("id", flat=True)[:5])
    runs_for_form = runs_qs.filter(id__in=last_run_ids) if last_run_ids else runs_qs.none()

    game_prefix = "game_speed"
    labs_prefix = "labs_speed"
    calculator = str(request.GET.get("calculator") or "")
    has_game = calculator == game_prefix or any(key.startswith(f"{game_prefix}-") for key in request.GET.keys())
    has_labs = calculator == labs_prefix or any(key.startswith(f"{labs_prefix}-") for key in request.GET.keys())

    game_form = GameSpeedCalculatorForm(
        request.GET if has_game else None,
        runs=runs_for_form,
        prefix=game_prefix,
    )
    labs_form = LabsSpeedupCalculatorForm(
        request.GET if has_labs else None,
        prefix=labs_prefix,
    )

    game_result: dict[str, object] | None = None
    if has_game and game_form.is_valid():
        run = game_form.cleaned_data["run"]
        speed_value = float(game_form.cleaned_data["game_speed"])
        wave_accelerator_active = bool(game_form.cleaned_data.get("wave_accelerator_active"))
        card_reduction_pct = wave_accelerator_reduction_percent(player=player)
        applied_reduction_pct = card_reduction_pct if wave_accelerator_active else 0.0
        progress = getattr(run, "run_progress", None)
        waves = getattr(progress, "wave", None) if progress else None
        real_time_seconds = getattr(progress, "real_time_seconds", None) if progress else None

        result = build_game_speed_result(
            waves=waves,
            real_time_seconds=real_time_seconds,
            game_speed=speed_value,
            wave_accelerator_active=wave_accelerator_active,
            reduction_pct=applied_reduction_pct,
        )
        expected_seconds = result.expected_real_time_seconds
        game_result = {
            "run_label": _calculator_run_label(run),
            "waves": waves,
            "real_time_seconds": real_time_seconds,
            "real_time_label": format_duration(total_seconds=int(real_time_seconds or 0))
            if real_time_seconds
            else "—",
            "expected_real_time_seconds": expected_seconds,
            "expected_real_time_label": format_duration(total_seconds=int(expected_seconds or 0))
            if expected_seconds
            else "—",
            "waves_per_hour": result.waves_per_hour,
            "expected_waves_per_hour": result.expected_waves_per_hour,
            "derived_speed": result.derived_speed,
            "seconds_per_wave": result.seconds_per_wave,
            "cooldown_seconds": result.cooldown_seconds,
            "cooldown_reduction_pct": round(card_reduction_pct, 2),
            "wave_accelerator_active": wave_accelerator_active,
        }

    labs_result: dict[str, object] | None = None
    if has_labs and labs_form.is_valid():
        labs_unlocked = int(labs_form.cleaned_data["labs_unlocked"])
        current_seconds = progress_seconds_from_parts(
            days=int(labs_form.cleaned_data.get("progress_days") or 0),
            hours=int(labs_form.cleaned_data.get("progress_hours") or 0),
            minutes=int(labs_form.cleaned_data.get("progress_minutes") or 0),
            seconds=int(labs_form.cleaned_data.get("progress_seconds") or 0),
        )
        goal_key = str(labs_form.cleaned_data.get("goal") or "")
        goal_lookup = {goal.key: goal for goal in LAB_GOALS}
        goal = goal_lookup.get(goal_key, LAB_GOALS[0])
        remaining_seconds = max(goal.total_seconds - current_seconds, 0)
        utc_now = timezone.now().astimezone(dt_timezone.utc)
        event_window = current_event_window(target=utc_now.date())
        deadline = datetime.combine(
            event_window.end + timedelta(days=1),
            time(0, 0),
            tzinfo=dt_timezone.utc,
        )
        remaining_window_seconds = max(int((deadline - utc_now).total_seconds()), 0)
        labs_for_calc = max(1, labs_unlocked)
        baseline_research_seconds = remaining_window_seconds * labs_for_calc
        shortfall_seconds = max(remaining_seconds - baseline_research_seconds, 0)
        rows = lab_speedup_rows(
            remaining_seconds=shortfall_seconds,
            labs_unlocked=labs_for_calc,
            available_seconds=remaining_window_seconds,
        )
        rows_payload = [
            {
                "boost": row.boost,
                "duration_hours": row.duration_hours,
                "boosts_needed": row.boosts_needed,
                "total_cells": row.total_cells,
                "research_duration": format_duration_dhms(total_seconds=row.research_seconds),
                "max_boosts": row.max_boosts,
                "possible_by_deadline": row.possible_by_deadline,
            }
            for row in rows
        ]
        pending_lab_costs = [
            (lab_num, cost) for lab_num, cost in LAB_UNLOCK_COSTS if lab_num > labs_unlocked
        ]
        labs_result = {
            "goal_label": goal.label,
            "goal_seconds": goal.total_seconds,
            "goal_duration": format_duration(total_seconds=goal.total_seconds),
            "current_seconds": current_seconds,
            "current_duration": format_duration(total_seconds=current_seconds),
            "remaining_seconds": remaining_seconds,
            "remaining_duration": format_duration(total_seconds=remaining_seconds),
            "shortfall_seconds": shortfall_seconds,
            "shortfall_duration": format_duration_dhms(total_seconds=shortfall_seconds),
            "deadline_date": event_window.end.isoformat(),
            "deadline_label": deadline.strftime("%Y-%m-%d %H:%M UTC"),
            "deadline_duration": format_duration_dhms(total_seconds=remaining_window_seconds),
            "labs_unlocked": labs_unlocked,
            "rows": rows_payload,
            "pending_lab_costs": pending_lab_costs,
        }

    return render(
        request,
        "core/calculator_tools.html",
        {
            "game_form": game_form,
            "labs_form": labs_form,
            "game_result": game_result,
            "labs_result": labs_result,
            "has_runs": bool(last_run_ids),
        },
    )


@login_required
def goals_dashboard(request: HttpRequest) -> HttpResponse:
    """Render the Goals dashboard for upgrade targets."""

    player = _request_player(request)
    if request.method == "POST" and demo_mode_enabled(request):
        return _reject_demo_write(request)

    filter_form = GoalsFilterForm(request.GET)
    filter_form.is_valid()
    selected_goal_type = str(filter_form.cleaned_data.get("goal_type") or "").strip() or None
    show_completed = bool(filter_form.cleaned_data.get("show_completed") or False)

    all_rows_by_type = goal_rows_for_dashboard(player=player, goal_type=selected_goal_type, show_completed=True)
    row_index: dict[tuple[str, str], GoalRow] = {}
    for rows in all_rows_by_type.values():
        for row in rows:
            row_index[(row.goal_type, row.goal_key)] = row

    candidates = goal_candidates_for_modal(player=player, goal_type=selected_goal_type)
    candidates_payload = [
        {
            "goal_type": c.goal_type,
            "goal_key": c.goal_key,
            "label": c.label,
            "currency": c.currency,
            "max_level": c.max_level,
            "target_options": list(c.target_options),
        }
        for c in candidates
    ]
    candidate_index: dict[str, GoalCandidate] = {c.goal_key: c for c in candidates}

    if request.method == "POST":
        action = (request.POST.get("action") or "").strip()
        redirect_response = safe_redirect(
            request,
            candidates=[request.POST.get("next"), request.META.get("HTTP_REFERER")],
            fallback=request.path,
        )

        if action == "clear_goal":
            goal_type = (request.POST.get("goal_type") or "").strip()
            goal_key = (request.POST.get("goal_key") or "").strip()
            deleted, _ = GoalTarget.objects.filter(
                player=player,
                goal_type=goal_type,
                goal_key=goal_key,
            ).delete()
            if deleted:
                messages.success(request, "Goal cleared.")
            else:
                messages.warning(request, "Goal not found.")
            return redirect_response

        if action in {"create_goal", "update_goal", "set_goal_max"}:
            goal_type = (request.POST.get("goal_type") or "").strip()
            goal_key = (request.POST.get("goal_key") or "").strip()
            selected_row = row_index.get((goal_type, goal_key))

            if action == "set_goal_max":
                if selected_row is None:
                    messages.error(request, "Goal target not found.")
                    return redirect_response
                target_level = int(selected_row.max_level or 0)
                existing = GoalTarget.objects.filter(player=player, goal_type=goal_type, goal_key=goal_key).first()
                notes = existing.notes if existing else ""
                if target_level <= 0:
                    messages.error(request, "Max level is unavailable for that parameter.")
                    return redirect_response
            else:
                max_level = None
                if selected_row is not None:
                    max_level = int(selected_row.max_level or 0) or None
                elif action == "create_goal":
                    candidate = candidate_index.get(goal_key)
                    max_level = int(candidate.max_level) if candidate else None
                form = GoalTargetUpdateForm(request.POST, max_level=max_level)
                if not form.is_valid():
                    messages.error(request, "Unable to save goal. Check target level and try again.")
                    return redirect_response
                target_level = int(form.cleaned_data["target_level"])
                if "notes" in request.POST:
                    notes = str(form.cleaned_data.get("notes") or "")
                else:
                    existing = GoalTarget.objects.filter(
                        player=player, goal_type=goal_type, goal_key=goal_key
                    ).first()
                    notes = existing.notes if existing else ""

            is_assumed = bool(getattr(selected_row, "current_is_assumed", False)) if selected_row is not None else False
            assumed_current_level = 0 if is_assumed else None

            GoalTarget.objects.update_or_create(
                player=player,
                goal_type=goal_type,
                goal_key=goal_key,
                defaults={
                    "target_level": target_level,
                    "notes": notes,
                    "assumed_current_level": assumed_current_level,
                    "is_current_level_assumed": is_assumed,
                },
            )
            messages.success(request, "Goal saved.")
            return redirect_response

        messages.error(request, "Unknown action.")
        return redirect_response

    display_rows_by_type = {
        kind: tuple(rows if show_completed else [row for row in rows if not row.is_completed])
        for kind, rows in all_rows_by_type.items()
    }
    category_labels: dict[str, str] = {
        str(GoalType.BOT): "Bots",
        str(GoalType.GUARDIAN_CHIP): "Guardian Chips",
        str(GoalType.ULTIMATE_WEAPON): "Ultimate Weapons",
    }
    sections = [
        {"kind": kind, "label": category_labels.get(kind, kind), "rows": rows}
        for kind, rows in display_rows_by_type.items()
    ]

    return render(
        request,
        "core/goals_dashboard.html",
        {
            "filter_form": filter_form,
            "sections": sections,
            "show_completed": show_completed,
            "goal_candidates": candidates_payload,
        },
    )


def _filtered_runs(filter_form: ChartContextForm, *, player: Player) -> QuerySet[BattleReport]:
    """Return a filtered BattleReport queryset based on validated form data."""

    runs = _with_effective_battle_date(
        BattleReport.objects.filter(player=player)
        .select_related(
            "run_progress",
            "run_progress__preset",
        )
        .prefetch_related(
            "run_bots__bot_definition",
            "run_guardians__guardian_chip_definition",
            "run_combat_uws__ultimate_weapon_definition",
            "run_utility_uws__ultimate_weapon_definition",
        )
    ).order_by("effective_battle_date", "id")
    valid = filter_form.is_valid()
    snapshot = filter_form.cleaned_data.get("context_snapshot") if valid else None
    snapshot_context = _snapshot_context_from_filter(snapshot)
    tournament_filter = filter_form.cleaned_data.get("tournament_filter") if valid else None
    force_tournaments = bool(tournament_filter) or bool(
        snapshot_context and (snapshot_context.tournament_filter or snapshot_context.include_tournaments)
    )
    include_tournaments = bool(valid and (filter_form.cleaned_data.get("include_tournaments") or False))
    include_dissonance = bool(valid and (filter_form.cleaned_data.get("include_dissonance") or False))
    runs = _exclude_special_runs(
        runs,
        include_tournaments=bool(include_tournaments or force_tournaments),
        include_dissonance=include_dissonance,
    )
    include_hidden = bool(valid and (filter_form.cleaned_data.get("include_hidden") or False))
    force_hidden = bool(snapshot_context and snapshot_context.include_hidden)
    if not include_hidden and not force_hidden:
        runs = runs.filter(is_hidden=False)
    if not valid:
        return runs

    start_date = filter_form.cleaned_data.get("start_date")
    end_date = filter_form.cleaned_data.get("end_date")
    tier = filter_form.cleaned_data.get("tier")
    preset = filter_form.cleaned_data.get("preset")
    exclude_presets = tuple(filter_form.cleaned_data.get("exclude_presets") or ())
    patch_boundaries = tuple(filter_form.cleaned_data.get("patch_boundaries") or ())
    window_kind = filter_form.cleaned_data.get("window_kind")
    window_n = filter_form.cleaned_data.get("window_n")
    if start_date:
        runs = runs.filter(effective_battle_date__date__gte=start_date)
    if end_date:
        runs = runs.filter(effective_battle_date__date__lte=end_date)
    if tier:
        runs = runs.filter(run_progress__tier=tier)
    if preset:
        runs = runs.filter(run_progress__preset=preset)
    if exclude_presets:
        runs = runs.exclude(run_progress__preset__in=exclude_presets)
    runs = _apply_tournament_filter(runs, tournament_filter=tournament_filter)
    runs = _apply_snapshot_context_filters(runs, snapshot_context=snapshot_context)
    if patch_boundaries:
        boundary_dates = [boundary.boundary_date for boundary in patch_boundaries]
        runs = _apply_patch_boundary_filters(runs, boundary_dates=boundary_dates)
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

    runs = _with_effective_battle_date(runs)
    if kind == "last_runs":
        ids = list(
            runs.order_by("-effective_battle_date").values_list("id", flat=True)[:n]
        )
        if not ids:
            return runs.none()
        return runs.filter(id__in=ids).order_by("effective_battle_date")

    if kind == "last_days":
        if end_date is not None:
            window_end = end_date
        else:
            latest = runs.aggregate(latest=Max("effective_battle_date"))["latest"]
            if latest is None:
                return runs.none()
            window_end = latest.date()
        window_start = window_end - timedelta(days=max(n - 1, 0))
        return runs.filter(effective_battle_date__date__gte=window_start)

    return runs


def _patch_boundary_window_map() -> dict[date, date | None]:
    """Return a mapping of patch boundary dates to their next boundary date."""

    boundary_dates = list(
        PatchBoundary.objects.values_list("boundary_date", flat=True).order_by("boundary_date")
    )
    window_map: dict[date, date | None] = {}
    for idx, boundary_date in enumerate(boundary_dates):
        next_date = boundary_dates[idx + 1] if idx + 1 < len(boundary_dates) else None
        window_map[boundary_date] = next_date
    return window_map


def _apply_patch_boundary_filters(
    runs: QuerySet[BattleReport],
    *,
    boundary_dates: Sequence[date],
) -> QuerySet[BattleReport]:
    """Apply patch boundary windows to a run queryset.

    Args:
        runs: BattleReport queryset with effective_battle_date annotations.
        boundary_dates: Selected patch boundary dates.

    Returns:
        QuerySet filtered to any of the selected patch windows.
    """

    if not boundary_dates:
        return runs
    window_map = _patch_boundary_window_map()
    selected = [value for value in boundary_dates if value in window_map]
    if not selected:
        return runs.none()
    query = Q()
    for boundary_date in selected:
        window_query = Q(effective_battle_date__date__gte=boundary_date)
        window_end = window_map.get(boundary_date)
        if window_end is not None:
            window_query &= Q(effective_battle_date__date__lt=window_end)
        query |= window_query
    return runs.filter(query)


def _resolve_patch_boundary_tokens(tokens: Iterable[object]) -> list[PatchBoundary]:
    """Resolve patch boundary tokens by label or ISO date string.

    Args:
        tokens: Iterable of raw token values from DSL or form filters.

    Returns:
        List of matching PatchBoundary rows.
    """

    boundaries: list[PatchBoundary] = []
    for token in tokens:
        raw = str(token or "").strip()
        if not raw:
            continue
        boundary = PatchBoundary.objects.filter(label__iexact=raw).first()
        if boundary is None:
            try:
                boundary_date = date.fromisoformat(raw)
            except ValueError:
                boundary_date = None
            if boundary_date is not None:
                boundary = PatchBoundary.objects.filter(boundary_date=boundary_date).first()
        if boundary is not None:
            boundaries.append(boundary)
    seen: set[date] = set()
    unique: list[PatchBoundary] = []
    for boundary in boundaries:
        if boundary.boundary_date in seen:
            continue
        seen.add(boundary.boundary_date)
        unique.append(boundary)
    return unique


def _format_patch_boundary_label(boundary: PatchBoundary) -> str:
    """Return a display label for a patch boundary selection."""

    label = (boundary.label or "").strip()
    date_label = boundary.boundary_date.isoformat()
    if label:
        return f"{label} ({date_label})"
    return date_label


def _apply_tournament_filter(
    runs: QuerySet[BattleReport], *, tournament_filter: str | None
) -> QuerySet[BattleReport]:
    """Apply a tournament filter to a run queryset.

    Args:
        runs: BattleReport queryset already scoped by player and date filters.
        tournament_filter: "all" for all tournaments or a rank key.

    Returns:
        QuerySet filtered to tournament runs (optionally by rank).
    """

    if not tournament_filter:
        return runs
    filtered = runs.filter(run_progress__is_tournament=True)
    if tournament_filter != "all":
        filtered = filtered.filter(run_progress__tournament_rank=tournament_filter)
    return filtered


def _snapshot_context_from_filter(snapshot: ChartSnapshot | None) -> ChartContextDTO | None:
    """Return a ChartContextDTO for a snapshot-based filter selection."""

    if snapshot is None:
        return None
    if snapshot.config:
        try:
            return decode_chart_config_dto(dict(snapshot.config)).context
        except ValueError:
            return None
    raw_context = dict(snapshot.chart_context or {})
    if not raw_context:
        return None
    raw_patch_boundaries = raw_context.get("patch_boundaries")
    patch_boundaries = []
    if isinstance(raw_patch_boundaries, list):
        for value in raw_patch_boundaries:
            parsed = _parse_context_date(value)
            if parsed is not None:
                patch_boundaries.append(parsed)
    return ChartContextDTO(
        start_date=_parse_context_date(raw_context.get("start_date")),
        end_date=_parse_context_date(raw_context.get("end_date")),
        tier=_parse_context_int(raw_context.get("tier")),
        tournament_filter=_parse_context_str(raw_context.get("tournament_filter")),
        preset_id=_parse_context_int(raw_context.get("preset_id") or raw_context.get("preset")),
        excluded_preset_ids=_parse_context_int_list(
            raw_context.get("excluded_preset_ids") or raw_context.get("exclude_presets")
        ),
        include_tournaments=_parse_context_bool(raw_context.get("include_tournaments")),
        include_dissonance=_parse_context_bool(raw_context.get("include_dissonance")),
        include_hidden=_parse_context_bool(raw_context.get("include_hidden")),
        patch_boundaries=tuple(patch_boundaries),
    )


def _apply_snapshot_context_filters(
    runs: QuerySet[BattleReport], *, snapshot_context: ChartContextDTO | None
) -> QuerySet[BattleReport]:
    """Apply snapshot context filters to an existing queryset."""

    if snapshot_context is None:
        return runs
    if not snapshot_context.include_hidden:
        runs = runs.filter(is_hidden=False)
    if snapshot_context.start_date:
        runs = runs.filter(effective_battle_date__date__gte=snapshot_context.start_date)
    if snapshot_context.end_date:
        runs = runs.filter(effective_battle_date__date__lte=snapshot_context.end_date)
    if snapshot_context.tier:
        runs = runs.filter(run_progress__tier=snapshot_context.tier)
    if snapshot_context.preset_id:
        runs = runs.filter(run_progress__preset_id=snapshot_context.preset_id)
    if snapshot_context.excluded_preset_ids:
        runs = runs.exclude(run_progress__preset_id__in=snapshot_context.excluded_preset_ids)
    if snapshot_context.patch_boundaries:
        runs = _apply_patch_boundary_filters(
            runs,
            boundary_dates=snapshot_context.patch_boundaries,
        )
    return _apply_tournament_filter(runs, tournament_filter=snapshot_context.tournament_filter)


def _parse_context_date(value: object) -> date | None:
    """Parse optional date values from snapshot context payloads."""

    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _parse_context_int(value: object) -> int | None:
    """Parse optional int values from snapshot context payloads."""

    if value is None or value == "":
        return None
    try:
        return int(str(value))
    except ValueError:
        return None


def _parse_context_int_list(value: object) -> tuple[int, ...]:
    """Parse a list of int values from snapshot context payloads."""

    if value is None:
        return ()
    if isinstance(value, (list, tuple, set)):
        parsed: list[int] = []
        for entry in value:
            item = _parse_context_int(entry)
            if item is None:
                continue
            parsed.append(item)
        return tuple(parsed)
    return ()


def _parse_context_bool(value: object) -> bool:
    """Parse optional bool values from snapshot context payloads."""

    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().casefold() in {"1", "true", "yes", "on"}


def _parse_context_str(value: object) -> str | None:
    """Parse optional string values from snapshot context payloads."""

    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _explore_form_initial_from_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return form initial values derived from a stored Explore payload."""

    scope_raw = payload.get("scope")
    scope = scope_raw if isinstance(scope_raw, dict) else {}
    date_range_raw = scope.get("date_range")
    date_range = date_range_raw if isinstance(date_range_raw, dict) else {}
    metrics_raw = payload.get("metrics")
    metric_entries = [
        entry
        for entry in (metrics_raw if isinstance(metrics_raw, list) else [])
        if isinstance(entry, dict)
    ]
    metric = metric_entries[0] if metric_entries else {}
    if not metric:
        metric_raw = payload.get("metric")
        metric = metric_raw if isinstance(metric_raw, dict) else {}
    breakdowns_raw = payload.get("breakdowns")
    breakdown_entries = [
        entry
        for entry in (breakdowns_raw if isinstance(breakdowns_raw, list) else [])
        if isinstance(entry, dict)
    ]
    breakdowns = sorted(
        breakdown_entries,
        key=lambda entry: int(entry.get("order") or 0),
    )

    initial: dict[str, object] = {
        "name": payload.get("name") or "",
        "start_date": date_range.get("start") or "",
        "end_date": date_range.get("end") or "",
        "preset": scope.get("preset") or "",
        "snapshot": scope.get("snapshot") or "",
        "past_n_runs": scope.get("past_n_runs") or "",
        "include_hidden": bool(scope.get("include_hidden")),
        "metric_key": metric.get("key") or "",
        "aggregation": metric.get("aggregation") or "sum",
        "percent_of_total": bool(metric.get("percent_of_total")) if isinstance(metric, dict) else False,
        "visualization": payload.get("visualization_hint") or "table",
    }

    if breakdowns:
        initial["primary_breakdown"] = breakdowns[0].get("dimension") or ""
    if len(breakdowns) > 1:
        initial["secondary_breakdown"] = breakdowns[1].get("dimension") or ""

    tier_values: list[str] = []
    filters_raw = payload.get("filters")
    filter_entries = [
        entry
        for entry in (filters_raw if isinstance(filters_raw, list) else [])
        if isinstance(entry, dict)
    ]
    for entry in filter_entries:
        field = entry.get("field")
        operator = entry.get("operator")
        value = entry.get("value")
        if field == "tier" and operator == "in" and isinstance(value, list):
            tier_values = [str(v) for v in value if v is not None]
        if field == "tier" and operator == ">=":
            initial["tier_min"] = value
        if field == "tier" and operator == "<=":
            initial["tier_max"] = value
        if field == "wave" and operator == ">=":
            initial["wave_min"] = value
        if field == "wave" and operator == "<=":
            initial["wave_max"] = value
        if field == "wave" and operator == "range" and isinstance(value, dict):
            initial["wave_min"] = value.get("min")
            initial["wave_max"] = value.get("max")
        if field == "death_cause":
            initial["death_cause"] = value or "__missing__"
        if field == "patch_boundary" and operator == "in" and isinstance(value, list):
            boundaries = _resolve_patch_boundary_tokens(value)
            if boundaries:
                initial["patch_boundaries"] = [boundary.id for boundary in boundaries]
        if field == "date_range" and operator == "range" and isinstance(value, dict):
            initial["start_date"] = value.get("start") or initial.get("start_date") or ""
            initial["end_date"] = value.get("end") or initial.get("end_date") or ""
        if field == "preset" and operator == "=":
            initial["preset"] = value or ""
    if tier_values:
        initial["tier_values"] = tier_values

    return initial


def _explore_form_initial_from_request(params: QueryDict) -> dict[str, object]:
    """Return form initial values from Explore query parameters."""

    initial: dict[str, object] = {}
    tier_values = [value for value in params.getlist("tier_values") if value]
    if tier_values:
        initial["tier_values"] = tier_values
    for field in ("start_date", "end_date", "preset", "snapshot", "past_n_runs", "death_cause"):
        if params.get(field):
            initial[field] = params.get(field)
    if params.get("include_hidden"):
        initial["include_hidden"] = _parse_context_bool(params.get("include_hidden"))
    patch_boundaries = [value for value in params.getlist("patch_boundaries") if value]
    if patch_boundaries:
        boundaries = _resolve_patch_boundary_tokens(patch_boundaries)
        if boundaries:
            initial["patch_boundaries"] = [boundary.id for boundary in boundaries]
    return initial


def _explore_prefill_scope_from_request(params: QueryDict) -> ExploreScope:
    """Return Explore scope defaults derived from query parameters."""

    start_date = _parse_context_date(params.get("start_date"))
    end_date = _parse_context_date(params.get("end_date"))
    tier = _parse_context_int(params.get("tier"))
    preset_id = _parse_context_int(params.get("preset") or params.get("preset_id"))
    snapshot_id = _parse_context_int(params.get("snapshot"))
    past_n_runs = _parse_context_int(params.get("past_n_runs"))
    include_hidden = _parse_context_bool(params.get("include_hidden"))
    return ExploreScope(
        start_date=start_date,
        end_date=end_date,
        tier=tier,
        preset_id=preset_id,
        snapshot_id=snapshot_id,
        past_n_runs=past_n_runs,
        include_hidden=include_hidden,
    )


_EXPLORE_JUST_SAVED_SESSION_KEY = "explore_just_saved_query_id"


def _consume_explore_just_saved_query_id(request: HttpRequest) -> int | None:
    """Return and clear the just-saved Explore query id from the session."""

    raw_value = request.session.pop(_EXPLORE_JUST_SAVED_SESSION_KEY, None)
    if raw_value is None:
        return None
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        return None


def _explore_payload_dsl_text(payload: dict[str, object] | None) -> str | None:
    """Return stored DSL text from an Explore payload when present."""

    if not payload:
        return None
    raw_value = payload.get("dsl_text")
    if isinstance(raw_value, str) and raw_value.strip():
        return raw_value
    return None


def _explore_payload_with_dsl(
    payload: dict[str, object] | None,
    dsl_text: str | None,
) -> dict[str, object]:
    """Return an Explore payload enriched with raw DSL text."""

    enriched = dict(payload or {})
    if dsl_text is not None and dsl_text.strip():
        enriched["dsl_text"] = dsl_text
    return enriched


def _explore_query_from_payload(payload: dict[str, object]) -> ExploreQuery:
    """Parse a stored Explore payload into a typed ExploreQuery."""

    scope_raw = payload.get("scope")
    scope = scope_raw if isinstance(scope_raw, dict) else {}
    date_range_raw = scope.get("date_range")
    date_range = date_range_raw if isinstance(date_range_raw, dict) else {}
    filters_raw = payload.get("filters")
    filter_entries = [
        entry
        for entry in (filters_raw if isinstance(filters_raw, list) else [])
        if isinstance(entry, dict)
    ]
    filters = tuple(
        ExploreFilter(
            field=str(entry.get("field") or ""),
            operator=cast(FilterOperator, str(entry.get("operator") or "=")),
            value=entry.get("value"),
        )
        for entry in filter_entries
    )
    breakdowns_raw = payload.get("breakdowns")
    breakdown_entries = [
        entry
        for entry in (breakdowns_raw if isinstance(breakdowns_raw, list) else [])
        if isinstance(entry, dict)
    ]
    breakdowns = tuple(
        ExploreBreakdown(
            dimension=str(entry.get("dimension") or ""),
            order=int(entry.get("order") or 0),
        )
        for entry in breakdown_entries
    )
    metrics_raw = payload.get("metrics")
    metric_entries = [
        entry
        for entry in (metrics_raw if isinstance(metrics_raw, list) else [])
        if isinstance(entry, dict)
    ]
    if not metric_entries:
        metric_raw = payload.get("metric")
        metric = metric_raw if isinstance(metric_raw, dict) else {}
        metric_entries = [metric] if metric else []
    metrics = tuple(
        ExploreMetricSelection(
            key=str(entry.get("key") or ""),
            aggregation=cast(Literal["sum", "count", "avg"], str(entry.get("aggregation") or "sum")),
            percent_of_total=bool(entry.get("percent_of_total")),
        )
        for entry in metric_entries
        if entry
    )
    return ExploreQuery(
        schema_version=str(payload.get("schema_version") or ""),
        player_id=str(payload.get("player_id") or ""),
        name=str(payload.get("name") or ""),
        scope=ExploreScope(
            start_date=_parse_context_date(date_range.get("start")),
            end_date=_parse_context_date(date_range.get("end")),
            tier=_parse_context_int(scope.get("tier")),
            preset_id=_parse_context_int(scope.get("preset")),
            snapshot_id=_parse_context_int(scope.get("snapshot")),
            past_n_runs=_parse_context_int(scope.get("past_n_runs")),
            include_hidden=_parse_context_bool(scope.get("include_hidden")),
        ),
        filters=filters,
        breakdowns=breakdowns,
        metrics=metrics,
        visualization_hint=cast(
            VisualizationHint,
            str(payload.get("visualization_hint") or "table"),
        ),
    )


def _explore_query_from_form(form: ExploreQueryForm, *, player: Player) -> ExploreQuery:
    """Build an ExploreQuery from validated form data."""

    cleaned = form.cleaned_data
    tier_values = [int(value) for value in cleaned.get("tier_values") or [] if str(value).isdigit()]
    tier_min = cleaned.get("tier_min")
    tier_max = cleaned.get("tier_max")

    scope_tier = None
    if len(tier_values) == 1 and not tier_min and not tier_max:
        scope_tier = tier_values[0]

    scope = ExploreScope(
        start_date=cleaned.get("start_date"),
        end_date=cleaned.get("end_date"),
        tier=scope_tier,
        preset_id=getattr(cleaned.get("preset"), "id", None),
        snapshot_id=getattr(cleaned.get("snapshot"), "id", None),
        past_n_runs=cleaned.get("past_n_runs"),
        include_hidden=bool(cleaned.get("include_hidden") or False),
    )

    filters: list[ExploreFilter] = []
    if cleaned.get("start_date") or cleaned.get("end_date"):
        filters.append(
            ExploreFilter(
                field="date_range",
                operator="range",
                value={
                    "start": cleaned.get("start_date").isoformat() if cleaned.get("start_date") else None,
                    "end": cleaned.get("end_date").isoformat() if cleaned.get("end_date") else None,
                },
            )
        )
    if tier_values:
        filters.append(ExploreFilter(field="tier", operator="in", value=tier_values))
    if tier_min:
        filters.append(ExploreFilter(field="tier", operator=">=", value=int(tier_min)))
    if tier_max:
        filters.append(ExploreFilter(field="tier", operator="<=", value=int(tier_max)))

    wave_min = cleaned.get("wave_min")
    wave_max = cleaned.get("wave_max")
    if wave_min and wave_max:
        filters.append(
            ExploreFilter(field="wave", operator="range", value={"min": int(wave_min), "max": int(wave_max)})
        )
    elif wave_min:
        filters.append(ExploreFilter(field="wave", operator=">=", value=int(wave_min)))
    elif wave_max:
        filters.append(ExploreFilter(field="wave", operator="<=", value=int(wave_max)))

    death_cause = cleaned.get("death_cause")
    if death_cause:
        if death_cause == "__missing__":
            filters.append(ExploreFilter(field="death_cause", operator="=", value=None))
        else:
            filters.append(ExploreFilter(field="death_cause", operator="=", value=str(death_cause)))

    patch_boundaries = tuple(cleaned.get("patch_boundaries") or ())
    if patch_boundaries:
        boundary_tokens = [
            (boundary.label or boundary.boundary_date.isoformat()) for boundary in patch_boundaries
        ]
        filters.append(ExploreFilter(field="patch_boundary", operator="in", value=boundary_tokens))

    preset = cleaned.get("preset")
    if preset is not None:
        filters.append(ExploreFilter(field="preset", operator="=", value=int(preset.id)))

    breakdowns: list[ExploreBreakdown] = []
    primary = str(cleaned.get("primary_breakdown") or "")
    secondary = str(cleaned.get("secondary_breakdown") or "")
    if primary:
        breakdowns.append(ExploreBreakdown(dimension=primary, order=1))
    if secondary:
        breakdowns.append(ExploreBreakdown(dimension=secondary, order=2))

    metric = ExploreMetricSelection(
        key=str(cleaned.get("metric_key") or ""),
        aggregation=cast(Literal["sum", "count", "avg"], str(cleaned.get("aggregation") or "sum")),
        percent_of_total=bool(cleaned.get("percent_of_total")),
    )

    return ExploreQuery(
        schema_version=SCHEMA_VERSION,
        player_id=str(player.id),
        name=str(cleaned.get("name") or "").strip(),
        scope=scope,
        filters=tuple(filters),
        breakdowns=tuple(breakdowns),
        metrics=(metric,),
        visualization_hint=cast(
            VisualizationHint,
            str(cleaned.get("visualization") or "table"),
        ),
    )


def _explore_runs_queryset(*, player: Player) -> QuerySet[BattleReport]:
    """Return a player-scoped Explore queryset with effective dates."""

    runs = BattleReport.objects.filter(player=player).select_related(
        "run_progress",
        "run_progress__preset",
        "derived_metrics",
    )
    runs = _with_effective_battle_date(runs)
    return runs.order_by("effective_battle_date", "id")


def _apply_explore_scope(
    runs: QuerySet[BattleReport],
    *,
    scope: ExploreScope,
    snapshot_id: int | None,
) -> QuerySet[BattleReport]:
    """Apply scope filters to an Explore queryset."""

    snapshot = (
        ChartSnapshot.objects.filter(id=snapshot_id).first()
        if snapshot_id is not None
        else None
    )
    snapshot_context = _snapshot_context_from_filter(snapshot)
    force_tournaments = bool(
        snapshot_context and (snapshot_context.tournament_filter or snapshot_context.include_tournaments)
    )
    force_dissonance = bool(snapshot_context and snapshot_context.include_dissonance)
    runs = _exclude_special_runs(
        runs,
        include_tournaments=force_tournaments,
        include_dissonance=force_dissonance,
    )
    include_hidden = bool(scope.include_hidden or (snapshot_context and snapshot_context.include_hidden))
    if not include_hidden:
        runs = runs.filter(is_hidden=False)
    if scope.start_date:
        runs = runs.filter(effective_battle_date__date__gte=scope.start_date)
    if scope.end_date:
        runs = runs.filter(effective_battle_date__date__lte=scope.end_date)
    if scope.tier:
        runs = runs.filter(run_progress__tier=scope.tier)
    if scope.preset_id:
        runs = runs.filter(run_progress__preset_id=scope.preset_id)
    runs = _apply_snapshot_context_filters(runs, snapshot_context=snapshot_context)
    if scope.past_n_runs:
        runs = _apply_rolling_window(
            runs,
            kind="last_runs",
            n=int(scope.past_n_runs),
            end_date=scope.end_date,
        )
    return runs


def _apply_explore_filters(
    runs: QuerySet[BattleReport],
    *,
    filters: Iterable[ExploreFilter],
) -> QuerySet[BattleReport]:
    """Apply filter entries to an Explore queryset."""

    for entry in filters:
        if entry.field == "tier":
            if entry.operator == "in" and isinstance(entry.value, list):
                values = [int(v) for v in entry.value if str(v).isdigit()]
                if values:
                    runs = runs.filter(run_progress__tier__in=values)
            if entry.operator == ">=" and entry.value is not None:
                value_int = _parse_context_int(entry.value)
                if value_int is not None:
                    runs = runs.filter(run_progress__tier__gte=value_int)
            if entry.operator == "<=" and entry.value is not None:
                value_int = _parse_context_int(entry.value)
                if value_int is not None:
                    runs = runs.filter(run_progress__tier__lte=value_int)
        if entry.field == "wave":
            if entry.operator == "range" and isinstance(entry.value, dict):
                wave_min = _parse_context_int(entry.value.get("min"))
                wave_max = _parse_context_int(entry.value.get("max"))
                if wave_min is not None:
                    runs = runs.filter(run_progress__wave__gte=wave_min)
                if wave_max is not None:
                    runs = runs.filter(run_progress__wave__lte=wave_max)
            if entry.operator == ">=" and entry.value is not None:
                value_int = _parse_context_int(entry.value)
                if value_int is not None:
                    runs = runs.filter(run_progress__wave__gte=value_int)
            if entry.operator == "<=" and entry.value is not None:
                value_int = _parse_context_int(entry.value)
                if value_int is not None:
                    runs = runs.filter(run_progress__wave__lte=value_int)
        if entry.field == "death_cause":
            if entry.value is None:
                runs = runs.filter(Q(run_progress__killed_by__isnull=True) | Q(run_progress__killed_by=""))
            else:
                runs = runs.filter(run_progress__killed_by=str(entry.value))
        if entry.field == "date_range" and isinstance(entry.value, dict):
            start = _parse_context_date(entry.value.get("start"))
            end = _parse_context_date(entry.value.get("end"))
            if start:
                runs = runs.filter(effective_battle_date__date__gte=start)
            if end:
                runs = runs.filter(effective_battle_date__date__lte=end)
        if entry.field == "preset" and entry.value is not None:
            preset_id = _parse_context_int(entry.value)
            if preset_id is not None:
                runs = runs.filter(run_progress__preset_id=preset_id)
        if entry.field == "tournament" and entry.operator == "=":
            if entry.value is False:
                runs = runs.exclude(run_progress__is_tournament=True)
            if entry.value is True:
                runs = runs.filter(run_progress__is_tournament=True)
        if entry.field == "date_exclude" and entry.operator == "in" and isinstance(entry.value, list):
            excluded_dates = [_parse_context_date(value) for value in entry.value]
            dates = [value for value in excluded_dates if value is not None]
            if dates:
                runs = runs.exclude(effective_battle_date__date__in=dates)
        if entry.field == "preset_name_include" and entry.operator == "in" and isinstance(entry.value, list):
            names = [str(value) for value in entry.value if value]
            if names:
                preset_query = Q()
                for name in names:
                    preset_query |= Q(run_progress__preset__name__iexact=name)
                runs = runs.filter(preset_query)
        if entry.field == "preset_name_exclude" and entry.operator == "in" and isinstance(entry.value, list):
            names = [str(value) for value in entry.value if value]
            if names:
                for name in names:
                    runs = runs.exclude(run_progress__preset__name__iexact=name)
        if entry.field == "patch_boundary" and entry.operator == "in" and isinstance(entry.value, list):
            boundaries = _resolve_patch_boundary_tokens(entry.value)
            boundary_dates = [boundary.boundary_date for boundary in boundaries]
            if boundary_dates:
                runs = _apply_patch_boundary_filters(runs, boundary_dates=boundary_dates)
    return runs


def _explore_metric_unit(
    metric: ExploreMetricDefinition | None,
    selection: ExploreMetricSelection,
) -> str:
    """Return the display unit for an Explore metric selection."""

    if selection.percent_of_total:
        return "percent"
    if metric is None:
        return ""
    return metric.unit


def _explore_aggregation_label(selection: ExploreMetricSelection) -> str:
    """Return a human-friendly aggregation label for Explore output."""

    base_labels = {"sum": "Sum", "count": "Count", "avg": "Average"}
    base_label = base_labels.get(selection.aggregation, selection.aggregation)
    if selection.percent_of_total:
        return f"Percent of total ({base_label.lower()})"
    return base_label


def _explore_execute_query(
    query: ExploreQuery,
    *,
    player: Player,
    registry: dict[str, ExploreMetricDefinition],
) -> dict[str, object]:
    """Execute an Explore query and build template payloads."""

    runs = _explore_runs_queryset(player=player)
    runs = _apply_explore_scope(runs, scope=query.scope, snapshot_id=query.scope.snapshot_id)
    runs = _apply_explore_filters(runs, filters=query.filters)
    run_list = list(runs)
    run_order = [run.id for run in run_list if getattr(run, "id", None) is not None]
    metric_selections = query.metrics
    metric_defs = [registry.get(selection.key) for selection in metric_selections]
    metric_labels = [
        metric.label if metric else selection.key for metric, selection in zip(metric_defs, metric_selections)
    ]
    metric_units = [
        _explore_metric_unit(metric, selection)
        for metric, selection in zip(metric_defs, metric_selections)
    ]
    metric_aggregations = [selection.aggregation for selection in metric_selections]
    metric_aggregation_labels = [
        _explore_aggregation_label(selection) for selection in metric_selections
    ]
    metric_entries = [
        {
            "label": label,
            "unit": unit,
            "aggregation": aggregation,
            "aggregation_label": aggregation_label,
        }
        for label, unit, aggregation, aggregation_label in zip(
            metric_labels,
            metric_units,
            metric_aggregations,
            metric_aggregation_labels,
        )
    ]
    per_metric_results = [
        execute_explore_query(
            run_list,
            query=query,
            metric_selection=selection,
            metric_registry=registry,
            breakdown_registry=DEFAULT_BREAKDOWNS,
        )
        for selection in metric_selections
    ]
    primary_result = per_metric_results[0] if per_metric_results else None
    breakdown_defs: list[ExploreBreakdownDefinition] = []
    for breakdown in query.breakdowns:
        definition = DEFAULT_BREAKDOWNS.get(breakdown.dimension)
        if definition is not None:
            breakdown_defs.append(definition)
    breakdown_headers = [definition.label for definition in breakdown_defs if definition is not None]

    breakdown_map: dict[tuple[str, ...], dict[str, object]] = {}
    for metric_idx, result in enumerate(per_metric_results):
        for row in result.rows:
            bucket = breakdown_map.setdefault(
                row.breakdown,
                {
                    "breakdown": row.breakdown,
                    "values": [None for _ in metric_selections],
                    "sample_counts": [0 for _ in metric_selections],
                    "run_id": row.run_id,
                },
            )
            values = bucket["values"]
            counts = bucket["sample_counts"]
            if isinstance(values, list):
                values[metric_idx] = row.value
            if isinstance(counts, list):
                counts[metric_idx] = row.sample_count
            if bucket.get("run_id") != row.run_id:
                bucket["run_id"] = None

    rows: list[ExploreResultRowPayload] = []
    for bucket in breakdown_map.values():
        values = bucket.get("values")
        counts = bucket.get("sample_counts")
        breakdown_value = bucket.get("breakdown")
        breakdown_labels = breakdown_value if isinstance(breakdown_value, tuple) else ()
        run_id_value = bucket.get("run_id")
        run_id = run_id_value if isinstance(run_id_value, int) else None
        count_list = counts if isinstance(counts, list) else []
        sample_count_mismatch = False
        if count_list:
            sample_count_mismatch = any(count != count_list[0] for count in count_list[1:])
        metric_cells = [
            {
                "value": values[idx] if isinstance(values, list) and idx < len(values) else None,
                "sample_count": count_list[idx] if idx < len(count_list) else 0,
                "unit": entry["unit"],
                "label": entry["label"],
                "aggregation": entry["aggregation"],
                "aggregation_label": entry["aggregation_label"],
            }
            for idx, entry in enumerate(metric_entries)
        ]
        rows.append(
            {
                "breakdown": breakdown_labels,
                "value": values[0] if isinstance(values, list) and values else None,
                "values": values if isinstance(values, list) else [],
                "sample_count": count_list[0] if count_list else 0,
                "sample_counts": count_list,
                "sample_count_mismatch": sample_count_mismatch,
                "metric_cells": metric_cells,
                "run_id": run_id,
            }
        )
    if breakdown_defs:
        rows = sorted(rows, key=lambda row: _explore_breakdown_sort_key(row["breakdown"], breakdown_defs))

    total_sample_counts = [
        sum(row.sample_count for row in result.rows) for result in per_metric_results
    ]
    total_sample_count_mismatch = False
    if total_sample_counts:
        total_sample_count_mismatch = any(
            count != total_sample_counts[0] for count in total_sample_counts[1:]
        )
    missing_counts = [result.missing_count for result in per_metric_results]
    total_values = [result.total_value for result in per_metric_results]
    total_cells = [
        {
            "value": total_values[idx] if idx < len(total_values) else None,
            "sample_count": total_sample_counts[idx] if idx < len(total_sample_counts) else 0,
            "unit": entry["unit"],
            "label": entry["label"],
            "aggregation": entry["aggregation"],
            "aggregation_label": entry["aggregation_label"],
        }
        for idx, entry in enumerate(metric_entries)
    ]

    labels = [" • ".join(row["breakdown"]) if row["breakdown"] else "Total" for row in rows]
    values = [row["value"] or 0.0 for row in rows]
    chart_unit = metric_units[0] if metric_units else ""
    chart_payload: dict[str, object] | None = None
    if len(metric_selections) == 1 and primary_result is not None:
        if metric_selections[0].percent_of_total:
            chart_unit = "percent"
        if query.visualization_hint == "donut" and not metric_selections[0].percent_of_total:
            total = sum(values)
            chart_unit = "percent"
            values = [(value / total * 100.0) if total else 0.0 for value in values]
        chart_payload = {"labels": labels, "values": values, "unit": chart_unit}

    return {
        "rows": rows,
        "breakdown_headers": breakdown_headers,
        "metric_label": metric_labels[0] if metric_labels else "",
        "metric_unit": metric_units[0] if metric_units else "",
        "metric_labels": metric_labels,
        "metric_units": metric_units,
        "metric_aggregations": metric_aggregations,
        "metric_aggregation_labels": metric_aggregation_labels,
        "metrics": metric_entries,
        "aggregation": metric_aggregations[0] if metric_aggregations else "",
        "aggregation_label": metric_aggregation_labels[0] if metric_aggregation_labels else "",
        "visualization": query.visualization_hint,
        "run_count": primary_result.run_count if primary_result else 0,
        "missing_count": sum(missing_counts),
        "missing_counts": missing_counts,
        "total_value": total_values[0] if total_values else None,
        "total_values": total_values,
        "total_sample_count": total_sample_counts[0] if total_sample_counts else 0,
        "total_sample_counts": total_sample_counts,
        "total_sample_count_mismatch": total_sample_count_mismatch,
        "total_cells": total_cells,
        "run_order": run_order,
        "chart": chart_payload,
        "explainability": _explore_explainability(
            query,
            player=player,
            run_count=primary_result.run_count if primary_result else 0,
            metric_labels=metric_labels,
            metric_aggregations=metric_aggregation_labels,
        ),
    }


def _append_explore_missing_warnings(results: dict[str, object], warnings: list[str]) -> None:
    """Append missing data warnings for Explore results."""

    missing_counts = results.get("missing_counts")
    metric_labels = results.get("metric_labels")
    if isinstance(missing_counts, list) and isinstance(metric_labels, list):
        for count, label in zip(missing_counts, metric_labels):
            if count:
                warnings.append(
                    f"Missing data: {count} run values were unavailable for metric {label}."
                )
        return
    missing_count = results.get("missing_count")
    if isinstance(missing_count, int) and missing_count:
        warnings.append(
            f"Missing data: {missing_count} run values were unavailable for the selected metric."
        )


def _explore_explainability(
    query: ExploreQuery,
    *,
    player: Player,
    run_count: int,
    metric_labels: Sequence[str],
    metric_aggregations: Sequence[str],
) -> tuple[str, ...]:
    """Return plain-language explainability lines for Explore outputs."""

    lines: list[str] = [f"Runs in scope: {run_count}"]

    if query.scope.start_date or query.scope.end_date:
        start = query.scope.start_date.isoformat() if query.scope.start_date else "Any"
        end = query.scope.end_date.isoformat() if query.scope.end_date else "Any"
        lines.append(f"Date range: {start} to {end}.")

    if query.scope.tier:
        lines.append(f"Tier scope: Tier {query.scope.tier}.")

    if query.scope.preset_id:
        preset = Preset.objects.filter(player=player, id=query.scope.preset_id).first()
        if preset is not None:
            lines.append(f"Preset scope: {preset.name}.")

    if query.scope.snapshot_id:
        snapshot = ChartSnapshot.objects.filter(player=player, id=query.scope.snapshot_id).first()
        if snapshot is not None:
            lines.append(f"Preset run scope: {snapshot.name}.")

    if query.scope.past_n_runs:
        lines.append(f"Past N runs: {query.scope.past_n_runs}.")

    filter_lines = _describe_explore_filters(query.filters, player=player)
    if filter_lines:
        lines.extend(filter_lines)

    breakdown_labels = [DEFAULT_BREAKDOWNS[entry.dimension].label for entry in query.breakdowns if entry.dimension in DEFAULT_BREAKDOWNS]
    if breakdown_labels:
        lines.append(f"Breakdowns: {', '.join(breakdown_labels)}.")
    else:
        lines.append("Breakdowns: none.")

    if metric_labels:
        labels = ", ".join(metric_labels)
        lines.append(f"Metrics: {labels}.")
    if metric_aggregations:
        aggs = ", ".join(metric_aggregations)
        lines.append(f"Aggregation: {aggs}.")
    return tuple(lines)


def _explore_breakdown_sort_key(
    breakdown: tuple[str, ...],
    definitions: list[ExploreBreakdownDefinition],
) -> tuple[tuple[object, ...], ...]:
    """Return a stable sort key for Explore breakdown labels."""

    key_parts: list[tuple[object, ...]] = []
    for idx, label in enumerate(breakdown):
        definition = definitions[idx] if idx < len(definitions) else None
        if definition is not None:
            if definition.key == "tier":
                tier_value = _parse_tier_label(label)
                key_parts.append((0, tier_value if tier_value is not None else 0, label))
                continue
            if definition.key == "real_time_hour":
                hour_value = _parse_hour_bucket_label(label, prefix="Real Time Hour")
                if hour_value is not None:
                    key_parts.append((0, hour_value, label))
                    continue
            if definition.key == "game_time_hour":
                hour_value = _parse_hour_bucket_label(label, prefix="Game Time Hour")
                if hour_value is not None:
                    key_parts.append((0, hour_value, label))
                    continue
        key_parts.append((1, label))
    return tuple(key_parts)


def _parse_tier_label(label: str) -> int | None:
    """Return a tier number parsed from a label like 'Tier 11'."""

    token = label.strip()
    if not token.lower().startswith("tier"):
        return None
    parts = token.split()
    if len(parts) < 2:
        return None
    if parts[1].isdigit():
        return int(parts[1])
    return None


def _parse_hour_bucket_label(label: str, *, prefix: str) -> int | None:
    """Return an hour number parsed from labels like 'Game Time Hour 3'."""

    token = label.strip()
    if not token.lower().startswith(prefix.lower()):
        return None
    suffix = token[len(prefix):].strip()
    if suffix.isdigit():
        return int(suffix)
    return None


def _describe_explore_filters(
    filters: Iterable[ExploreFilter],
    *,
    player: Player | None = None,
) -> list[str]:
    """Return human-readable filter descriptions."""

    lines: list[str] = []
    for entry in filters:
        if entry.field == "tier":
            if entry.operator == "in" and isinstance(entry.value, list):
                tiers = ", ".join(f"Tier {v}" for v in entry.value if v is not None)
                lines.append(f"Tier filter: {tiers}.")
            if entry.operator == ">=" and entry.value is not None:
                lines.append(f"Tier minimum: {entry.value}.")
            if entry.operator == "<=" and entry.value is not None:
                lines.append(f"Tier maximum: {entry.value}.")
        if entry.field == "wave":
            if entry.operator == "range" and isinstance(entry.value, dict):
                wave_min = entry.value.get("min")
                wave_max = entry.value.get("max")
                lines.append(f"Wave range: {wave_min} to {wave_max}.")
            if entry.operator == ">=" and entry.value is not None:
                lines.append(f"Wave minimum: {entry.value}.")
            if entry.operator == "<=" and entry.value is not None:
                lines.append(f"Wave maximum: {entry.value}.")
        if entry.field == "death_cause":
            if entry.value is None:
                lines.append("Death cause: Not recorded.")
            else:
                lines.append(f"Death cause: {entry.value}.")
        if entry.field == "preset" and entry.value is not None:
            preset_label = str(entry.value)
            if player is not None:
                preset_id = _parse_context_int(entry.value)
                if preset_id is not None:
                    preset = Preset.objects.filter(player=player, id=preset_id).first()
                    if preset is not None:
                        preset_label = preset.name
            lines.append(f"Preset filter: {preset_label}.")
        if entry.field == "patch_boundary" and entry.operator == "in" and isinstance(entry.value, list):
            resolved = _resolve_patch_boundary_tokens(entry.value)
            if resolved:
                labels = ", ".join(_format_patch_boundary_label(boundary) for boundary in resolved)
                lines.append(f"Patch boundary filter: {labels}.")
            else:
                raw_labels = ", ".join(str(value) for value in entry.value if value)
                if raw_labels:
                    lines.append(f"Patch boundary filter: {raw_labels}.")
        if entry.field == "date_range" and isinstance(entry.value, dict):
            start = entry.value.get("start") or "Any"
            end = entry.value.get("end") or "Any"
            lines.append(f"Date filter: {start} to {end}.")
    return lines


def _context_filtered_runs(filter_form: ChartContextForm, *, player: Player) -> QuerySet[BattleReport]:
    """Return a queryset filtered only by tier/preset context.

    This is used for comparisons where the selected windows should remain
    independent of any chart date filters.
    """

    runs = _with_effective_battle_date(
        BattleReport.objects.filter(player=player).select_related(
            "run_progress",
            "run_progress__preset",
        )
    ).order_by("effective_battle_date", "id")
    valid = filter_form.is_valid()
    snapshot = filter_form.cleaned_data.get("context_snapshot") if valid else None
    snapshot_context = _snapshot_context_from_filter(snapshot)
    tournament_filter = filter_form.cleaned_data.get("tournament_filter") if valid else None
    force_tournaments = bool(tournament_filter) or bool(
        snapshot_context and (snapshot_context.tournament_filter or snapshot_context.include_tournaments)
    )
    include_tournaments = bool(valid and (filter_form.cleaned_data.get("include_tournaments") or False))
    include_dissonance = bool(valid and (filter_form.cleaned_data.get("include_dissonance") or False))
    runs = _exclude_special_runs(
        runs,
        include_tournaments=bool(include_tournaments or force_tournaments),
        include_dissonance=include_dissonance,
    )
    include_hidden = bool(valid and (filter_form.cleaned_data.get("include_hidden") or False))
    force_hidden = bool(snapshot_context and snapshot_context.include_hidden)
    if not include_hidden and not force_hidden:
        runs = runs.filter(is_hidden=False)
    if not valid:
        return runs

    tier = filter_form.cleaned_data.get("tier")
    preset = filter_form.cleaned_data.get("preset")
    exclude_presets = tuple(filter_form.cleaned_data.get("exclude_presets") or ())
    patch_boundaries = tuple(filter_form.cleaned_data.get("patch_boundaries") or ())
    if tier:
        runs = runs.filter(run_progress__tier=tier)
    if preset:
        runs = runs.filter(run_progress__preset=preset)
    if exclude_presets:
        runs = runs.exclude(run_progress__preset__in=exclude_presets)
    runs = _apply_tournament_filter(runs, tournament_filter=tournament_filter)
    runs = _apply_snapshot_context_filters(runs, snapshot_context=snapshot_context)
    if patch_boundaries:
        boundary_dates = [boundary.boundary_date for boundary in patch_boundaries]
        runs = _apply_patch_boundary_filters(runs, boundary_dates=boundary_dates)
    return runs


def _comparison_scope_options(
    runs: Iterable[BattleReport],
) -> tuple[
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
    dict[str, list[int]],
]:
    """Build tier, tournament, preset, and patch options for comparison dropdowns.

    Args:
        runs: Iterable of BattleReport records already scoped to the active context.

    Returns:
        Tuple of (tier_options, preset_options, tournament_options, patch_options, run_id_map)
        where the options are simple dicts with `value`/`label` keys and the map
        stores run ids keyed by option value.
    """

    tiers: dict[int, list[int]] = {}
    tournaments: list[int] = []
    tournament_ranks: dict[str, list[int]] = {}
    presets: dict[int, list[int]] = {}
    preset_labels: dict[int, str] = {}
    patches: dict[date, list[int]] = {}
    patch_boundaries = list(PatchBoundary.objects.order_by("boundary_date"))
    patch_window_map = _patch_boundary_window_map() if patch_boundaries else {}

    for run in runs:
        progress = getattr(run, "run_progress", None)
        if progress is None:
            continue
        tier = getattr(progress, "tier", None)
        if tier is not None:
            tiers.setdefault(int(tier), []).append(run.id)
        if bool(getattr(progress, "is_tournament", False)):
            tournaments.append(run.id)
            rank = getattr(progress, "tournament_rank", None)
            if rank:
                tournament_ranks.setdefault(str(rank), []).append(run.id)
        preset_id = getattr(progress, "preset_id", None)
        if preset_id:
            presets.setdefault(int(preset_id), []).append(run.id)
            preset = getattr(progress, "preset", None)
            name = getattr(preset, "name", None)
            if name:
                preset_labels[int(preset_id)] = name
        effective_date = getattr(run, "effective_battle_date", None)
        run_date = getattr(effective_date, "date", lambda: None)()
        if run_date and patch_window_map:
            for boundary_date, next_date in patch_window_map.items():
                if run_date >= boundary_date and (next_date is None or run_date < next_date):
                    patches.setdefault(boundary_date, []).append(run.id)
                    break

    tier_options = [
        {"value": tier_filter_value(tier), "label": f"Tier {tier}"}
        for tier in sorted(tiers)
    ]
    tournament_options: list[dict[str, str]] = []
    if tournaments:
        tournament_options.append(
            {"value": tournament_filter_value(None), "label": "Tournament (all)"}
        )
        for key, label in TOURNAMENT_RANK_CHOICES:
            if key in tournament_ranks:
                tournament_options.append(
                    {
                        "value": tournament_filter_value(key),
                        "label": f"Tournament: {label}",
                    }
                )
    preset_options = [
        {"value": f"preset:{preset_id}", "label": preset_labels.get(preset_id, f"Preset {preset_id}")}
        for preset_id in sorted(presets, key=lambda pid: preset_labels.get(pid, str(pid)).casefold())
    ]
    patch_options = [
        {
            "value": f"patch:{boundary.boundary_date.isoformat()}",
            "label": _format_patch_boundary_label(boundary),
        }
        for boundary in patch_boundaries
        if boundary.boundary_date in patches
    ]

    run_id_map: dict[str, list[int]] = {}
    for tier, run_ids in tiers.items():
        run_id_map[tier_filter_value(tier)] = run_ids
    for preset_id, run_ids in presets.items():
        run_id_map[f"preset:{preset_id}"] = run_ids
    if tournaments:
        run_id_map[tournament_filter_value(None)] = tournaments
        for rank, run_ids in tournament_ranks.items():
            run_id_map[tournament_filter_value(rank)] = run_ids
    for boundary_date, run_ids in patches.items():
        run_id_map[f"patch:{boundary_date.isoformat()}"] = run_ids

    return tier_options, preset_options, tournament_options, patch_options, run_id_map


def _with_effective_battle_date(runs: QuerySet[BattleReport]) -> QuerySet[BattleReport]:
    """Annotate a queryset with an effective battle date for time-series filtering.

    Args:
        runs: BattleReport queryset.

    Returns:
        QuerySet annotated with `effective_battle_date`, using `battle_date` when
        present and otherwise falling back to the report import time.
    """

    return runs.annotate(
        effective_battle_date=Coalesce(
            "run_progress__battle_date",
            "parsed_at",
            output_field=DateTimeField(),
        )
    )


def _comparison_scope_size_warning(
    *, scope_a_count: int | None, scope_b_count: int | None, scope_average: bool | None
) -> str | None:
    """Return a warning message when comparison scopes differ substantially.

    Args:
        scope_a_count: Number of runs in scope A.
        scope_b_count: Number of runs in scope B.

    Returns:
        Warning text when scope sizes differ enough to skew comparisons,
        otherwise None.
    """

    if scope_a_count is None or scope_b_count is None:
        return None
    if scope_a_count <= 0 or scope_b_count <= 0:
        return None
    larger = max(scope_a_count, scope_b_count)
    smaller = min(scope_a_count, scope_b_count)
    if smaller == 0:
        return None
    if larger >= smaller * 2 and (larger - smaller) >= 3:
        if scope_average:
            return "Scope sizes differ widely; averages help but uneven samples can still skew comparisons."
        return "Scope sizes differ widely; consider enabling Average each scope for fairer comparisons."
    return None


def _build_comparison_result(
    form: ComparisonForm,
    *,
    base_analysis: tuple[RunAnalysis, ...],
    context_runs: QuerySet[BattleReport],
) -> dict[str, object] | None:
    """Build a comparison result payload for template rendering."""

    if not form.is_valid():
        return None

    focus = str(form.cleaned_data.get("summary_focus") or "economy")
    goal_aware_supported = focus == "economy"

    raw_text_metric_specs: dict[str, tuple[str, UnitType]] = {
        "damage_dealt": ("Damage dealt", UnitType.damage),
        "projectiles_damage": ("Projectiles Damage", UnitType.damage),
        "orb_damage": ("Orb Damage", UnitType.damage),
        "land_mine_damage": ("Land Mine Damage", UnitType.damage),
        "chain_lightning_damage": ("Chain Lightning Damage", UnitType.damage),
        "death_wave_damage": ("Death Wave Damage", UnitType.damage),
        "smart_missile_damage": ("Smart Missile Damage", UnitType.damage),
        "enemies_destroyed_basic": ("Basic", UnitType.count),
        "enemies_destroyed_fast": ("Fast", UnitType.count),
        "enemies_destroyed_tank": ("Tank", UnitType.count),
        "enemies_destroyed_ranged": ("Ranged", UnitType.count),
        "enemies_destroyed_boss": ("Boss", UnitType.count),
        "enemies_destroyed_protector": ("Protector", UnitType.count),
        "enemies_destroyed_by_orbs": ("Destroyed By Orbs", UnitType.count),
        "enemies_destroyed_by_thorns": ("Destroyed by Thorns", UnitType.count),
    }

    def _aggregate_metric_value(
        records: tuple[BattleReport, ...],
        *,
        metric_key: str,
        mode: str,
    ) -> tuple[int, float | None]:
        """Compute the aggregated metric value and its contributing sample size.

        Args:
            records: BattleReport records included in the scope.
            metric_key: Metric key registered in the analysis engine.
            mode: Either "average" or "total".

        Returns:
            A `(n, value)` tuple where `n` counts non-missing values and
            `value` is None when there are no usable points.
        """

        raw_spec = raw_text_metric_specs.get(metric_key)
        if raw_spec is not None:
            label, unit_type = raw_spec
            values: list[float] = []
            for record in records:
                raw_text = getattr(record, "raw_text", None)
                if not isinstance(raw_text, str):
                    continue
                extracted = extract_numeric_value(raw_text, label=label, unit_type=unit_type)
                if extracted is None:
                    continue
                values.append(float(extracted.value))
            if not values:
                return 0, None
            total = float(sum(values))
            return (len(values), total / len(values)) if mode == "average" else (len(values), total)

        series = analyze_metric_series(records, metric_key=metric_key)
        values = [point.value for point in series.points if point.value is not None]
        if not values:
            return 0, None
        total = float(sum(values))
        return (len(values), total / len(values)) if mode == "average" else (len(values), total)

    def _metric_summaries_for_focus(
        *,
        records_a: tuple[BattleReport, ...],
        records_b: tuple[BattleReport, ...],
        metric_keys: tuple[str, ...],
        mode: str,
        allow_single_run: bool,
    ) -> tuple[list[dict[str, object]], tuple[str, ...]]:
        """Build metric summary rows for the selected focus.

        Args:
            records_a: Scope A BattleReport records.
            records_b: Scope B BattleReport records.
            metric_keys: Ordered metric keys to summarize.
            allow_single_run: Whether to allow single-run scopes without minimum sample checks.

        Returns:
            A `(rows, limitations)` tuple. Rows include only metrics with at
            least `MIN_RUNS_FOR_ADVICE` contributing samples in both scopes
            unless averaging or single-run scopes are allowed.
        """

        rows: list[dict[str, object]] = []
        limitations: list[str] = []
        min_samples = 1 if mode == "average" or allow_single_run else MIN_RUNS_FOR_ADVICE

        for metric_key in metric_keys:
            n_a, value_a = _aggregate_metric_value(records_a, metric_key=metric_key, mode=mode)
            n_b, value_b = _aggregate_metric_value(records_b, metric_key=metric_key, mode=mode)
            if n_a < min_samples or n_b < min_samples:
                label = get_metric_definition(metric_key).label
                limitations.append(
                    f"Metric omitted due to insufficient samples: {label} (A n={n_a}, B n={n_b})."
                )
                continue
            if value_a is None or value_b is None:
                label = get_metric_definition(metric_key).label
                limitations.append(
                    f"Metric omitted due to missing values: {label} (A n={n_a}, B n={n_b})."
                )
                continue

            spec = get_metric_definition(metric_key)
            computed = delta(value_a, value_b)
            rows.append(
                {
                    "metric_key": metric_key,
                    "label": spec.label,
                    "unit": spec.unit,
                    "baseline_value": value_a,
                    "comparison_value": value_b,
                    "delta": computed,
                    "percent_display": computed.percent * 100 if computed.percent is not None else None,
                    "baseline_n": n_a,
                    "comparison_n": n_b,
                }
            )

        return rows, tuple(limitations)

    def _goal_scope_sample_from_records(label: str, records: tuple[BattleReport, ...]) -> GoalScopeSample:
        """Build a GoalScopeSample from per-run metric values.

        Args:
            label: Human-friendly scope label.
            records: BattleReport records included in the scope.

        Returns:
            GoalScopeSample used by goal-aware advice scoring.
        """

        runs_coins_per_hour, coins_per_hour = _aggregate_metric_value(
            records, metric_key="coins_per_hour", mode="average"
        )
        runs_coins_per_wave, coins_per_wave = _aggregate_metric_value(
            records, metric_key="coins_per_wave", mode="average"
        )
        runs_waves_reached, waves_reached = _aggregate_metric_value(
            records, metric_key="waves_reached", mode="average"
        )

        return GoalScopeSample(
            label=label,
            runs_coins_per_hour=runs_coins_per_hour,
            runs_coins_per_wave=runs_coins_per_wave,
            runs_waves_reached=runs_waves_reached,
            coins_per_hour=coins_per_hour,
            coins_per_wave=coins_per_wave,
            waves_reached=waves_reached,
        )

    focus_metric_keys_by_id: dict[str, tuple[str, ...]] = {
        "economy": (
            "coins_per_hour",
            "coins_per_wave",
            "coins_earned",
            "cash_earned",
            "cells_earned",
            "reroll_shards_earned",
            "waves_reached",
        ),
        "damage": (
            "damage_dealt",
            "projectiles_damage",
            "orb_damage",
            "land_mine_damage",
            "chain_lightning_damage",
            "death_wave_damage",
            "smart_missile_damage",
        ),
        "enemy_destruction": (
            "enemies_destroyed_total",
            "enemies_destroyed_boss",
            "enemies_destroyed_basic",
            "enemies_destroyed_fast",
            "enemies_destroyed_tank",
            "enemies_destroyed_ranged",
            "enemies_destroyed_protector",
            "enemies_destroyed_by_orbs",
            "enemies_destroyed_by_thorns",
        ),
        "efficiency": (
            "coins_per_hour",
            "waves_per_hour",
            "enemies_destroyed_per_hour",
        ),
    }
    focus_metric_keys = focus_metric_keys_by_id.get(focus) or focus_metric_keys_by_id["economy"]

    scope_a_runs = tuple(form.cleaned_data.get("scope_a_runs") or ())
    scope_b_runs = tuple(form.cleaned_data.get("scope_b_runs") or ())
    scope_average = bool(form.cleaned_data.get("scope_average") or False)
    mode = "average" if scope_average else "total"
    if scope_a_runs and scope_b_runs:
        headline_n_a, headline_a = _aggregate_metric_value(scope_a_runs, metric_key="coins_per_hour", mode=mode)
        headline_n_b, headline_b = _aggregate_metric_value(scope_b_runs, metric_key="coins_per_hour", mode=mode)
        computed = None if headline_a is None or headline_b is None else delta(headline_a, headline_b)

        rows, limitations = _metric_summaries_for_focus(
            records_a=scope_a_runs,
            records_b=scope_b_runs,
            metric_keys=focus_metric_keys,
            mode=mode,
            allow_single_run=len(scope_a_runs) == 1 and len(scope_b_runs) == 1,
        )

        goal_baseline = _goal_scope_sample_from_records("Scope A", scope_a_runs) if goal_aware_supported else None
        goal_comparison = _goal_scope_sample_from_records("Scope B", scope_b_runs) if goal_aware_supported else None

        return {
            "kind": "run_sets",
            "summary_focus": focus,
            "goal_aware_supported": goal_aware_supported,
            "focus_metrics_sufficient": bool(rows),
            "scope_a_run_count": len(scope_a_runs),
            "scope_b_run_count": len(scope_b_runs),
            "scope_summary_mode": mode,
            "metric": "coins/hour",
            "label_a": "Scope A",
            "label_b": "Scope B",
            "baseline_value": headline_a,
            "comparison_value": headline_b,
            "delta": computed,
            "percent_display": None if computed is None else computed.percent * 100 if computed.percent is not None else None,
            "metric_summaries": rows,
            "metric_limitations": limitations,
            "goal_baseline": goal_baseline,
            "goal_comparison": goal_comparison,
            "headline_n_a": headline_n_a,
            "headline_n_b": headline_n_b,
        }

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

        records_a = tuple(
            _with_effective_battle_date(context_runs).filter(
                effective_battle_date__date__gte=a_start,
                effective_battle_date__date__lte=a_end,
            )
        )
        records_b = tuple(
            _with_effective_battle_date(context_runs).filter(
                effective_battle_date__date__gte=b_start,
                effective_battle_date__date__lte=b_end,
            )
        )
        headline_n_a, baseline_value = _aggregate_metric_value(records_a, metric_key="coins_per_hour", mode=mode)
        headline_n_b, comparison_value = _aggregate_metric_value(records_b, metric_key="coins_per_hour", mode=mode)
        computed = (
            None
            if baseline_value is None or comparison_value is None
            else delta(baseline_value, comparison_value)
        )

        rows, limitations = _metric_summaries_for_focus(
            records_a=records_a,
            records_b=records_b,
            metric_keys=focus_metric_keys,
            mode=mode,
            allow_single_run=len(records_a) == 1 and len(records_b) == 1,
        )
        goal_baseline = _goal_scope_sample_from_records("Window A", records_a) if goal_aware_supported else None
        goal_comparison = _goal_scope_sample_from_records("Window B", records_b) if goal_aware_supported else None

        return {
            "kind": "windows",
            "summary_focus": focus,
            "goal_aware_supported": goal_aware_supported,
            "focus_metrics_sufficient": bool(rows),
            "metric": "coins/hour",
            "window_a": window_a,
            "window_b": window_b,
            "scope_summary_mode": mode,
            "baseline_value": baseline_value,
            "comparison_value": comparison_value,
            "delta": computed,
            "percent_display": None if computed is None else computed.percent * 100 if computed.percent is not None else None,
            "metric_summaries": rows,
            "metric_limitations": limitations,
            "goal_baseline": goal_baseline,
            "goal_comparison": goal_comparison,
            "headline_n_a": headline_n_a,
            "headline_n_b": headline_n_b,
        }

    return None


def _form_has_filters(form: ChartContextForm) -> bool:
    """Return True when the chart context form applies any filter/overlay options."""

    if not form.is_valid():
        return False
    if form.cleaned_data.get("start_date") or form.cleaned_data.get("end_date"):
        return True
    if (
        form.cleaned_data.get("tier")
        or form.cleaned_data.get("tournament_filter")
        or form.cleaned_data.get("preset")
        or form.cleaned_data.get("exclude_presets")
        or form.cleaned_data.get("context_snapshot")
        or form.cleaned_data.get("past_runs")
        or form.cleaned_data.get("patch_boundaries")
    ):
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
            "granularity": None,
            "tier": None,
            "preset": None,
            "excluded_presets": None,
            "patch_boundaries": None,
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
    granularity = form.cleaned_data.get("granularity")
    tier = form.data.get("tier") if hasattr(form, "data") else None
    preset = form.cleaned_data.get("preset")
    excluded_presets = tuple(form.cleaned_data.get("exclude_presets") or ())
    excluded_labels = [preset.name for preset in excluded_presets if getattr(preset, "name", None)]
    excluded_display = ", ".join(excluded_labels)
    patch_boundaries = tuple(form.cleaned_data.get("patch_boundaries") or ())
    patch_labels = [_format_patch_boundary_label(boundary) for boundary in patch_boundaries]
    patch_display = ", ".join(patch_labels)
    snapshot = form.cleaned_data.get("context_snapshot")
    moving_average_window = form.cleaned_data.get("moving_average_window")
    ev_trials = form.cleaned_data.get("ev_trials")
    ev_seed = form.cleaned_data.get("ev_seed")

    return {
        "charts": selected_display or None,
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None,
        "granularity": str(granularity) if granularity else None,
        "tier": str(tier) if tier else None,
        "preset": preset.name if preset else None,
        "excluded_presets": excluded_display or None,
        "patch_boundaries": patch_display or None,
        "snapshot": snapshot.name if snapshot else None,
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


def _chart_scope_summary_payload(
    *,
    chart_context: dict[str, str | None],
    total_filtered_runs: int,
    chartable_points: int,
    has_filters: bool,
    chart_empty_state: str | None,
) -> dict[str, object]:
    """Return a scope + completeness payload for the Charts dashboard.

    Args:
        chart_context: Output of `_chart_context_summary` used to display active filters.
        total_filtered_runs: Count of BattleReport rows in the current scope.
        chartable_points: Count of non-null datapoints across rendered datasets.
        has_filters: Whether the context form includes any non-default filters.
        chart_empty_state: Empty-state message shown when there are no usable datapoints.

    Returns:
        Dict intended for template rendering.
    """

    return {
        "runs_in_scope": total_filtered_runs,
        "has_filters": has_filters,
        "chartable_points": chartable_points,
        "empty_state": chart_empty_state,
        "context": chart_context,
    }


def _why_am_i_seeing_this_payload(
    *,
    chart_context: dict[str, str | None],
    total_filtered_runs: int,
    chartable_points: int,
    has_filters: bool,
    chart_empty_state: str | None,
) -> dict[str, tuple[str, ...] | str]:
    """Return plain-language scope and aggregation notes for the Charts dashboard.

    Args:
        chart_context: Output of `_chart_context_summary` used to describe the active selection.
        total_filtered_runs: Count of BattleReport rows in the current scope.
        chartable_points: Count of non-null datapoints across rendered datasets.
        has_filters: Whether the context form includes any non-default filters.
        chart_empty_state: Empty-state message shown when there are no usable datapoints.

    Returns:
        Dict with stable, template-ready strings.
    """

    included: list[str] = []
    excluded: list[str] = []
    aggregation: list[str] = []
    limitations: list[str] = []

    if chart_context.get("start_date") or chart_context.get("end_date"):
        included.append(
            "Date range: "
            f"{chart_context.get('start_date') or '…'} to {chart_context.get('end_date') or '…'}"
        )
        excluded.append("Runs outside the selected date range.")
    if chart_context.get("tier"):
        included.append(f"Tier: {chart_context['tier']}")
        excluded.append("Runs from other tiers.")
    if chart_context.get("preset"):
        included.append(f"Preset: {chart_context['preset']}")
        excluded.append("Runs with other presets (or no preset).")
    if chart_context.get("excluded_presets"):
        excluded.append(f"Excluded presets: {chart_context['excluded_presets']}.")
    if chart_context.get("patch_boundaries"):
        included.append(f"Patch boundary: {chart_context['patch_boundaries']}.")
        excluded.append("Runs outside the selected patch windows.")

    if not included:
        included.append("All imported runs in the default date window.")
        if has_filters:
            included.append("Additional filters may be active in Advanced options.")

    if (granularity := chart_context.get("granularity")):
        aggregation.append(f"X-axis buckets follow the selected granularity ({granularity}).")
    aggregation.append(
        "When multiple runs fall into the same bucket, charts combine values within that bucket."
    )

    if chart_empty_state:
        limitations.append(chart_empty_state)
    if total_filtered_runs > 0 and chartable_points == 0:
        limitations.append("Some charts require fields that may be missing from your imported Battle Reports.")

    return {
        "included": tuple(included),
        "excluded": tuple(excluded),
        "aggregation": tuple(aggregation),
        "limitations": tuple(limitations),
        "title": "Why am I seeing this?",
    }
