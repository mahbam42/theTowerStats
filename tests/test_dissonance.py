"""Unit tests for Dissonance progression helpers."""

from __future__ import annotations

from decimal import Decimal

import pytest

from core.dissonance import effective_multiplier, next_dissonance_level

pytestmark = pytest.mark.unit


@pytest.mark.regression
def test_next_dissonance_level_starts_first_logged_clear_at_level_three() -> None:
    """The first logged Dissonance clear should unlock the in-game level 3 bonus."""

    assert next_dissonance_level(None) == 3
    assert next_dissonance_level(1) == 3


def test_next_dissonance_level_advances_existing_progress_by_one() -> None:
    """Existing Dissonance progress should continue increasing one level per clear."""

    assert next_dissonance_level(3) == 4
    assert next_dissonance_level(4) == 5


@pytest.mark.regression
def test_next_dissonance_level_caps_utility_at_three() -> None:
    """Utility Dissonance should stop increasing once it reaches the 3x cap."""

    assert next_dissonance_level(1, dissonance_type="utility") == 3
    assert next_dissonance_level(3, dissonance_type="utility") == 3
    assert next_dissonance_level(4, dissonance_type="utility") == 3


@pytest.mark.regression
def test_next_dissonance_level_caps_other_types_at_five() -> None:
    """Attack, Defense, and Ultimate Weapon Dissonance should stop at 5x."""

    assert next_dissonance_level(4, dissonance_type="attack") == 5
    assert next_dissonance_level(5, dissonance_type="defense") == 5
    assert next_dissonance_level(6, dissonance_type="ultimate_weapon") == 5


@pytest.mark.regression
def test_effective_multiplier_clamps_utility_snapshot_levels_to_three() -> None:
    """Utility multiplier display should respect the 3x cap even for stale higher snapshots."""

    assert effective_multiplier(
        multiplier_level=7,
        wave=1959,
        dissonance_type="utility",
    ) == Decimal("1.3881")
