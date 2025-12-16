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
        if mode == "none":
            warnings.append(f"ChartConfig[{config.id}].comparison.mode is 'none' but comparison is present.")
        if mode in ("by_tier", "by_preset") and config.comparison.entities:
            warnings.append(f"ChartConfig[{config.id}].comparison.entities is ignored for mode={mode}.")
        if mode == "by_entity" and not config.comparison.entities:
            errors.append(f"ChartConfig[{config.id}] comparison mode 'by_entity' requires entities.")

    if config.derived is not None:
        referenced = registry.formula_metric_keys(config.derived.formula)
        if not referenced:
            errors.append(f"ChartConfig[{config.id}].derived.formula must reference at least one metric key.")
        available = {series.metric_key for series in config.metric_series}
        missing = referenced - available
        if missing:
            errors.append(
                f"ChartConfig[{config.id}].derived.formula references metrics not present in metric_series: "
                f"{sorted(missing)}."
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

