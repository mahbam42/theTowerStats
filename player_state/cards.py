"""Card dashboard helpers for deriving display-only values.

Cards have editable inventory counts, but their derived level is intentionally
computed rather than stored as a separate mutable field.
"""

from __future__ import annotations


def derive_card_level(*, inventory_count: int) -> int:
    """Derive a card "level" from an inventory count.

    Args:
        inventory_count: Non-negative count of owned card copies.

    Returns:
        A non-negative derived level used for UI display.
    """

    return max(0, int(inventory_count))

