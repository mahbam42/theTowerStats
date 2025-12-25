"""Goal-oriented cost computations for upgradeable parameters.

This module is intentionally pure (no Django imports) so it can be unit-tested
and reused across views without database coupling.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PerLevelCost:
    """A single upgrade step cost from `from_level` to `to_level`."""

    from_level: int
    to_level: int
    cost_raw: str
    cost_amount: int | None


@dataclass(frozen=True, slots=True)
class GoalCostBreakdown:
    """Computed remaining cost and optional per-level breakdown for a goal."""

    current_level_display: int
    current_level_for_calc: int
    target_level: int
    currency: str
    total_invested: int
    total_to_target: int
    total_remaining: int
    per_level: tuple[PerLevelCost, ...]
    assumptions: tuple[str, ...]


def parse_cost_amount(*, cost_raw: str | None) -> int | None:
    """Parse an integer amount from a raw cost string.

    Args:
        cost_raw: Raw cost string (e.g. "50", "1,250", or "50 Medals").

    Returns:
        Parsed integer amount when a number token is present, otherwise None.
    """

    if not cost_raw:
        return None
    match = re.search(r"([0-9][0-9,]*)", cost_raw)
    if not match:
        return None
    try:
        return int(match.group(1).replace(",", ""))
    except ValueError:
        return None


def compute_goal_cost_breakdown(
    *,
    costs_by_level: dict[int, str],
    currency: str,
    current_level_display: int,
    current_level_for_calc: int,
    current_is_assumed: bool,
    target_level: int,
) -> GoalCostBreakdown:
    """Compute remaining upgrade cost and per-level breakdown.

    Cost rows are expected to be keyed by the resulting level: the cost at level
    N is the price to upgrade from N-1 -> N (matching typical wiki tables).

    Args:
        costs_by_level: Mapping of resulting level -> cost_raw.
        currency: Currency label (e.g. "stones", "medals", "bits").
        current_level_display: Level to display in UI (may be a fallback).
        current_level_for_calc: Level used for remaining-cost calculation.
        current_is_assumed: Whether current level is a fallback value.
        target_level: Desired target level.

    Returns:
        GoalCostBreakdown with per-level costs and total remaining amount.
    """

    assumptions: list[str] = []
    if current_is_assumed:
        assumptions.append(
            "Current level is not recorded yet; remaining totals are computed from 0."
        )

    if target_level <= current_level_for_calc:
        return GoalCostBreakdown(
            current_level_display=current_level_display,
            current_level_for_calc=current_level_for_calc,
            target_level=target_level,
            currency=currency,
            total_invested=0,
            total_to_target=0,
            total_remaining=0,
            per_level=(),
            assumptions=tuple(assumptions),
        )

    if not costs_by_level:
        assumptions.append("No cost rows are available for this parameter.")
        return GoalCostBreakdown(
            current_level_display=current_level_display,
            current_level_for_calc=current_level_for_calc,
            target_level=target_level,
            currency=currency,
            total_invested=0,
            total_to_target=0,
            total_remaining=0,
            per_level=(),
            assumptions=tuple(assumptions),
        )

    min_level = min(costs_by_level)
    total_to_target = 0
    for to_level in range(min_level, target_level + 1):
        raw = costs_by_level.get(to_level)
        parsed = parse_cost_amount(cost_raw=raw)
        if parsed is not None:
            total_to_target += parsed
        elif raw is not None:
            assumptions.append(f"Unparseable cost for level {to_level}: {raw!r}.")
        else:
            assumptions.append(f"Missing cost row for level {to_level}.")

    total_invested = 0
    if current_level_for_calc >= min_level:
        for to_level in range(min_level, current_level_for_calc + 1):
            raw = costs_by_level.get(to_level)
            parsed = parse_cost_amount(cost_raw=raw)
            if parsed is not None:
                total_invested += parsed
            elif raw is not None:
                assumptions.append(f"Unparseable cost for level {to_level}: {raw!r}.")
            else:
                assumptions.append(f"Missing cost row for level {to_level}.")

    start_to_level = max(min_level, current_level_for_calc + 1)

    per_level: list[PerLevelCost] = []
    total_remaining = 0
    for to_level in range(start_to_level, target_level + 1):
        raw = costs_by_level.get(to_level)
        if raw is None:
            assumptions.append(f"Missing cost row for level {to_level}.")
            continue
        parsed = parse_cost_amount(cost_raw=raw)
        per_level.append(
            PerLevelCost(
                from_level=to_level - 1,
                to_level=to_level,
                cost_raw=raw,
                cost_amount=parsed,
            )
        )
        if parsed is not None:
            total_remaining += parsed

    return GoalCostBreakdown(
        current_level_display=current_level_display,
        current_level_for_calc=current_level_for_calc,
        target_level=target_level,
        currency=currency,
        total_invested=total_invested,
        total_to_target=total_to_target,
        total_remaining=total_remaining,
        per_level=tuple(per_level),
        assumptions=tuple(dict.fromkeys(assumptions)),
    )
