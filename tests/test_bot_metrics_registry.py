"""Unit tests for bot metric registry entries."""

from __future__ import annotations

import pytest

from analysis.explore_registry import build_explore_metric_registry
from analysis.series_registry import DEFAULT_REGISTRY, allowed_chart_builder_aggregations

pytestmark = pytest.mark.unit


def test_bot_metrics_allow_average_aggregation() -> None:
    """Bot metrics support avg alongside sum in registries."""

    chart_registry = DEFAULT_REGISTRY
    explore_registry = build_explore_metric_registry()

    for key in ("flame_bot_damage", "thunder_bot_stuns", "golden_bot_coins_earned"):
        spec = chart_registry.get(key)
        assert spec is not None
        allowed = allowed_chart_builder_aggregations(spec)
        assert "avg" in allowed

        explore_metric = explore_registry.get(key)
        assert explore_metric is not None
        assert "avg" in explore_metric.allowed_aggregations
