"""Targeted tests for Phase 1.5 quantity normalization."""

from __future__ import annotations

from decimal import Decimal

from analysis.quantity import UnitType, parse_quantity


def test_parse_quantity_handles_compact_suffixes() -> None:
    """Parse compact K/M/q suffixes into scaled Decimals."""

    parsed = parse_quantity("7.67M", unit_type=UnitType.coins)
    assert parsed.raw_value == "7.67M"
    assert parsed.normalized_value == Decimal("7670000")
    assert parsed.magnitude == "m"
    assert parsed.unit_type == UnitType.coins

    parsed = parse_quantity("111.78q", unit_type=UnitType.damage)
    assert parsed.normalized_value == Decimal("111780000000000000")
    assert parsed.magnitude == "q"
    assert parsed.unit_type == UnitType.damage

    parsed = parse_quantity("1.44K")
    assert parsed.normalized_value == Decimal("1440")
    assert parsed.magnitude == "k"
    assert parsed.unit_type == UnitType.count


def test_parse_quantity_handles_multiplier_and_percent() -> None:
    """Parse multiplier-style values into normalized Decimals."""

    parsed = parse_quantity("x1.15")
    assert parsed.normalized_value == Decimal("1.15")
    assert parsed.magnitude is None
    assert parsed.unit_type == UnitType.multiplier

    parsed = parse_quantity("15%")
    assert parsed.normalized_value == Decimal("0.15")
    assert parsed.magnitude is None
    assert parsed.unit_type == UnitType.multiplier


def test_parse_quantity_never_raises_on_unknown_formats() -> None:
    """Return a Quantity with `normalized_value=None` for unknown inputs."""

    parsed = parse_quantity("not-a-number", unit_type=UnitType.coins)
    assert parsed.normalized_value is None
    assert parsed.unit_type == UnitType.coins

