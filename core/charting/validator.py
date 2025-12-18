"""Validation for ChartConfig definitions.

Chart configs are treated as user-editable output (eventually emitted by a
Chart Builder), so validation is strict and fails fast.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from analysis.series_registry import MetricSeriesRegistry

from .schema import ChartConfig


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Result of validating a chart config."""

    is_valid: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


def validate_chart_config(config: ChartConfig, *, registry: MetricSeriesRegistry) -> ValidationResult:
    """Validate a single ChartConfig against the MetricSeries registry.

    Args:
        config: ChartConfig to validate.
        registry: MetricSeriesRegistry used for metric lookups/capabilities.

    Returns:
        ValidationResult containing errors and warnings.
    """

    errors: list[str] = []
    warnings: list[str] = []

    if not config.id.strip():
        errors.append("ChartConfig.id must be a non-empty string.")
    if not config.title.strip():
        errors.append(f"ChartConfig[{config.id}].title must be a non-empty string.")

    if config.filters.date_range.enabled and not isinstance(config.filters.date_range.default_start, datetime):
        errors.append(f"ChartConfig[{config.id}].filters.date_range.default_start must be a datetime.")

    if not config.metric_series:
        errors.append(f"ChartConfig[{config.id}].metric_series must contain at least one entry.")

    allowed_categories = {
        "top_level",
        "sub_chart",
        "uw_performance",
        "guardian_stats",
        "bot_stats",
        "comparison",
        "derived",
    }
    if config.category not in allowed_categories:
        errors.append(f"ChartConfig[{config.id}].category is not a supported value: {config.category!r}.")

    allowed_chart_types = {"line", "bar", "area", "scatter", "donut"}
    if config.chart_type not in allowed_chart_types:
        errors.append(f"ChartConfig[{config.id}].chart_type is not a supported value: {config.chart_type!r}.")

    if config.chart_type == "donut":
        if config.derived is not None:
            errors.append(f"ChartConfig[{config.id}] donut charts cannot declare derived formulas.")
        if config.comparison is not None and config.comparison.mode != "none":
            errors.append(f"ChartConfig[{config.id}] donut charts cannot use comparison modes.")

    for idx, series in enumerate(config.metric_series):
        spec = registry.get(series.metric_key)
        if spec is None:
            errors.append(
                f"ChartConfig[{config.id}].metric_series[{idx}] references unknown metric_key={series.metric_key!r}."
            )
            continue

        if series.transform not in spec.allowed_transforms:
            errors.append(
                f"ChartConfig[{config.id}].metric_series[{idx}] transform={series.transform!r} "
                f"is not allowed for metric_key={series.metric_key!r}."
            )

        enabled_filters = _enabled_filter_keys(config)
        unsupported = enabled_filters - spec.supported_filters
        if unsupported:
            errors.append(
                f"ChartConfig[{config.id}].metric_series[{idx}] metric_key={series.metric_key!r} "
                f"does not support filters: {sorted(unsupported)}."
            )

        if series.transform == "moving_average" and not config.filters.date_range.enabled:
            warnings.append(
                f"ChartConfig[{config.id}] uses moving_average without date_range filtering enabled."
            )

    if config.comparison is not None:
        mode = config.comparison.mode
        if config.category != "comparison" and mode != "none":
            errors.append(
                f"ChartConfig[{config.id}] comparison.mode={mode!r} is only allowed for category='comparison'."
            )
        if mode == "none":
            warnings.append(f"ChartConfig[{config.id}].comparison.mode is 'none' but comparison is present.")
        if mode in ("by_tier", "by_preset") and config.comparison.entities:
            warnings.append(f"ChartConfig[{config.id}].comparison.entities is ignored for mode={mode}.")
        if mode == "by_entity" and not config.comparison.entities:
            errors.append(f"ChartConfig[{config.id}] comparison mode 'by_entity' requires entities.")
        if mode == "by_tier":
            _validate_comparison_dimension(config, registry=registry, dimension="tier", errors=errors)
        if mode == "by_preset":
            _validate_comparison_dimension(config, registry=registry, dimension="preset", errors=errors)
        if mode == "by_entity":
            enabled_entity_filters = [
                key for key in ("uw", "guardian", "bot") if getattr(config.filters, key).enabled
            ]
            if len(enabled_entity_filters) != 1:
                errors.append(
                    f"ChartConfig[{config.id}] comparison mode 'by_entity' requires exactly one entity filter enabled "
                    f"(uw/guardian/bot); got {enabled_entity_filters}."
                )
            else:
                _validate_comparison_dimension(
                    config, registry=registry, dimension=enabled_entity_filters[0], errors=errors
                )

    if config.derived is not None:
        inspection = registry.inspect_formula(config.derived.formula)
        if not inspection.is_valid_syntax:
            errors.append(f"ChartConfig[{config.id}].derived.formula must be valid syntax.")
        if inspection.is_valid_syntax and not inspection.is_safe:
            errors.append(f"ChartConfig[{config.id}].derived.formula contains unsupported operations.")
        if inspection.unknown_identifiers:
            errors.append(
                f"ChartConfig[{config.id}].derived.formula references unknown identifiers: "
                f"{sorted(inspection.unknown_identifiers)}."
            )

        referenced = set(inspection.referenced_metric_keys)
        if inspection.is_valid_syntax and inspection.is_safe and not inspection.unknown_identifiers and not referenced:
            errors.append(f"ChartConfig[{config.id}].derived.formula must reference at least one metric key.")
        available = {series.metric_key for series in config.metric_series}
        missing = referenced - available
        if missing:
            errors.append(
                f"ChartConfig[{config.id}].derived.formula references metrics not present in metric_series: "
                f"{sorted(missing)}."
            )
        _validate_derived_axes(
            config,
            registry=registry,
            referenced=referenced,
            errors=errors,
        )

    return ValidationResult(is_valid=not errors, errors=tuple(errors), warnings=tuple(warnings))


