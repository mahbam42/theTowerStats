# Explore Registry

This page is **Developer Documentation**. It describes how Explore builds and validates its metric and breakdown registry.

## Overview

Explore relies on a registry that describes which metrics are available, how they can be aggregated, and which breakdowns can group results. The registry is derived from the Chart Builder metric registry so that charting and Explore stay aligned.

## Registry Build Flow

- `build_explore_metric_registry` copies chartable metric definitions from `analysis.series_registry.DEFAULT_REGISTRY`.
- Each entry is normalized into an `ExploreMetricDefinition` with label, unit, aggregation rules, and a derived logic description.
- Metric unit strings are mapped to `UnitType` with `_unit_type_for_unit` so aggregation rules stay consistent.

## Aggregation Rules

- `_allowed_aggregations_for_unit` uses the series registry aggregation default (`sum` or `avg`) and the unit type to determine allowed aggregations.
- Count-only metrics return `count` as the only aggregation.
- Currency, time, and count units allow `avg` in addition to `sum`.

## Breakdowns

- `DEFAULT_BREAKDOWNS` defines semantic groupings like damage source, enemy type, and coin source.
- Each breakdown is tagged as either `field` (direct value on a run) or `metric_group` (a fixed list of metric keys).
- `compatible_metric_keys` limits which metrics can be paired with a breakdown to avoid invalid groupings.

## Extension Guidelines

- Add new chartable metrics to `analysis.series_registry.DEFAULT_REGISTRY` first; Explore will pick them up automatically.
- When a metric should be excluded from Explore, filter it before `build_explore_metric_registry` returns.
- When adding a new breakdown, keep the labels user-facing and document the grouping in user guide notes if it changes UX.
