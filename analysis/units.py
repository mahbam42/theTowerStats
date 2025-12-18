"""Unit validation and formatting helpers.

Phase 6 introduces a strict unit contract for any metric that is displayed in
dashboards. Unlike `analysis.quantity.parse_quantity`, this module is allowed
to fail fast when a value violates the expected unit contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .quantity import Quantity, UnitType, parse_quantity


class UnitValidationError(ValueError):
    """Raised when a quantity does not satisfy a unit contract."""

    def __init__(self, *, raw_value: str, expected: UnitType, actual: UnitType) -> None:
        """Initialize the error.

        Args:
            raw_value: Original raw input.
            expected: Expected UnitType contract.
            actual: Parsed UnitType from the raw value.
        """

        super().__init__(
            f"Ambiguous or mismatched units for {raw_value!r}: expected {expected.value}, got {actual.value}."
        )
        self.raw_value = raw_value
        self.expected = expected
        self.actual = actual


@dataclass(frozen=True, slots=True)
class UnitContract:
    """Contract describing the expected unit type for a parsed value.

    Args:
        unit_type: Expected UnitType for the value.
        allow_zero: Whether a numeric zero is considered valid.
    """

    unit_type: UnitType
    allow_zero: bool = True


@dataclass(frozen=True, slots=True)
class ValidatedQuantity:
    """A validated quantity value that satisfies a UnitContract.

    Args:
        raw_value: Raw value string (trimmed).
        normalized_value: Parsed Decimal value.
        unit_type: UnitType that was validated against the contract.
        magnitude: Magnitude suffix (k/m/b/t/q) when present.
    """

    raw_value: str
    normalized_value: Decimal
    unit_type: UnitType
    magnitude: str | None


def parse_validated_quantity(raw_value: str, *, contract: UnitContract) -> ValidatedQuantity:
    """Parse and validate a quantity string against a strict unit contract.

    Args:
        raw_value: Raw Battle Report value (e.g. `7.67M`, `$55.90M`, `x1.15`, `15%`).
        contract: UnitContract describing the expected unit type.

    Returns:
        ValidatedQuantity with a non-None Decimal value.

    Raises:
        UnitValidationError: When the parsed unit type does not match the contract.
        ValueError: When the value cannot be parsed into a numeric Decimal.
    """

    parsed = parse_quantity(raw_value, unit_type=contract.unit_type)
    if parsed.normalized_value is None:
        raise ValueError(f"Could not parse numeric value from {raw_value!r}.")

    if parsed.unit_type is not contract.unit_type:
        raise UnitValidationError(raw_value=raw_value, expected=contract.unit_type, actual=parsed.unit_type)

    if not contract.allow_zero and parsed.normalized_value == 0:
        raise ValueError(f"Zero is not allowed for {raw_value!r}.")

    return ValidatedQuantity(
        raw_value=parsed.raw_value,
        normalized_value=parsed.normalized_value,
        unit_type=parsed.unit_type,
        magnitude=parsed.magnitude,
    )


def coerce_non_negative_int(quantity: Quantity) -> int | None:
    """Coerce a parsed Quantity to a non-negative integer if possible.

    Args:
        quantity: Quantity returned from parsing routines.

    Returns:
        An int when normalized_value is present and non-negative; otherwise None.
    """

    if quantity.normalized_value is None:
        return None
    if quantity.normalized_value < 0:
        return None
    try:
        return int(quantity.normalized_value)
    except (OverflowError, ValueError):
        return None
