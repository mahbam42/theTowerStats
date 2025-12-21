"""Golden tests for Phase 2 delta calculations."""

from __future__ import annotations

import pytest

from analysis.deltas import delta

pytestmark = [pytest.mark.unit, pytest.mark.golden]


def test_delta_computes_absolute_and_percent() -> None:
    """Compute absolute and percent change between two values."""

    computed = delta(100.0, 120.0)
    assert computed.baseline == 100.0
    assert computed.comparison == 120.0
    assert computed.absolute == 20.0
    assert computed.percent == 0.2


def test_delta_handles_zero_baseline() -> None:
    """Return percent=None when baseline is 0 to avoid division by zero."""

    computed = delta(0.0, 10.0)
    assert computed.absolute == 10.0
    assert computed.percent is None