def validate_chart_configs(
    configs: Iterable[ChartConfig],
    *,
    registry: MetricSeriesRegistry,
) -> ValidationResult:
    """Validate a collection of ChartConfig entries, enforcing uniqueness.

    Args:
        configs: ChartConfig entries to validate.
        registry: MetricSeriesRegistry used for metric lookups/capabilities.

    Returns:
        ValidationResult covering all input configs.
    """

    errors: list[str] = []
    warnings: list[str] = []

    seen: set[str] = set()
    for config in configs:
        if config.id in seen:
            errors.append(f"Duplicate ChartConfig.id: {config.id!r}.")
        else:
            seen.add(config.id)
        result = validate_chart_config(config, registry=registry)
        errors.extend(result.errors)
        warnings.extend(result.warnings)

    return ValidationResult(is_valid=not errors, errors=tuple(errors), warnings=tuple(warnings))


def _enabled_filter_keys(config: ChartConfig) -> set[str]:
    """Return enabled filter keys for compatibility validation."""

    enabled: set[str] = set()
    if config.filters.tier.enabled:
        enabled.add("tier")
    if config.filters.preset.enabled:
        enabled.add("preset")
    if config.filters.uw.enabled:
        enabled.add("uw")
    if config.filters.guardian.enabled:
        enabled.add("guardian")
    if config.filters.bot.enabled:
        enabled.add("bot")
    if config.filters.date_range.enabled:
        enabled.add("date_range")
    return enabled


def _validate_comparison_dimension(
    config: ChartConfig,
    *,
    registry: MetricSeriesRegistry,
    dimension: str,
    errors: list[str],
) -> None:
    """Ensure all metrics in a comparison chart support the comparison dimension."""

    for idx, series in enumerate(config.metric_series):
        spec = registry.get(series.metric_key)
        if spec is None:
            continue
        if dimension not in spec.supported_filters:
            errors.append(
                f"ChartConfig[{config.id}].metric_series[{idx}] metric_key={series.metric_key!r} "
                f"does not support comparison dimension: {dimension}."
            )


def _validate_derived_axes(
    config: ChartConfig,
    *,
    registry: MetricSeriesRegistry,
    referenced: set[str],
    errors: list[str],
) -> None:
    """Validate derived metric axis compatibility against referenced series specs."""

    if config.derived is None:
        return

    expected_time_index = "timestamp" if config.derived.x_axis == "time" else "wave_number"
    for key in referenced:
        spec = registry.get(key)
        if spec is None:
            continue
        if spec.time_index != expected_time_index:
            errors.append(
                f"ChartConfig[{config.id}].derived.x_axis={config.derived.x_axis!r} is incompatible with "
                f"metric_key={key!r} (time_index={spec.time_index!r})."
            )
