"""Card dashboard helpers for deriving display-only values.

Cards have editable inventory counts (progress toward the next tier) and derived
boost levels (stars). The dashboard uses deterministic rollover rules to keep
stored (stars, inventory) internally consistent.
"""

from __future__ import annotations

from dataclasses import dataclass


MAX_CARD_LEVEL = 7
CARD_LEVEL_THRESHOLDS: dict[int, int] = {
    1: 0,
    2: 3,
    3: 5,
    4: 8,
    5: 12,
    6: 20,
    7: 32,
}


@dataclass(frozen=True, slots=True)
class CardProgress:
    """Derived card progress state for UI display.

    Attributes:
        level: Derived card boost level (1..7). Level 7 is the max.
        inventory: Current inventory progress toward the next tier.
        threshold: Inventory cap for the current tier (shown as `inventory / threshold`).
        is_maxed: True when the card is at max level and inventory is clamped.
    """

    level: int
    inventory: int
    threshold: int
    is_maxed: bool


def apply_inventory_rollover(*, level: int, inventory: int) -> tuple[int, int]:
    """Apply rollover rules to keep card (level, inventory) consistent.

    This implements the Cards Dashboard semantics:
    - inventory represents progress toward the next level
    - when inventory meets/exceeds the tier threshold, it rolls over
    - rollovers can span multiple tiers in a single update
    - progress clamps at max level (7), stopping at 32 / 32

    Args:
        level: Current boost level (0..7). Values <= 0 are treated as level 1.
        inventory: New inventory value (non-negative).

    Returns:
        A tuple of (new_level, new_inventory) after applying rollover and clamping.
    """

    current_level = max(1, min(MAX_CARD_LEVEL, int(level)))
    current_inventory = max(0, int(inventory))

    while current_level < MAX_CARD_LEVEL:
        threshold = CARD_LEVEL_THRESHOLDS.get(current_level, 0)
        if threshold <= 0:
            if current_inventory <= 0:
                break
            current_level += 1
            continue

        if current_inventory < threshold:
            break

        current_inventory -= threshold
        current_level += 1

    if current_level >= MAX_CARD_LEVEL:
        current_level = MAX_CARD_LEVEL
        current_inventory = min(current_inventory, CARD_LEVEL_THRESHOLDS[MAX_CARD_LEVEL])

    return current_level, current_inventory


def derive_card_progress(*, stars_unlocked: int, inventory_count: int) -> CardProgress:
    """Derive display state for a card from stored stars and inventory.

    Args:
        stars_unlocked: Stored boost level (0..7). Values <= 0 are treated as level 1 for display.
        inventory_count: Stored inventory progress value.

    Returns:
        A CardProgress DTO containing the normalized level, inventory, threshold, and maxed flag.
    """

    normalized_level, normalized_inventory = apply_inventory_rollover(
        level=stars_unlocked,
        inventory=inventory_count,
    )
    threshold = CARD_LEVEL_THRESHOLDS.get(normalized_level, CARD_LEVEL_THRESHOLDS[MAX_CARD_LEVEL])
    is_maxed = normalized_level == MAX_CARD_LEVEL and normalized_inventory >= threshold
    return CardProgress(
        level=normalized_level,
        inventory=normalized_inventory,
        threshold=threshold,
        is_maxed=is_maxed,
    )
