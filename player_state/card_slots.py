"""Card slot helpers for UI progression.

These helpers translate wiki-derived card slot tables into display-ready values.
They are intentionally conservative: when slot data is missing or malformed, the
functions return None so the UI can fall back to "Not tracked yet".
"""

from __future__ import annotations

from typing import Final

from definitions.models import WikiData

_CARDS_SLOT_PARSE_VERSION: Final[str] = "cards_v1"
_CARDS_SLOT_SOURCE_PREFIX: Final[str] = "cards_table_"


def card_slot_max_slots() -> int | None:
    """Return the maximum card slot count when wiki slot data is available.

    Returns:
        The highest slot number found in the latest wiki slot table, or None
        when slot limits are not available.
    """

    latest_by_entity = _latest_slot_wikidata()
    if not latest_by_entity:
        return None

    max_slot = 0
    for record in latest_by_entity.values():
        slot_int = _parse_slot_number(record)
        if slot_int is None:
            continue
        max_slot = max(max_slot, slot_int)

    return max_slot or None


def next_card_slot_unlock_cost_raw(*, unlocked: int) -> str | None:
    """Return the raw unlock cost string for the next slot.

    Args:
        unlocked: Current number of unlocked slots.

    Returns:
        Raw cost string for the next slot (e.g. "50 Gems"), or None when the
        slot cost is missing/unknown.
    """

    return card_slot_unlock_cost_raw_for_slot(slot_number=unlocked + 1)


def card_slot_unlock_cost_raw_for_slot(*, slot_number: int) -> str | None:
    """Return the raw unlock cost string for a specific slot number.

    Args:
        slot_number: Slot number to look up (1-indexed, as shown in the wiki).

    Returns:
        Raw cost string for that slot, or None when missing/unknown.
    """

    if slot_number <= 0:
        return None

    latest_by_entity = _latest_slot_wikidata()
    if not latest_by_entity:
        return None

    for record in latest_by_entity.values():
        slot_int = _parse_slot_number(record)
        if slot_int != slot_number:
            continue
        return _parse_slot_cost(record)

    return None


def _latest_slot_wikidata() -> dict[str, WikiData]:
    """Return latest cards slot WikiData rows keyed by entity id."""

    qs = (
        WikiData.objects.filter(
            parse_version=_CARDS_SLOT_PARSE_VERSION,
            source_section__startswith=_CARDS_SLOT_SOURCE_PREFIX,
        )
        .order_by("entity_id", "-last_seen", "-id")
        .only("entity_id", "canonical_name", "raw_row", "last_seen")
    )
    latest_by_entity: dict[str, WikiData] = {}
    for row in qs.iterator():
        latest_by_entity.setdefault(row.entity_id, row)
    return latest_by_entity


def _parse_slot_number(record: WikiData) -> int | None:
    """Extract a slot number from a wiki row."""

    raw_row = record.raw_row or {}
    slot_number = (
        raw_row.get("Slots")
        or raw_row.get("Slot")
        or raw_row.get("Card Slots")
        or record.canonical_name
    )
    try:
        return int(str(slot_number).strip())
    except (TypeError, ValueError):
        return None


def _parse_slot_cost(record: WikiData) -> str | None:
    """Extract the raw unlock cost value from a wiki row."""

    raw_row = record.raw_row or {}
    cost_raw = str(raw_row.get("Gem Cost") or raw_row.get("Cost") or raw_row.get("Unlock Cost") or "").strip()
    return cost_raw or None
