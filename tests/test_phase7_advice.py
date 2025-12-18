"""Phase 7 advice-generation tests."""

from __future__ import annotations

import pytest

from core.advice import generate_optimization_advice


def test_advice_is_non_prescriptive_for_run_comparison() -> None:
    """Advice output must avoid imperative language and remain descriptive."""

    comparison_result = {
        "kind": "runs",
        "metric": "coins/hour",
        "label_a": "2025-12-10",
        "label_b": "2025-12-11",
        "baseline_value": 100.0,
        "comparison_value": 110.0,
        "delta": object(),
        "percent_display": 10.0,
    }
    items = generate_optimization_advice(comparison_result)
    assert items
    combined = " ".join((items[0].title, items[0].basis, items[0].context, items[0].limitations)).casefold()
    assert "should" not in combined
    assert "best" not in combined
    assert "optimal" not in combined


def test_advice_raises_on_forbidden_tokens() -> None:
    """Guard against accidental prescriptive language."""

    bad = {
        "kind": "runs",
        "metric": "coins/hour",
        "label_a": "optimal",
        "label_b": "B",
        "baseline_value": 0.0,
        "comparison_value": 0.0,
        "delta": object(),
        "percent_display": None,
    }
    with pytest.raises(ValueError):
        generate_optimization_advice(bad)
