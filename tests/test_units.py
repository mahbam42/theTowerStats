"""Targeted tests for Phase 6 unit contracts and validation."""

from __future__ import annotations

from decimal import Decimal

import pytest

from analysis.quantity import UnitType
from analysis.units import UnitContract, UnitValidationError, parse_validated_quantity


def test_parse_validated_quantity_rejects_multiplier_for_non_multiplier_contract() -> None:
    """Reject `%` and `x…` values when the contract expects a non-multiplier."""

    with pytest.raises(UnitValidationError):
        parse_validated_quantity("15%", contract=UnitContract(unit_type=UnitType.coins))

    with pytest.raises(UnitValidationError):
        parse_validated_quantity("x1.15", contract=UnitContract(unit_type=UnitType.coins))


def test_parse_validated_quantity_accepts_multiplier_contract() -> None:
    """Accept `%` and `x…` values when the contract expects multipliers."""

    parsed = parse_validated_quantity("15%", contract=UnitContract(unit_type=UnitType.multiplier))
    assert parsed.normalized_value == Decimal("0.15")
    assert parsed.unit_type is UnitType.multiplier

    parsed = parse_validated_quantity("x1.15", contract=UnitContract(unit_type=UnitType.multiplier))
    assert parsed.normalized_value == Decimal("1.15")
    assert parsed.unit_type is UnitType.multiplier


def test_parse_validated_quantity_parses_magnitude_suffixes() -> None:
    """Parse K/M/B/T magnitude suffixes deterministically."""

    assert parse_validated_quantity("1K", contract=UnitContract(unit_type=UnitType.coins)).normalized_value == Decimal(
        "1000"
    )
    assert parse_validated_quantity("2.5M", contract=UnitContract(unit_type=UnitType.coins)).normalized_value == Decimal(
        "2500000"
    )
    assert parse_validated_quantity("3B", contract=UnitContract(unit_type=UnitType.damage)).normalized_value == Decimal(
        "3000000000"
    )
    assert parse_validated_quantity("4T", contract=UnitContract(unit_type=UnitType.damage)).normalized_value == Decimal(
        "4000000000000"
    )


def test_parse_validated_quantity_rejects_time_strings_for_numeric_contract() -> None:
    """Reject time-like strings that are not part of numeric parsing."""

    with pytest.raises(ValueError):
        parse_validated_quantity("1h 2m 3s", contract=UnitContract(unit_type=UnitType.coins))

