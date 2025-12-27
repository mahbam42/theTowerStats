"""Unit tests covering persisted derived metrics consumption."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from analysis.metrics import MetricComputeConfig, compute_metric_value

pytestmark = [pytest.mark.unit, pytest.mark.regression]


@dataclass(frozen=True, slots=True)
class _DerivedMetrics:
    values: dict[str, float]


@dataclass(frozen=True, slots=True)
class _Record:
    derived_metrics: _DerivedMetrics
    raw_text: str = ""


def test_persisted_derived_metric_used_when_present() -> None:
    """Persisted derived values are returned without re-parsing raw text."""

    record = _Record(derived_metrics=_DerivedMetrics(values={"coins_from_golden_tower": 123.0}))

    value, _used, assumptions = compute_metric_value(
        "coins_from_golden_tower",
        record=record,
        coins=None,
        cash=None,
        interest_earned=None,
        cells=None,
        reroll_shards=None,
        wave=None,
        real_time_seconds=None,
        context=None,
        entity_type=None,
        entity_name=None,
        config=MetricComputeConfig(),
    )

    assert value == 123.0
    assert assumptions == ()


def test_missing_persisted_metric_returns_none() -> None:
    """Metrics without persisted values return None even when raw text is present."""

    record = _Record(
        derived_metrics=_DerivedMetrics(values={}),
        raw_text="Battle Report\nCoins From Golden Tower\t9.9M\n",
    )

    value, _used, assumptions = compute_metric_value(
        "coins_from_golden_tower",
        record=record,
        coins=None,
        cash=None,
        interest_earned=None,
        cells=None,
        reroll_shards=None,
        wave=None,
        real_time_seconds=None,
        context=None,
        entity_type=None,
        entity_name=None,
        config=MetricComputeConfig(),
    )

    assert value is None
    assert assumptions == ("Persisted derived metric missing; reparse or reingest the Battle Report.",)
