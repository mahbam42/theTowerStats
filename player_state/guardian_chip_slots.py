"""Guardian chip slot helpers for UI progression."""

from __future__ import annotations

GUARDIAN_CHIP_SLOT_COSTS: dict[int, str] = {
    2: "200 Bits",
    3: "300 Bits",
}


def guardian_chip_max_slots() -> int:
    """Return the maximum guardian chip slot count supported by known costs.

    Returns:
        Maximum slot number that has a known unlock cost, or 1 when none exist.
    """

    if not GUARDIAN_CHIP_SLOT_COSTS:
        return 1
    return max(GUARDIAN_CHIP_SLOT_COSTS.keys())


def guardian_chip_slot_unlock_cost_raw_for_slot(*, slot_number: int) -> str | None:
    """Return the raw unlock cost string for a specific slot number.

    Args:
        slot_number: Slot number to look up (1-indexed).

    Returns:
        Raw cost string for that slot (e.g. "200 Bits"), or None when unknown.
    """

    if slot_number <= 1:
        return None
    return GUARDIAN_CHIP_SLOT_COSTS.get(slot_number)


def next_guardian_chip_slot_unlock_cost_raw(*, unlocked: int) -> str | None:
    """Return the raw unlock cost string for the next guardian chip slot.

    Args:
        unlocked: Current number of unlocked slots.

    Returns:
        Raw cost string for the next slot, or None when unknown.
    """

    return guardian_chip_slot_unlock_cost_raw_for_slot(slot_number=unlocked + 1)
