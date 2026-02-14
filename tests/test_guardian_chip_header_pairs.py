"""Unit tests for guardian chip header pairing rules."""

from __future__ import annotations

import pytest

from definitions.wiki_rebuild import _guardian_header_pairs

pytestmark = pytest.mark.unit


def test_guardian_header_pairs_supports_scout_chip() -> None:
    """Scout chip headers should map to cooldown, range bonus, and duration."""

    raw_row = {
        "Cooldown": "105s",
        "Bits": "0",
        "Range Bonus": "2.0x",
        "Bits__2": "0",
        "Duration": "5s",
        "Bits__3": "0",
        "_wiki_entity_id": "scout",
        "Guardian": "Scout",
        "Level": "1",
    }

    pairs = _guardian_header_pairs(raw_row, slug="scout")

    assert pairs == [
        ("Cooldown", "Bits"),
        ("Range Bonus", "Bits__2"),
        ("Duration", "Bits__3"),
    ]
