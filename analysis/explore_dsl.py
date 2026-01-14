"""Parse and format the Explore DSL."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re
from typing import cast

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
    use_all_tokens = query is not None

    def _date_or_placeholder(value: date | None) -> str:
        return value.isoformat() if value else "[date:YYYY-MM-DD]"

    def _value_or_placeholder(
        value: object | None,
        *,
        placeholder: str,
        default_value: object | None,
    ) -> str:
        if use_all_tokens and value is None and default_value is not None:
            return "all"
        return str(value) if value is not None else placeholder

    def _date_range_value() -> str:
        if (
            use_all_tokens
            and scope.start_date is None
            and scope.end_date is None
            and (default_scope.start_date or default_scope.end_date)
        ):
            return "all"
        start = scope.start_date if scope.start_date is not None else default_scope.start_date
        end = scope.end_date if scope.end_date is not None else default_scope.end_date
        return f"{_date_or_placeholder(start)}..{_date_or_placeholder(end)}"

    name = query.name if query else "New Explore Query"
    lines: list[str] = [f'name "{name}"']

    date_excludes: list[str] = []
    preset_excludes: list[str] = []
    preset_includes: list[str] = []

    tier_filter = None
    tournament_excluded = False
    remaining_filters: list[ExploreFilter] = []
    if query:
        for entry in query.filters:
            if entry.field == "tournament" and entry.operator == "=" and entry.value is False:
                tournament_excluded = True
                continue
            if entry.field == "tier" and entry.operator in (">=", "<="):
                tier_filter = entry
                continue
            if entry.field == "tier" and entry.operator == "range" and isinstance(entry.value, dict):
                tier_filter = entry
                continue
            if entry.field == "date_exclude" and entry.operator == "in" and isinstance(entry.value, list):
                date_excludes = [str(value) for value in entry.value if value]
                continue
            if entry.field == "preset_name_include" and entry.operator == "in" and isinstance(entry.value, list):
                preset_includes = [str(value) for value in entry.value if value]
                continue
            if entry.field == "preset_name_exclude" and entry.operator == "in" and isinstance(entry.value, list):
                preset_excludes = [str(value) for value in entry.value if value]
                continue
            remaining_filters.append(entry)

    date_line = f"scope date {_date_range_value()}"
    if date_excludes:
        date_line = f"{date_line} not {', '.join(_format_name(value) for value in date_excludes)}"
    lines.append(date_line)

    tier_line = f"scope tier {_value_or_placeholder(scope.tier, placeholder='[tier:—]', default_value=default_scope.tier)}"
    if tier_filter is not None:
        if tier_filter.operator == "range" and isinstance(tier_filter.value, dict):
            tier_min = tier_filter.value.get("min")
            tier_max = tier_filter.value.get("max")
            tier_line = f"scope tier {tier_min}..{tier_max}"
        elif tier_filter.operator in (">=", "<="):
            tier_line = f"scope tier {tier_filter.operator}{tier_filter.value}"
    if tournament_excluded:
        tier_line = f"{tier_line} not tournament"
    lines.append(tier_line)

    if preset_includes:
        preset_line = f"scope preset {', '.join(_format_name(value) for value in preset_includes)}"
    else:
        preset_line = f"scope preset {_value_or_placeholder(scope.preset_id, placeholder='[preset:—]', default_value=default_scope.preset_id)}"
    if preset_excludes:
        preset_line = f"{preset_line} not {', '.join(_format_name(value) for value in preset_excludes)}"
    lines.append(preset_line)

    lines.append(
        "scope snapshot "
        + _value_or_placeholder(
            scope.snapshot_id,
            placeholder="[snapshot:—]",
            default_value=default_scope.snapshot_id,
        )
    )

    lines.append(
        "scope past_n_runs "
        + _value_or_placeholder(
            scope.past_n_runs,
            placeholder="[runs:—]",
            default_value=default_scope.past_n_runs,
        )
    )

    if query:
        for entry in remaining_filters:
            lines.extend(_format_filter(entry))

        if query.breakdowns:
            breakdown_line = ", ".join(breakdown.dimension for breakdown in query.breakdowns)
            lines.append(f"breakdown by {breakdown_line}")

        lines.append(f"metric {query.metric.key} {query.metric.aggregation}")
        if query.visualization_hint != "table":
            lines.append(f"output {query.visualization_hint}")
        else:
            lines.append("# output bar | donut | kpi")

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
            scope, scope_filters, scope_errors = _parse_scope_line(
                match.group("field").strip(),
                match.group("value").strip(),
                scope,
                default_scope,
            )
            errors.extend(scope_errors)
            filters.extend(scope_filters)
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

        if line.lower().startswith("metric "):
            raw_metric = line[len("metric ") :].strip()
            if not raw_metric:
                errors.append("Metric selection is required.")
                continue
            tokens = raw_metric.split()
            if "and" in tokens:
                errors.append("Explore v1 supports one metric per query.")
                continue
            if len(tokens) == 1:
                metric_key = tokens[0]
                aggregation = "sum"
            elif len(tokens) == 2:
                metric_key, aggregation = tokens
                aggregation = aggregation.lower()
            else:
                errors.append("Metric line must be: metric <key> [sum|count].")
                continue
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


def _format_name(value: str) -> str:
    """Return a DSL-safe name token."""

    token = value.strip()
    if not token:
        return token
    if " " in token or "," in token:
        return f"\"{token}\""
    return token


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
        "and",
        "not",
        "all",
        "*",
        "tournament",
        "tournaments",
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
) -> tuple[ExploreScope, list[ExploreFilter], list[str]]:
    """Parse a scope line into an ExploreScope."""

    errors: list[str] = []
    filters: list[ExploreFilter] = []
    normalized = value.replace("&", " and ")
    tournament_excluded = False
    tournament_match = re.search(r"\bnot\s+(tournament|tournaments|tournament_rank)\b", normalized, re.I)
    if tournament_match:
        tournament_excluded = True
        normalized = re.sub(
            r"\bnot\s+(tournament|tournaments|tournament_rank)\b",
            "",
            normalized,
            flags=re.I,
        ).strip()
    normalized = re.sub(r"\band\b", "", normalized, flags=re.I).strip()
    main_value, not_clause = _split_not_clause(normalized) if field in {"date", "preset"} else (normalized, None)
    if field == "date":
        all_token = _is_all_token(main_value)
        if all_token:
            start = None
            end = None
        else:
            start, end, date_errors = _parse_date_range(main_value)
            errors.extend(date_errors)
        if not_clause:
            dates, date_errors = _parse_date_list(not_clause)
            errors.extend(date_errors)
            if dates:
                filters.append(ExploreFilter(field="date_exclude", operator="in", value=dates))
        scope = ExploreScope(
            start_date=None if all_token else (start if start is not None else default_scope.start_date),
            end_date=None if all_token else (end if end is not None else default_scope.end_date),
            tier=scope.tier,
            preset_id=scope.preset_id,
            snapshot_id=scope.snapshot_id,
            past_n_runs=scope.past_n_runs,
        )
    elif field == "tier":
        if _is_all_token(normalized):
            scope = ExploreScope(
                start_date=scope.start_date,
                end_date=scope.end_date,
                tier=None,
                preset_id=scope.preset_id,
                snapshot_id=scope.snapshot_id,
                past_n_runs=scope.past_n_runs,
            )
        else:
            operator_match = re.match(r"^(>=|<=|>|<|=)?\s*(.+)?$", normalized)
            operator = (operator_match.group(1) or "").strip() if operator_match else ""
            raw_value = (operator_match.group(2) or "").strip() if operator_match else normalized
            tier_value = _parse_int(raw_value)
            if operator in (">", "<") and tier_value is not None:
                if operator == ">":
                    tier_value += 1
                    operator = ">="
                else:
                    tier_value -= 1
                    operator = "<="
            if operator in (">=", "<=") and tier_value is not None:
                filters.append(
                    ExploreFilter(
                        field="tier",
                        operator=cast(FilterOperator, operator),
                        value=tier_value,
                    )
                )
            else:
                scope = ExploreScope(
                    start_date=scope.start_date,
                    end_date=scope.end_date,
                    tier=tier_value if tier_value is not None else default_scope.tier,
                    preset_id=scope.preset_id,
                    snapshot_id=scope.snapshot_id,
                    past_n_runs=scope.past_n_runs,
                )
    elif field == "preset":
        all_token = _is_all_token(main_value)
        preset_value = None if all_token else _parse_id_with_optional_label(main_value)
        if not_clause:
            names, name_errors = _parse_name_list(not_clause)
            errors.extend(name_errors)
            if names:
                filters.append(ExploreFilter(field="preset_name_exclude", operator="in", value=names))
        if (
            preset_value is None
            and main_value
            and not _is_placeholder(main_value)
            and not _is_all_token(main_value)
        ):
            include_names, include_errors = _parse_name_list(main_value)
            errors.extend(include_errors)
            if include_names:
                filters.append(
                    ExploreFilter(
                        field="preset_name_include",
                        operator="in",
                        value=include_names,
                    )
                )
        scope = ExploreScope(
            start_date=scope.start_date,
            end_date=scope.end_date,
            tier=scope.tier,
            preset_id=None if all_token else (preset_value if preset_value is not None else default_scope.preset_id),
            snapshot_id=scope.snapshot_id,
            past_n_runs=scope.past_n_runs,
        )
    elif field == "snapshot":
        all_token = _is_all_token(normalized)
        snapshot_value = None if all_token else _parse_id_with_optional_label(normalized)
        scope = ExploreScope(
            start_date=scope.start_date,
            end_date=scope.end_date,
            tier=scope.tier,
            preset_id=scope.preset_id,
            snapshot_id=None if all_token else (snapshot_value if snapshot_value is not None else default_scope.snapshot_id),
            past_n_runs=scope.past_n_runs,
        )
    elif field == "past_n_runs":
        all_token = _is_all_token(normalized)
        runs_value = None if all_token else _parse_int(normalized)
        scope = ExploreScope(
            start_date=scope.start_date,
            end_date=scope.end_date,
            tier=scope.tier,
            preset_id=scope.preset_id,
            snapshot_id=scope.snapshot_id,
            past_n_runs=None if all_token else (runs_value if runs_value is not None else default_scope.past_n_runs),
        )
    else:
        errors.append(f"Unknown scope field: {field}.")
    if tournament_excluded:
        filters.append(ExploreFilter(field="tournament", operator="=", value=False))
    return scope, filters, errors


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
    normalized = re.sub(r"\s+and\s+", ",", normalized, flags=re.IGNORECASE)
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


def _split_not_clause(value: str) -> tuple[str, str | None]:
    """Split a value into a main value and a not-clause."""

    match = re.search(r"\bnot\b(.+)$", value, re.I)
    if not match:
        return value.strip(), None
    main = value[: match.start()].strip()
    clause = match.group(1).strip()
    return main, clause


def _parse_date_list(value: str) -> tuple[list[str], list[str]]:
    """Parse a comma/and-separated list of ISO dates."""

    errors: list[str] = []
    items: list[str] = []
    for token in re.split(r"\s*(?:,|and)\s*", value):
        cleaned = token.replace("not ", "").strip()
        if not cleaned:
            continue
        parsed = _parse_date_token(cleaned)
        if parsed is None:
            errors.append(f"Invalid date exclusion: {cleaned}.")
            continue
        items.append(parsed.isoformat())
    return items, errors


def _parse_name_list(value: str) -> tuple[list[str], list[str]]:
    """Parse a comma/and-separated list of names."""

    errors: list[str] = []
    items: list[str] = []
    for token in re.split(r"\s*(?:,|and)\s*", value):
        cleaned = token.replace("not ", "").strip()
        if not cleaned:
            continue
        parsed = _parse_value(cleaned)
        if parsed is None:
            errors.append(f"Invalid preset exclusion: {cleaned}.")
            continue
        items.append(str(parsed))
    return items, errors


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


def _is_all_token(value: str) -> bool:
    """Return True when a value represents the all wildcard."""

    normalized = value.strip().casefold()
    return normalized in {"all", "*"}
