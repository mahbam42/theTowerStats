"""Validation for Phase 7 ChartConfigDTO values."""

from __future__ import annotations

from dataclasses import dataclass

from analysis.chart_config_dto import ChartConfigDTO
from analysis.series_registry import MetricSeriesRegistry


@dataclass(frozen=True, slots=True)
class ChartConfigValidationResult:
    """Validation result for ChartConfigDTO.

    Args:
        is_valid: True when no errors exist.
        errors: Fatal validation errors.
        warnings: Non-fatal warnings intended for UI display.
    """

    is_valid: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


def validate_chart_config_dto(
    config: ChartConfigDTO,
    *,
    registry: MetricSeriesRegistry,
) -> ChartConfigValidationResult:
    """Validate a ChartConfigDTO against the MetricSeries registry.

    Args:
        config: ChartConfigDTO from the Chart Builder.
        registry: MetricSeriesRegistry for unit/category/transform capability checks.

    Returns:
        ChartConfigValidationResult containing errors and warnings.
    """

    errors: list[str] = []
    warnings: list[str] = []

    if not config.metrics:
        errors.append("ChartConfigDTO.metrics must contain at least one metric key.")

    if config.chart_type == "donut":
        if config.group_by != "time":
            errors.append("Donut charts do not support grouping.")
        if config.comparison != "none":
            errors.append("Donut charts do not support comparisons.")
        if len(config.metrics) < 2:
            errors.append("Donut charts require at least two metrics.")

    if config.comparison != "none":
        if config.scopes is None or len(config.scopes) != 2:
            errors.append("Two-scope comparisons require exactly two scopes.")
        if config.group_by != "time":
            errors.append("Two-scope comparisons require group_by='time'.")

    specs = []
    for key in config.metrics:
        spec = registry.get(key)
        if spec is None:
            errors.append(f"Unknown metric key: {key!r}.")
            continue
        specs.append(spec)

    if len(specs) >= 2:
        units = {spec.unit for spec in specs}
        if len(units) > 1:
            errors.append(f"Mixed units are not allowed in one chart: {sorted(units)}.")
        categories = {str(spec.category) for spec in specs}
        if len(categories) > 1:
            errors.append(f"Cross-category metrics are not allowed in one chart: {sorted(categories)}.")

    if config.smoothing == "rolling_avg":
        for key in config.metrics:
            spec = registry.get(key)
            if spec is None:
                continue
            if "moving_average" not in spec.allowed_transforms:
                errors.append(f"Rolling average is not supported for metric key: {key!r}.")

    if config.comparison == "run_vs_run" and config.scopes is not None:
        for idx, scope in enumerate(config.scopes):
            if scope.run_id is None:
                errors.append(f"run_vs_run scope {idx} requires run_id.")

    if config.comparison == "before_after" and config.scopes is not None:
        for idx, scope in enumerate(config.scopes):
            if scope.start_date is None or scope.end_date is None:
                errors.append(f"before_after scope {idx} requires start_date and end_date.")
            if scope.start_date is not None and scope.end_date is not None and scope.start_date > scope.end_date:
                errors.append(f"before_after scope {idx} start_date must be <= end_date.")

    return ChartConfigValidationResult(is_valid=not errors, errors=tuple(errors), warnings=tuple(warnings))

