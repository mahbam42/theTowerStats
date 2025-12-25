"""Unit tests for delta formatting precision."""

from __future__ import annotations

import pytest

from core.upgradeables import format_delta
from definitions.models import Unit

pytestmark = pytest.mark.unit


def test_format_delta_preserves_decimal_precision_for_multipliers() -> None:
    """Multiplier deltas retain decimals when the raw strings include them."""

    assert format_delta(current_raw="10.3", next_raw="10.7", unit_kind=str(Unit.Kind.MULTIPLIER)) == "+0.4x"
    assert format_delta(current_raw="3.9", next_raw="11.1", unit_kind=str(Unit.Kind.MULTIPLIER)) == "+7.2x"
