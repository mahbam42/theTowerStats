"""Phase 7 advice-generation tests."""

from __future__ import annotations

from datetime import date

import pytest

from analysis.dto import WindowSummary
from core.advice import SnapshotDeltaInput, generate_optimization_advice, generate_snapshot_delta_advice


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
    assert "Insufficient data" in items[0].title
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


def test_advice_summarizes_window_comparison_with_sufficient_data() -> None:
    """Window advice summarizes deltas only when each scope has enough runs."""

    window_a = WindowSummary(start_date=date(2025, 12, 1), end_date=date(2025, 12, 3), run_count=3, average_coins_per_hour=100.0)
    window_b = WindowSummary(start_date=date(2025, 12, 4), end_date=date(2025, 12, 6), run_count=3, average_coins_per_hour=110.0)
    comparison_result = {
        "kind": "windows",
        "metric": "coins/hour",
        "window_a": window_a,
        "window_b": window_b,
        "baseline_value": 100.0,
        "comparison_value": 110.0,
        "percent_display": 10.0,
    }
    items = generate_optimization_advice(comparison_result)
    assert items
    assert "Observed change" in items[0].title


def test_snapshot_delta_advice_degrades_to_insufficient_data() -> None:
    """Snapshot advice degrades deterministically for thin inputs."""

    items = generate_snapshot_delta_advice(
        SnapshotDeltaInput(
            metric_key="coins_per_hour",
            baseline_label="Snapshot A",
            baseline_runs=2,
            baseline_value=100.0,
            comparison_label="Current filters",
            comparison_runs=5,
            comparison_value=110.0,
        )
    )
    assert items
    assert "Insufficient data" in items[0].title
