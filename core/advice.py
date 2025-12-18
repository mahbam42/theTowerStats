"""Deterministic, non-prescriptive advice helpers.

Advice in this project is descriptive: it summarizes observed deltas and
provides context and limitations. It does not recommend actions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


_FORBIDDEN_TOKENS = ("should", "best", "optimal")


@dataclass(frozen=True, slots=True)
class AdviceItem:
    """A single advice item suitable for UI rendering.

    Args:
        title: Short summary sentence.
        basis: Data basis description (what inputs were used).
        context: Context description (filters or window definitions).
        limitations: Limitations or caveats for interpretation.
    """

    title: str
    basis: str
    context: str
    limitations: str


def generate_optimization_advice(comparison_result: dict[str, Any] | None) -> tuple[AdviceItem, ...]:
    """Generate descriptive advice items from an existing comparison result.

    Args:
        comparison_result: Result payload returned by `_build_comparison_result`.

    Returns:
        A tuple of AdviceItem values.
    """

    if not comparison_result:
        return ()

    baseline = float(comparison_result.get("baseline_value") or 0.0)
    comparison = float(comparison_result.get("comparison_value") or 0.0)
    delta = comparison - baseline
    percent = comparison_result.get("percent_display")

    title = f"Observed change in coins/hour: {delta:+.2f}"
    if percent is not None:
        title = f"{title} ({float(percent):+.2f}%)"

    kind = comparison_result.get("kind")
    if kind == "runs":
        basis = "Basis: 1 run in each scope."
        context = f"Context: Run A {comparison_result.get('label_a')} vs Run B {comparison_result.get('label_b')}."
        limitations = "Limitations: A single run can be noisy and may not represent a stable trend."
    else:
        window_a = comparison_result.get("window_a")
        window_b = comparison_result.get("window_b")
        a_count = getattr(window_a, "run_count", None)
        b_count = getattr(window_b, "run_count", None)
        basis = f"Basis: Window A runs={a_count}, Window B runs={b_count}."
        context = (
            f"Context: Window A {getattr(window_a, 'start_date', None)} → {getattr(window_a, 'end_date', None)}; "
            f"Window B {getattr(window_b, 'start_date', None)} → {getattr(window_b, 'end_date', None)}."
        )
        thin = []
        if isinstance(a_count, int) and a_count < 3:
            thin.append("Window A has fewer than 3 runs.")
        if isinstance(b_count, int) and b_count < 3:
            thin.append("Window B has fewer than 3 runs.")
        limitations = "Limitations: " + (" ".join(thin) if thin else "Window averages can still vary by day and tier.")

    item = AdviceItem(title=title, basis=basis, context=context, limitations=limitations)
    _assert_non_prescriptive(item)
    return (item,)


def _assert_non_prescriptive(item: AdviceItem) -> None:
    """Raise when advice contains forbidden imperative language."""

    combined = " ".join((item.title, item.basis, item.context, item.limitations)).casefold()
    for token in _FORBIDDEN_TOKENS:
        if token in combined:
            raise ValueError(f"Advice contains forbidden token: {token!r}")

