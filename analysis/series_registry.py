"""MetricSeries registry used by declarative chart configs.

This registry is a thin, analysis-layer description of which metric keys exist,
which filter dimensions they support, and which transforms are allowed. It is
used by the ChartConfig validator and the dashboard renderer.

The registry remains Django-free and describes *capabilities* only. Query
scoping (date range, tier, preset, entity selection) happens at the view layer
before records are passed into the Analysis Engine.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Final, Iterable, Literal

MetricTransform = Literal["none", "moving_average", "cumulative", "rate_per_hour"]

FilterKey = Literal["date_range", "tier", "preset", "uw", "guardian", "bot"]
Aggregation = Literal["sum", "avg"]


@dataclass(frozen=True, slots=True)
class MetricSeriesSpec:
    """Describe a chartable metric series.

    Args:
        key: Stable metric key referenced by ChartConfig.metric_series.metric_key.
        label: Human-friendly label.
        unit: Display unit string.
        kind: Either "observed" or "derived".
        aggregation: Default aggregation used by dashboard charts.
        allowed_transforms: Allowed transforms for this metric.
        supported_filters: Filter dimensions supported by this metric.
    """

    key: str
    label: str
    unit: str
    kind: str
    aggregation: Aggregation
    allowed_transforms: frozenset[MetricTransform]
    supported_filters: frozenset[FilterKey]


class MetricSeriesRegistry:
    """Lookup and validation helpers for metric series definitions."""

    def __init__(self, specs: Iterable[MetricSeriesSpec]) -> None:
        """Initialize a registry from a collection of specs."""

        self._specs: dict[str, MetricSeriesSpec] = {}
        for spec in specs:
            if spec.key in self._specs:
                raise ValueError(f"Duplicate MetricSeriesSpec key: {spec.key!r}")
            self._specs[spec.key] = spec

    def get(self, key: str) -> MetricSeriesSpec | None:
        """Return a spec for a metric key, or None when missing."""

        return self._specs.get(key)

    def list(self) -> tuple[MetricSeriesSpec, ...]:
        """Return all specs in a stable order."""

        return tuple(self._specs[key] for key in sorted(self._specs.keys()))

    def formula_metric_keys(self, formula: str) -> set[str]:
        """Return metric keys referenced by a derived formula.

        Args:
            formula: An expression containing metric keys as variable names.

        Returns:
            A set of variable names that correspond to registered metric keys.
        """

        try:
            tree = ast.parse(formula, mode="eval")
        except SyntaxError:
            return set()

        names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                names.add(node.id)
        return {name for name in names if name in self._specs}


_COMMON_FILTERS: Final[frozenset[FilterKey]] = frozenset({"date_range", "tier", "preset"})


DEFAULT_REGISTRY: Final[MetricSeriesRegistry] = MetricSeriesRegistry(
    specs=(
        MetricSeriesSpec(
            key="coins_earned",
            label="Coins earned",
            unit="coins",
            kind="observed",
            aggregation="sum",
            allowed_transforms=frozenset({"none", "rate_per_hour", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="cash_earned",
            label="Cash earned",
            unit="cash",
            kind="observed",
            aggregation="sum",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="cells_earned",
            label="Cells earned",
            unit="cells",
            kind="observed",
            aggregation="sum",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="reroll_shards_earned",
            label="Reroll shards earned",
            unit="shards",
            kind="observed",
            aggregation="sum",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="waves_reached",
            label="Waves reached",
            unit="waves",
            kind="observed",
            aggregation="avg",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="uw_runs_count",
            label="Runs using selected ultimate weapon",
            unit="runs",
            kind="observed",
            aggregation="sum",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=frozenset({"date_range", "tier", "preset", "uw"}),
        ),
        MetricSeriesSpec(
            key="guardian_runs_count",
            label="Runs using selected guardian chip",
            unit="runs",
            kind="observed",
            aggregation="sum",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=frozenset({"date_range", "tier", "preset", "guardian"}),
        ),
        MetricSeriesSpec(
            key="bot_runs_count",
            label="Runs using selected bot",
            unit="runs",
            kind="observed",
            aggregation="sum",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=frozenset({"date_range", "tier", "preset", "bot"}),
        ),
    )
)
