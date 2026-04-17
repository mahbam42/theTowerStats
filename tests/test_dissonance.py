"""Unit tests for Dissonance progression helpers."""

from __future__ import annotations

import pytest

from core.dissonance import next_dissonance_level

pytestmark = pytest.mark.unit


@pytest.mark.regression
def test_next_dissonance_level_starts_first_logged_clear_at_level_three() -> None:
    """The first logged Dissonance clear should unlock the in-game level 3 bonus."""

    assert next_dissonance_level(None) == 3
    assert next_dissonance_level(1) == 3


def test_next_dissonance_level_advances_existing_progress_by_one() -> None:
    """Existing Dissonance progress should continue increasing one level per clear."""

    assert next_dissonance_level(3) == 4
    assert next_dissonance_level(7) == 8
