"""Card dashboard helpers for deriving display-only values.

Cards have editable inventory counts (progress toward the next tier) and derived
boost levels (stars). The dashboard uses deterministic rollover rules to keep
stored (stars, inventory) internally consistent.
"""

from __future__ import annotations

from dataclasses import dataclass


MAX_CARD_LEVEL = 7
MAX_CARD_INVENTORY = 32
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


@dataclass(frozen=True, slots=True)
class TotalCardsProgress:
    """Aggregate card progress values for the Cards dashboard.

    Attributes:
        total_copies: Total copies required to fully max all card definitions.
        copies_collected: Copies implied by the stored player card state.
        copies_remaining: Remaining copies to fully max all card definitions.
        maxed_cards: Number of cards at level 7 and clamped at 32/32.
        progress_percent: Overall completion percent, from 0.0 to 100.0.
        gems_needed: Estimated gems required to buy the remaining copies.
        events_needed: Estimated event missions required to earn `gems_needed`.
    """

    total_copies: int
    copies_collected: int
    copies_remaining: int
    maxed_cards: int
    progress_percent: float
    gems_needed: int
    events_needed: int


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


def total_copies_for_card_definitions(*, definition_count: int) -> int:
    """Return total copies required to fully max the given number of cards.

    Args:
        definition_count: Number of known card definitions.

    Returns:
        The number of copies required to reach level 7 and inventory 32/32 for
        every card.
    """

    per_card = sum(CARD_LEVEL_THRESHOLDS[level] for level in range(1, MAX_CARD_LEVEL)) + MAX_CARD_INVENTORY
    return max(0, int(definition_count)) * per_card


def derive_total_cards_progress(
    *, definition_count: int, card_states: list[tuple[int, int]]
) -> TotalCardsProgress:
    """Derive aggregate Cards dashboard progress from stored card state.

    This treats each entry in `card_states` as a stored `(stars_unlocked, inventory_count)`
    pair, then normalizes the values using the same rollover/clamp rules as the
    per-card dashboard table.

    Args:
        definition_count: Number of known card definitions (used for totals).
        card_states: Stored card state pairs aligned to known definitions.

    Returns:
        A TotalCardsProgress DTO for display.
    """

    total_copies = total_copies_for_card_definitions(definition_count=definition_count)

    copies_collected = 0
    maxed_cards = 0
    for stars_unlocked, inventory_count in card_states:
        progress = derive_card_progress(stars_unlocked=stars_unlocked, inventory_count=inventory_count)
        copies_collected += sum(CARD_LEVEL_THRESHOLDS[level] for level in range(1, progress.level)) + progress.inventory
        if progress.is_maxed:
            maxed_cards += 1

    copies_collected = max(0, min(copies_collected, total_copies)) if total_copies else max(0, copies_collected)
    copies_remaining = max(0, total_copies - copies_collected)
    progress_percent = ((copies_collected / total_copies) * 100.0) if total_copies else 0.0

    packs_needed = (copies_remaining + 9) // 10
    gems_needed = packs_needed * 200
    events_needed = (gems_needed + 1599) // 1600 if gems_needed else 0

    return TotalCardsProgress(
        total_copies=total_copies,
        copies_collected=copies_collected,
        copies_remaining=copies_remaining,
        maxed_cards=maxed_cards,
        progress_percent=progress_percent,
        gems_needed=gems_needed,
        events_needed=events_needed,
    )
