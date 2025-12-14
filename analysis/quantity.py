"""Best-effort unit/quantity parsing utilities.

Phase 1.5 introduces a small normalization layer for compact numeric strings
commonly found in Battle Reports (e.g. `7.67M`, `x1.15`, `15%`).

This module is intentionally:
- pure (no Django imports, no database writes),
- defensive (never raises on unknown formats),
- minimal (only supports formats needed by Phase 1 inputs so far).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Final


class UnitType(Enum):
    """Supported unit categories for Phase 1.5."""

    coins = "coins"
    damage = "damage"
    count = "count"
    time = "time"
    multiplier = "multiplier"


@dataclass(frozen=True)
class Quantity:
    """A parsed quantity with both raw and normalized representations.

    Attributes:
        raw_value: The original raw string value (trimmed).
        normalized_value: The parsed numeric value as a Decimal, or None if the
            value could not be parsed.
        magnitude: The compact magnitude suffix (e.g. `k`, `m`, `b`, `t`, `q`),
            or None when not applicable.
        unit_type: The category of unit this value represents.
    """

    raw_value: str
    normalized_value: Decimal | None
    magnitude: str | None
    unit_type: UnitType


_MAGNITUDE_MULTIPLIERS: Final[dict[str, Decimal]] = {
    "": Decimal(1),
    "k": Decimal(1_000),
    "m": Decimal(1_000_000),
    "b": Decimal(1_000_000_000),
    "t": Decimal(1_000_000_000_000),
    "q": Decimal(1_000_000_000_000_000),
}


def parse_quantity(raw_value: str, *, unit_type: UnitType = UnitType.count) -> Quantity:
    """Parse a compact quantity string into a normalized Decimal.

    Args:
        raw_value: Raw value string (e.g. `7.67M`, `x1.15`, `15%`).
        unit_type: Unit category to assign for non-annotated values.

    Returns:
        Quantity where `normalized_value` is None when parsing fails.

    Notes:
        - A leading `x` forces `unit_type=multiplier` and parses the remainder.
        - A trailing `%` forces `unit_type=multiplier` and normalizes as a
          fraction (e.g. `15%` -> `0.15`).
        - Magnitude suffixes are case-insensitive and stored lowercased.
    """

    trimmed = raw_value.strip()
    if not trimmed:
        return Quantity(
            raw_value=trimmed, normalized_value=None, magnitude=None, unit_type=unit_type
        )

    if trimmed[:1].casefold() == "x":
        return _parse_multiplier(trimmed)

    if trimmed.endswith("%"):
        return _parse_percent(trimmed)

    return _parse_compact_number(trimmed, unit_type=unit_type)


def _parse_multiplier(value: str) -> Quantity:
    """Parse `x1.15` multiplier strings."""

    number_text = value[1:].strip()
    number = _parse_decimal(number_text)
    return Quantity(
        raw_value=value.strip(),
        normalized_value=number,
        magnitude=None,
        unit_type=UnitType.multiplier,
    )


def _parse_percent(value: str) -> Quantity:
    """Parse percent strings like `15%` into fractional multipliers."""

    number_text = value[:-1].strip()
    number = _parse_decimal(number_text)
    if number is None:
        normalized = None
    else:
        normalized = number / Decimal(100)
    return Quantity(
        raw_value=value.strip(),
        normalized_value=normalized,
        magnitude=None,
        unit_type=UnitType.multiplier,
    )


def _parse_compact_number(value: str, *, unit_type: UnitType) -> Quantity:
    """Parse `7.67M`-style compact numbers."""

    cleaned = value.strip()
    prefix_stripped = cleaned.lstrip("$")
    suffix = ""
    if prefix_stripped and prefix_stripped[-1].isalpha():
        suffix = prefix_stripped[-1].casefold()
        number_text = prefix_stripped[:-1]
    else:
        number_text = prefix_stripped

    multiplier = _MAGNITUDE_MULTIPLIERS.get(suffix)
    if multiplier is None:
        return Quantity(
            raw_value=cleaned, normalized_value=None, magnitude=suffix or None, unit_type=unit_type
        )

    number = _parse_decimal(number_text)
    if number is None:
        normalized = None
    else:
        normalized = number * multiplier

    return Quantity(
        raw_value=cleaned,
        normalized_value=normalized,
        magnitude=suffix or None,
        unit_type=unit_type,
    )


def _parse_decimal(number_text: str) -> Decimal | None:
    """Parse a Decimal from a Battle Report-style numeric string."""

    cleaned = number_text.replace(",", "").strip()
    if not cleaned:
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None
