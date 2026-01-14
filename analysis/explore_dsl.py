"""Parse and format the Explore DSL."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re

from .explore_registry import ExploreBreakdownDefinition, ExploreMetricDefinition
from .explore_schema import (
    ExploreBreakdown,
    ExploreFilter,
    ExploreMetricSelection,
    ExploreQuery,
    ExploreScope,
    FilterOperator,
    VisualizationHint,
)


@dataclass(frozen=True, slots=True)
class ExploreDslParseResult:
    """Parsed result for the Explore DSL."""

    query: ExploreQuery | None
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


_PLACEHOLDER_RE = re.compile(r"^\[[^:\]]+:[^\]]*\]$")
_NAME_RE = re.compile(r'^name\s+"(?P<name>.+)"\s*$', re.IGNORECASE)
_SCOPE_RE = re.compile(r"^scope\s+(?P<field>[a-z_]+)\s+(?P<value>.+)$", re.IGNORECASE)
_FILTER_RE = re.compile(r"^filter\s+(?P<field>[a-z_]+)\s+(?P<value>.+)$", re.IGNORECASE)
_BREAKDOWN_RE = re.compile(r"^breakdown(?:\s+by)?\s+(?P<value>.+)$", re.IGNORECASE)
_METRIC_RE = re.compile(r"^metric\s+(?P<key>[a-z0-9_]+)\s+(?P<agg>[a-z]+)$", re.IGNORECASE)
_OUTPUT_RE = re.compile(r"^output\s+(?P<value>[a-z]+)$", re.IGNORECASE)
_DATE_RANGE_RE = re.compile(r"^(?P<start>.+)\.\.(?P<end>.+)$")
_ID_WITH_LABEL_RE = re.compile(r'^(?P<id>\d+)(?:\s+"[^"]+")?$')
_QUOTED_RE = re.compile(r'^"(.*)"$')


def format_explore_dsl(
    query: ExploreQuery | None,
    *,
    default_scope: ExploreScope,
) -> str:
    """Format an ExploreQuery into DSL text."""

    scope = query.scope if query else default_scope

    def _date_or_placeholder(value: date | None) -> str:
        return value.isoformat() if value else "[date:YYYY-MM-DD]"

    def _value_or_placeholder(value: object | None, placeholder: str) -> str:
        return str(value) if value is not None else placeholder

    name = query.name if query else "New Explore Query"
    lines: list[str] = [f'name "{name}"']

    start = scope.start_date if scope.start_date else default_scope.start_date
    end = scope.end_date if scope.end_date else default_scope.end_date
    lines.append(f"scope date {_date_or_placeholder(start)}..{_date_or_placeholder(end)}")

    tier = scope.tier if scope.tier is not None else default_scope.tier
    lines.append(f"scope tier {_value_or_placeholder(tier, '[tier:—]')}")

    preset = scope.preset_id if scope.preset_id is not None else default_scope.preset_id
    lines.append(f"scope preset {_value_or_placeholder(preset, '[preset:—]')}")

    snapshot = scope.snapshot_id if scope.snapshot_id is not None else default_scope.snapshot_id
    lines.append(f"scope snapshot {_value_or_placeholder(snapshot, '[snapshot:—]')}")

    past_n = scope.past_n_runs if scope.past_n_runs is not None else default_scope.past_n_runs
    lines.append(f"scope past_n_runs {_value_or_placeholder(past_n, '[runs:—]')}")

    if query:
        for entry in query.filters:
            lines.extend(_format_filter(entry))

        if query.breakdowns:
            breakdown_line = ", ".join(breakdown.dimension for breakdown in query.breakdowns)
            lines.append(f"breakdown by {breakdown_line}")

        lines.append(f"metric {query.metric.key} {query.metric.aggregation}")
        lines.append(f"output {query.visualization_hint}")

    return "\n".join(lines)


def parse_explore_dsl(
    text: str,
    *,
    player_id: str,
    default_scope: ExploreScope,
) -> ExploreDslParseResult:
    """Parse Explore DSL text into a query."""

    errors: list[str] = []
    warnings: list[str] = []
    name: str | None = None
    scope = default_scope
    filters: list[ExploreFilter] = []
    breakdowns: list[ExploreBreakdown] = []
    metric: ExploreMetricSelection | None = None
    visualization: VisualizationHint = "table"

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if match := _NAME_RE.match(line):
            name = match.group("name").strip()
            continue

        if match := _SCOPE_RE.match(line):
            scope, scope_errors = _parse_scope_line(
                match.group("field").strip(),
                match.group("value").strip(),
                scope,
                default_scope,
            )
            errors.extend(scope_errors)
            continue

        if match := _FILTER_RE.match(line):
            filter_entries, filter_errors = _parse_filter_line(
                match.group("field").strip(),
                match.group("value").strip(),
            )
            filters.extend(filter_entries)
            errors.extend(filter_errors)
            continue

        if match := _BREAKDOWN_RE.match(line):
            breakdowns, breakdown_errors = _parse_breakdown_line(match.group("value").strip())
            errors.extend(breakdown_errors)
            continue

        if match := _METRIC_RE.match(line):
            metric_key = match.group("key").strip()
            aggregation = match.group("agg").strip().lower()
            if aggregation not in ("sum", "count"):
                errors.append(f"Aggregation {aggregation} is not supported.")
            metric = ExploreMetricSelection(key=metric_key, aggregation=aggregation)  # type: ignore[arg-type]
            continue

        if match := _OUTPUT_RE.match(line):
            output = match.group("value").strip().lower()
            if output not in ("table", "bar", "donut", "kpi"):
                errors.append(f"Output {output} is not supported.")
            else:
                visualization = output  # type: ignore[assignment]
            continue

        errors.append(f"Unrecognized DSL line: {line}")

    if not name:
        errors.append("Query name is required.")
    if metric is None:
        errors.append("Metric selection is required.")

    if errors:
        return ExploreDslParseResult(query=None, errors=tuple(errors), warnings=tuple(warnings))

    assert metric is not None
    query = ExploreQuery(
        schema_version="1.0",
        player_id=player_id,
        name=name or "Explore Query",
        scope=scope,
        filters=tuple(filters),
        breakdowns=tuple(breakdowns),
        metric=metric,
        visualization_hint=visualization,
    )
    return ExploreDslParseResult(query=query, errors=tuple(errors), warnings=tuple(warnings))


def build_explore_autocomplete(
    metric_registry: dict[str, ExploreMetricDefinition],
    breakdown_registry: dict[str, ExploreBreakdownDefinition],
) -> dict[str, list[dict[str, str]]]:
    """Return autocomplete payloads for the Explore DSL editor."""

    keywords = [
        "name",
        "scope",
        "filter",
        "breakdown",
        "metric",
        "output",
        "by",
        "sum",
        "count",
        "table",
        "bar",
        "donut",
        "kpi",
        "date",
        "tier",
        "preset",
        "snapshot",
        "past_n_runs",
        "death_cause",
        "wave",
        "run",
        "in",
    ]
    metrics = [
        {"label": key, "detail": metric.label, "type": "metric"}
        for key, metric in sorted(metric_registry.items())
    ]
    breakdowns = [
        {"label": key, "detail": breakdown.label, "type": "breakdown"}
        for key, breakdown in sorted(breakdown_registry.items())
    ]
    keyword_entries = [{"label": entry, "type": "keyword"} for entry in keywords]
    return {"keywords": keyword_entries, "metrics": metrics, "breakdowns": breakdowns}


def _format_filter(entry: ExploreFilter) -> list[str]:
    """Return DSL lines for a filter entry."""

    if entry.field == "tier" and entry.operator == "in" and isinstance(entry.value, list):
        values = ", ".join(str(value) for value in entry.value)
        return [f"filter tier in {values}"]
    if entry.field == "tier" and entry.operator in (">=", "<="):
        return [f"filter tier {entry.operator} {entry.value}"]
    if entry.field == "wave" and entry.operator == "range" and isinstance(entry.value, dict):
        wave_min = entry.value.get("min")
        wave_max = entry.value.get("max")
        return [f"filter wave {wave_min}..{wave_max}"]
    if entry.field == "wave" and entry.operator in (">=", "<="):
        return [f"filter wave {entry.operator} {entry.value}"]
    if entry.field == "death_cause":
        if entry.value is None:
            return ["filter death_cause = [death:—]"]
        return [f'filter death_cause = "{entry.value}"']
    if entry.field == "preset" and entry.operator == "=":
        return [f"filter preset = {entry.value}"]
    if entry.field == "date_range" and entry.operator == "range" and isinstance(entry.value, dict):
        start = entry.value.get("start") or "[date:YYYY-MM-DD]"
        end = entry.value.get("end") or "[date:YYYY-MM-DD]"
        return [f"filter date_range {start}..{end}"]
    return []


def _parse_scope_line(
    field: str,
    value: str,
    scope: ExploreScope,
    default_scope: ExploreScope,
) -> tuple[ExploreScope, list[str]]:
    """Parse a scope line into an ExploreScope."""

    errors: list[str] = []
    if field == "date":
        start, end, date_errors = _parse_date_range(value)
        errors.extend(date_errors)
        scope = ExploreScope(
            start_date=start if start is not None else default_scope.start_date,
            end_date=end if end is not None else default_scope.end_date,
            tier=scope.tier,
            preset_id=scope.preset_id,
            snapshot_id=scope.snapshot_id,
            past_n_runs=scope.past_n_runs,
        )
    elif field == "tier":
        tier_value = _parse_int(value)
        scope = ExploreScope(
            start_date=scope.start_date,
            end_date=scope.end_date,
            tier=tier_value if tier_value is not None else default_scope.tier,
            preset_id=scope.preset_id,
            snapshot_id=scope.snapshot_id,
            past_n_runs=scope.past_n_runs,
        )
    elif field == "preset":
        preset_value = _parse_id_with_optional_label(value)
        scope = ExploreScope(
            start_date=scope.start_date,
            end_date=scope.end_date,
            tier=scope.tier,
            preset_id=preset_value if preset_value is not None else default_scope.preset_id,
            snapshot_id=scope.snapshot_id,
            past_n_runs=scope.past_n_runs,
        )
    elif field == "snapshot":
        snapshot_value = _parse_id_with_optional_label(value)
        scope = ExploreScope(
            start_date=scope.start_date,
            end_date=scope.end_date,
            tier=scope.tier,
            preset_id=scope.preset_id,
            snapshot_id=snapshot_value if snapshot_value is not None else default_scope.snapshot_id,
            past_n_runs=scope.past_n_runs,
        )
    elif field == "past_n_runs":
        runs_value = _parse_int(value)
        scope = ExploreScope(
            start_date=scope.start_date,
            end_date=scope.end_date,
            tier=scope.tier,
            preset_id=scope.preset_id,
            snapshot_id=scope.snapshot_id,
            past_n_runs=runs_value if runs_value is not None else default_scope.past_n_runs,
        )
    else:
        errors.append(f"Unknown scope field: {field}.")
    return scope, errors


def _parse_filter_line(field: str, value: str) -> tuple[list[ExploreFilter], list[str]]:
    """Parse a filter line into ExploreFilter entries."""

    errors: list[str] = []
    filters: list[ExploreFilter] = []
    operator: FilterOperator | None = None
    parsed_value: object | None = None

    if ".." in value and field in {"tier", "wave", "date_range"}:
        range_match = _DATE_RANGE_RE.match(value)
        if not range_match:
            errors.append(f"Invalid range filter: {value}.")
            return filters, errors
        start_raw = range_match.group("start").strip()
        end_raw = range_match.group("end").strip()
        if field == "date_range":
            operator = "range"
            parsed_value = {
                "start": _parse_date_token(start_raw),
                "end": _parse_date_token(end_raw),
            }
        else:
            min_value = _parse_int(start_raw)
            max_value = _parse_int(end_raw)
            operator = "range"
            parsed_value = {"min": min_value, "max": max_value}
    elif value.lower().startswith("in "):
        operator = "in"
        raw_list = value[3:].split(",")
        parsed_value = [_parse_int(entry.strip()) for entry in raw_list if entry.strip()]
    else:
        parts = value.split(maxsplit=1)
        if len(parts) == 2 and parts[0] in {">=", "<=", "!=", "="}:
            operator = parts[0]  # type: ignore[assignment]
            parsed_value = _parse_value(parts[1].strip())
        elif field in {"tier", "wave"}:
            errors.append(f"Invalid filter syntax for {field}: {value}.")
        else:
            operator = "="
            parsed_value = _parse_value(value)

    if field == "death_cause" and _is_placeholder(value):
        parsed_value = None
    if operator:
        filters.append(ExploreFilter(field=field, operator=operator, value=parsed_value))
    else:
        errors.append(f"Missing operator for filter: {field}.")
    return filters, errors


def _parse_breakdown_line(value: str) -> tuple[list[ExploreBreakdown], list[str]]:
    """Parse a breakdown line into ExploreBreakdown entries."""

    errors: list[str] = []
    breakdowns: list[ExploreBreakdown] = []
    normalized = value.replace(" then ", ",")
    raw_breakdowns = [entry.strip() for entry in normalized.split(",") if entry.strip()]
    if not raw_breakdowns:
        errors.append("Breakdown line is empty.")
        return breakdowns, errors
    for idx, entry in enumerate(raw_breakdowns, start=1):
        breakdowns.append(ExploreBreakdown(dimension=entry, order=idx))
    return breakdowns, errors


def _parse_date_range(value: str) -> tuple[date | None, date | None, list[str]]:
    """Parse a date range string into dates."""

    errors: list[str] = []
    match = _DATE_RANGE_RE.match(value)
    if not match:
        errors.append("Date scope must use start..end format.")
        return None, None, errors

    start = _parse_date_token(match.group("start").strip())
    end = _parse_date_token(match.group("end").strip())
    return start, end, errors


def _parse_date_token(value: str) -> date | None:
    """Parse a date token or return None for placeholders."""

    if _is_placeholder(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _parse_int(value: str) -> int | None:
    """Parse an integer token, honoring placeholders."""

    if _is_placeholder(value):
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _parse_id_with_optional_label(value: str) -> int | None:
    """Parse an integer id with an optional quoted label."""

    if _is_placeholder(value):
        return None
    match = _ID_WITH_LABEL_RE.match(value)
    if not match:
        return None
    return int(match.group("id"))


def _parse_value(value: str) -> object | None:
    """Parse a generic filter value."""

    if _is_placeholder(value):
        return None
    if match := _QUOTED_RE.match(value):
        return match.group(1)
    if value.isdigit():
        return int(value)
    return value


def _is_placeholder(value: str) -> bool:
    """Return True when a value represents a placeholder token."""

    return bool(_PLACEHOLDER_RE.match(value.strip()))
