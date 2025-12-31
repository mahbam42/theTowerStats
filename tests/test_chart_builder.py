"""Unit tests for chart builder helpers."""

from __future__ import annotations

from datetime import date

import pytest

from analysis.categories import MetricCategory
from core.charting.builder import (
    ChartBuilderSelection,
    _domain_for_category,
    _infer_domain,
    build_before_after_scopes,
    build_run_vs_run_scopes,
    build_runtime_chart_config,
)

pytestmark = pytest.mark.unit


def test_build_runtime_chart_config_defaults() -> None:
    """Build a baseline runtime chart config with no comparisons."""

    selection = ChartBuilderSelection(
        metric_keys=("coins_earned",),
        chart_type="line",
        group_by="time",
        comparison="none",
        smoothing="none",
    )
    config = build_runtime_chart_config(selection)

    assert config.id == "chart_builder_custom"
    assert config.domain == "economy"
    assert config.category == "economy"
    assert config.metric_series[0].transform == "none"
    assert config.comparison is None


def test_build_runtime_chart_config_rolling_avg_and_donut() -> None:
    """Rolling average selections should map to moving-average transforms."""

    selection = ChartBuilderSelection(
        metric_keys=("coins_earned", "cash_earned"),
        chart_type="donut",
        group_by="time",
        comparison="none",
        smoothing="rolling_avg",
    )
    config = build_runtime_chart_config(selection)

    assert config.semantic_type == "distribution"
    assert all(series.transform == "moving_average" for series in config.metric_series)


def test_build_runtime_chart_config_group_by_tier() -> None:
    """Grouping by tier should map to a comparison chart."""

    selection = ChartBuilderSelection(
        metric_keys=("coins_earned",),
        chart_type="line",
        group_by="tier",
        comparison="none",
        smoothing="none",
    )
    config = build_runtime_chart_config(selection)

    assert config.category == "comparison"
    assert config.comparison is not None
    assert config.comparison.mode == "by_tier"


def test_domain_helpers_handle_mixed_categories() -> None:
    """Domain helpers should fall back to economy for mixed categories."""

    assert _infer_domain(("coins_earned", "damage_dealt")) == "economy"
    assert _domain_for_category(MetricCategory.utility) == "efficiency"


def test_build_before_after_scopes() -> None:
    """Before/after scope builders should map dates and labels."""

    scope_a, scope_b = build_before_after_scopes(
        window_a_start=date(2025, 1, 1),
        window_a_end=date(2025, 1, 7),
        window_b_start=date(2025, 1, 8),
        window_b_end=date(2025, 1, 14),
        label_a="Before",
        label_b="After",
    )

    assert scope_a.label == "Before"
    assert scope_a.start_date == date(2025, 1, 1)
    assert scope_b.label == "After"
    assert scope_b.end_date == date(2025, 1, 14)


def test_build_run_vs_run_scopes() -> None:
    """Run-vs-run scope builders should map run IDs and labels."""

    scope_a, scope_b = build_run_vs_run_scopes(run_a_id=10, run_b_id=11, label_a="Run A", label_b="Run B")

    assert scope_a.run_id == 10
    assert scope_b.run_id == 11
