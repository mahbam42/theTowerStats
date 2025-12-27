"""Deterministic, non-prescriptive advice helpers.

Advice in this project is descriptive: it summarizes observed deltas and
provides context and limitations. It does not recommend actions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


_FORBIDDEN_TOKENS = (
    "should",
    "must",
    "best",
    "optimal",
    "recommended",
    "recommend",
    "always",
    "never",
    "clearly better",
)
MIN_RUNS_FOR_ADVICE = 3
INSUFFICIENT_DATA_MESSAGE = "Insufficient data to draw a conclusion."


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

    kind = comparison_result.get("kind")
    if kind == "runs":
        basis = "Basis: 1 run in each scope."
        context = f"Context: Run A {comparison_result.get('label_a')} vs Run B {comparison_result.get('label_b')}."
        limitations = (
            "Limitations: Advice summaries require at least 3 runs per scope. "
            "Single-run comparisons can be noisy and are not summarized as advice."
        )
        item = AdviceItem(
            title=INSUFFICIENT_DATA_MESSAGE,
            basis=basis,
            context=context,
            limitations=limitations,
        )
        _assert_non_prescriptive(item)
        return (item,)
    if kind == "run_sets":
        a_count = comparison_result.get("scope_a_run_count")
        b_count = comparison_result.get("scope_b_run_count")
        focus = comparison_result.get("summary_focus") or "economy"
        basis = f"Basis: Scope A runs={a_count}, Scope B runs={b_count}."
        context = f"Context: Summary focus={focus}."
        if (
            not isinstance(a_count, int)
            or not isinstance(b_count, int)
            or a_count < MIN_RUNS_FOR_ADVICE
            or b_count < MIN_RUNS_FOR_ADVICE
        ):
            limitations = f"Limitations: Advice summaries require at least {MIN_RUNS_FOR_ADVICE} runs per scope."
            item = AdviceItem(
                title=INSUFFICIENT_DATA_MESSAGE,
                basis=basis,
                context=context,
                limitations=limitations,
            )
            _assert_non_prescriptive(item)
            return (item,)

        if comparison_result.get("focus_metrics_sufficient") is False:
            item = AdviceItem(
                title=INSUFFICIENT_DATA_MESSAGE,
                basis=basis,
                context=context,
                limitations=(
                    "Limitations: The selected Summary focus does not have enough usable metric samples "
                    f"to summarize (need at least {MIN_RUNS_FOR_ADVICE} runs per scope for each metric)."
                ),
            )
            _assert_non_prescriptive(item)
            return (item,)

        baseline = comparison_result.get("baseline_value")
        comparison = comparison_result.get("comparison_value")
        if baseline is None or comparison is None:
            item = AdviceItem(
                title=INSUFFICIENT_DATA_MESSAGE,
                basis=basis,
                context=context,
                limitations="Limitations: Missing coins/hour values in one or both scopes.",
            )
            _assert_non_prescriptive(item)
            return (item,)

        baseline_value = float(baseline)
        comparison_value = float(comparison)
        delta_value = comparison_value - baseline_value
        percent = comparison_result.get("percent_display")

        title = f"Observed change in coins/hour: {delta_value:+.2f}"
        if percent is not None:
            title = f"{title} ({float(percent):+.2f}%)"
        item = AdviceItem(
            title=title,
            basis=basis,
            context=context,
            limitations="Limitations: Results depend on the runs available in each scope and the focus you selected.",
        )
        _assert_non_prescriptive(item)
        return (item,)

    if kind == "windows":
        window_a = comparison_result.get("window_a")
        window_b = comparison_result.get("window_b")
        a_count = getattr(window_a, "run_count", None)
        b_count = getattr(window_b, "run_count", None)
        focus = comparison_result.get("summary_focus") or "economy"
        basis = f"Basis: Window A runs={a_count}, Window B runs={b_count}."
        context = (
            f"Context: Window A {getattr(window_a, 'start_date', None)} → {getattr(window_a, 'end_date', None)}; "
            f"Window B {getattr(window_b, 'start_date', None)} → {getattr(window_b, 'end_date', None)}."
        )
        context = f"{context} Summary focus={focus}."
        if (
            not isinstance(a_count, int)
            or not isinstance(b_count, int)
            or a_count < MIN_RUNS_FOR_ADVICE
            or b_count < MIN_RUNS_FOR_ADVICE
        ):
            limitations = (
                f"Limitations: Advice summaries require at least {MIN_RUNS_FOR_ADVICE} runs per scope."
            )
            item = AdviceItem(
                title=INSUFFICIENT_DATA_MESSAGE,
                basis=basis,
                context=context,
                limitations=limitations,
            )
            _assert_non_prescriptive(item)
            return (item,)

        if comparison_result.get("focus_metrics_sufficient") is False:
            item = AdviceItem(
                title=INSUFFICIENT_DATA_MESSAGE,
                basis=basis,
                context=context,
                limitations=(
                    "Limitations: The selected Summary focus does not have enough usable metric samples "
                    f"to summarize (need at least {MIN_RUNS_FOR_ADVICE} runs per scope for each metric)."
                ),
            )
            _assert_non_prescriptive(item)
            return (item,)

        baseline = comparison_result.get("baseline_value")
        comparison = comparison_result.get("comparison_value")
        if baseline is None or comparison is None:
            item = AdviceItem(
                title=INSUFFICIENT_DATA_MESSAGE,
                basis=basis,
                context=context,
                limitations="Limitations: Missing coins/hour values in one or both scopes.",
            )
            _assert_non_prescriptive(item)
            return (item,)

        baseline_value = float(baseline)
        comparison_value = float(comparison)
        delta_value = comparison_value - baseline_value
        percent = comparison_result.get("percent_display")

        title = f"Observed change in coins/hour: {delta_value:+.2f}"
        if percent is not None:
            title = f"{title} ({float(percent):+.2f}%)"
        item = AdviceItem(
            title=title,
            basis=basis,
            context=context,
            limitations="Limitations: Window averages can still vary by day and tier.",
        )
        _assert_non_prescriptive(item)
        return (item,)

    return ()


@dataclass(frozen=True, slots=True)
class SnapshotDeltaInput:
    """Inputs for snapshot-based advice deltas.

    Args:
        metric_key: Metric key used for the delta basis (e.g. "coins_per_hour").
        baseline_label: Label shown for the baseline scope (e.g. snapshot name).
        baseline_runs: Count of runs contributing to the baseline metric.
        baseline_value: Baseline metric value (average), or None when unavailable.
        comparison_label: Label shown for the comparison scope (snapshot name or "Current filters").
        comparison_runs: Count of runs contributing to the comparison metric.
        comparison_value: Comparison metric value (average), or None when unavailable.
    """

    metric_key: str
    baseline_label: str
    baseline_runs: int
    baseline_value: float | None
    comparison_label: str
    comparison_runs: int
    comparison_value: float | None


def generate_snapshot_delta_advice(delta_input: SnapshotDeltaInput) -> tuple[AdviceItem, ...]:
    """Generate descriptive advice from a snapshot delta.

    Args:
        delta_input: SnapshotDeltaInput defining the two compared scopes.

    Returns:
        A tuple containing a single AdviceItem.
    """

    basis = (
        f"Basis: metric={delta_input.metric_key}; "
        f"{delta_input.baseline_label} runs={delta_input.baseline_runs}; "
        f"{delta_input.comparison_label} runs={delta_input.comparison_runs}."
    )
    context = f"Context: {delta_input.baseline_label} vs {delta_input.comparison_label}."

    if (
        delta_input.baseline_runs < MIN_RUNS_FOR_ADVICE
        or delta_input.comparison_runs < MIN_RUNS_FOR_ADVICE
        or delta_input.baseline_value is None
        or delta_input.comparison_value is None
    ):
        limitations = (
            f"Limitations: Advice summaries require at least {MIN_RUNS_FOR_ADVICE} runs per scope and non-empty values."
        )
        item = AdviceItem(
            title=INSUFFICIENT_DATA_MESSAGE,
            basis=basis,
            context=context,
            limitations=limitations,
        )
        _assert_non_prescriptive(item)
        return (item,)

    delta_value = delta_input.comparison_value - delta_input.baseline_value
    percent = None
    if delta_input.baseline_value != 0:
        percent = (delta_value / delta_input.baseline_value) * 100.0

    title = f"Observed change in coins/hour: {delta_value:+.2f}"
    if percent is not None:
        title = f"{title} ({percent:+.2f}%)"

    item = AdviceItem(
        title=title,
        basis=basis,
        context=context,
        limitations="Limitations: Results depend on your selected filters and the runs available in each scope.",
    )
    _assert_non_prescriptive(item)
    return (item,)


@dataclass(frozen=True, slots=True)
class GoalWeights:
    """User-controlled weights for goal-aware advice scoring.

    These weights apply to percent-change deltas between two scopes. The score
    is a transparent weighted sum of those percent changes.

    Attributes:
        coins_per_hour: Weight applied to the coins/hour percent change.
        coins_per_wave: Weight applied to the coins/wave percent change.
        waves_reached: Weight applied to the waves reached percent change.
    """

    coins_per_hour: float
    coins_per_wave: float
    waves_reached: float


@dataclass(frozen=True, slots=True)
class GoalScopeSample:
    """A summarized metric sample for a single comparison scope.

    Attributes:
        label: Human-friendly label for the scope (snapshot name or "Current filters").
        runs_coins_per_hour: Number of runs contributing to the coins/hour average.
        runs_coins_per_wave: Number of runs contributing to the coins/wave average.
        runs_waves_reached: Number of runs contributing to the waves reached average.
        coins_per_hour: Average coins/hour across contributing runs, or None.
        coins_per_wave: Average coins/wave across contributing runs, or None.
        waves_reached: Average waves reached across contributing runs, or None.
    """

    label: str
    runs_coins_per_hour: int
    runs_coins_per_wave: int
    runs_waves_reached: int
    coins_per_hour: float | None
    coins_per_wave: float | None
    waves_reached: float | None


def generate_goal_weighted_advice(
    *,
    goal_label: str,
    baseline: GoalScopeSample,
    comparison: GoalScopeSample,
    weights: GoalWeights,
) -> tuple[AdviceItem, ...]:
    """Generate goal-aware, descriptive advice from two summarized scopes.

    Args:
        goal_label: User-selected intent label (e.g. "Economy / Farming").
        baseline: Baseline sample summary.
        comparison: Comparison sample summary.
        weights: User-controlled weights applied to percent-change deltas.

    Returns:
        A tuple containing a single AdviceItem.
    """

    basis = (
        "Basis: "
        f"{baseline.label} runs(cph={baseline.runs_coins_per_hour}, cpw={baseline.runs_coins_per_wave}, waves={baseline.runs_waves_reached}); "
        f"{comparison.label} runs(cph={comparison.runs_coins_per_hour}, cpw={comparison.runs_coins_per_wave}, waves={comparison.runs_waves_reached})."
    )
    context = (
        "Context: score = "
        f"({weights.coins_per_hour:g}×Δ% coins/hour) + "
        f"({weights.coins_per_wave:g}×Δ% coins/wave) + "
        f"({weights.waves_reached:g}×Δ% waves reached)."
    )

    if (
        baseline.runs_coins_per_hour < MIN_RUNS_FOR_ADVICE
        or baseline.runs_coins_per_wave < MIN_RUNS_FOR_ADVICE
        or baseline.runs_waves_reached < MIN_RUNS_FOR_ADVICE
        or comparison.runs_coins_per_hour < MIN_RUNS_FOR_ADVICE
        or comparison.runs_coins_per_wave < MIN_RUNS_FOR_ADVICE
        or comparison.runs_waves_reached < MIN_RUNS_FOR_ADVICE
    ):
        item = AdviceItem(
            title=f"For your selected goal: {goal_label} — {INSUFFICIENT_DATA_MESSAGE}",
            basis=basis,
            context=context,
            limitations=f"Limitations: Goal-aware summaries require at least {MIN_RUNS_FOR_ADVICE} runs per scope.",
        )
        _assert_non_prescriptive(item)
        return (item,)

    def percent_change(baseline_value: float | None, comparison_value: float | None) -> float | None:
        """Return percent change (B-A)/A*100 or None when unavailable."""

        if baseline_value is None or comparison_value is None:
            return None
        if baseline_value == 0:
            return None
        return ((comparison_value - baseline_value) / baseline_value) * 100.0

    pct_cph = percent_change(baseline.coins_per_hour, comparison.coins_per_hour)
    pct_cpw = percent_change(baseline.coins_per_wave, comparison.coins_per_wave)
    pct_waves = percent_change(baseline.waves_reached, comparison.waves_reached)

    if pct_cph is None or pct_cpw is None or pct_waves is None:
        item = AdviceItem(
            title=f"For your selected goal: {goal_label} — {INSUFFICIENT_DATA_MESSAGE}",
            basis=basis,
            context=context,
            limitations="Limitations: One or more required averages are missing or have a zero baseline.",
        )
        _assert_non_prescriptive(item)
        return (item,)

    score = (
        (weights.coins_per_hour * pct_cph)
        + (weights.coins_per_wave * pct_cpw)
        + (weights.waves_reached * pct_waves)
    )

    title = f"For your selected goal: {goal_label} — weighted percent index: {score:+.2f}"
    breakdown = f"Δ%: coins/hour={pct_cph:+.2f}%, coins/wave={pct_cpw:+.2f}%, waves reached={pct_waves:+.2f}%."
    item = AdviceItem(
        title=title,
        basis=basis,
        context=f"{context} {breakdown}",
        limitations="Limitations: This index is a transparent summary of percent changes, not a prediction.",
    )
    _assert_non_prescriptive(item)
    return (item,)


def _assert_non_prescriptive(item: AdviceItem) -> None:
    """Raise when advice contains forbidden imperative language."""

    combined = " ".join((item.title, item.basis, item.context, item.limitations)).casefold()
    for token in _FORBIDDEN_TOKENS:
        if token in combined:
            raise ValueError(f"Advice contains forbidden token: {token!r}")
