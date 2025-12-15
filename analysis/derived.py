"""Derived metric helpers based on parameterized game mechanics.

This module contains deterministic, testable computations that combine
observations (run data) with parameterized effects (wiki-derived tables and
player context). It must remain pure and defensive: callers should receive
partial results instead of exceptions when inputs are missing.
"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random


@dataclass(frozen=True, slots=True)
class MonteCarloConfig:
    """Configuration for deterministic Monte Carlo computations.

    Args:
        trials: Number of simulated trials (must be > 0).
        seed: RNG seed used to ensure deterministic results in tests and UI.
    """

    trials: int
    seed: int


def effective_cooldown_seconds(
    *,
    base_seconds: float | None,
    reduction_fractions: tuple[float, ...],
) -> float | None:
    """Compute an effective cooldown in seconds after reductions.

    Formula (assumption):
        effective = base_seconds * (1 - sum(reduction_fractions))

    Reductions are treated as additive fractions (e.g. 10% -> 0.10). The result
    is clamped to >= 0.

    Args:
        base_seconds: Base cooldown in seconds.
        reduction_fractions: Sequence of fractional reductions (0..1).

    Returns:
        Effective cooldown in seconds, or None if base is missing/invalid.
    """

    if base_seconds is None or not (base_seconds > 0):
        return None
    total_reduction = 0.0
    for fraction in reduction_fractions:
        if fraction <= 0:
            continue
        total_reduction += fraction
    effective = base_seconds * (1.0 - total_reduction)
    if effective < 0:
        effective = 0.0
    return effective


def expected_multiplier_bernoulli(*, proc_chance: float | None, proc_multiplier: float | None) -> float | None:
    """Compute the expected multiplier for a Bernoulli proc.

    Args:
        proc_chance: Probability of proc in [0, 1].
        proc_multiplier: Multiplier applied on proc (>= 0).

    Returns:
        Expected multiplier E[M] = (1-p)*1 + p*m, or None if inputs are invalid.
    """

    if proc_chance is None or proc_multiplier is None:
        return None
    if not (0.0 <= proc_chance <= 1.0):
        return None
    if proc_multiplier < 0:
        return None
    return (1.0 - proc_chance) * 1.0 + proc_chance * proc_multiplier


def monte_carlo_expected_multiplier_bernoulli(
    *,
    proc_chance: float | None,
    proc_multiplier: float | None,
    config: MonteCarloConfig,
) -> float | None:
    """Estimate expected multiplier via deterministic Monte Carlo simulation.

    Args:
        proc_chance: Probability of proc in [0, 1].
        proc_multiplier: Multiplier applied on proc (>= 0).
        config: MonteCarloConfig controlling trial count and RNG seed.

    Returns:
        Estimated expected multiplier, or None if inputs are invalid.
    """

    if proc_chance is None or proc_multiplier is None:
        return None
    expected = expected_multiplier_bernoulli(
        proc_chance=proc_chance, proc_multiplier=proc_multiplier
    )
    if expected is None:
        return None
    if config.trials <= 0:
        return None

    rng = Random(config.seed)
    total = 0.0
    for _ in range(config.trials):
        if rng.random() < proc_chance:
            total += proc_multiplier
        else:
            total += 1.0
    return total / config.trials


def apply_multiplier(value: float | None, *, multiplier: float | None) -> float | None:
    """Apply a multiplier to a numeric value.

    Args:
        value: Baseline value.
        multiplier: Multiplier factor.

    Returns:
        `value * multiplier`, or None if inputs are missing/invalid.
    """

    if value is None or multiplier is None:
        return None
    return value * multiplier
