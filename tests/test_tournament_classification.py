"""Unit tests for derived tournament run classification."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from core.tournament import extract_tier_label, is_tournament, tournament_bracket

pytestmark = pytest.mark.unit


def test_extract_tier_label_finds_colon_or_tab_value() -> None:
    """Extract Tier values from common Battle Report formats."""

    assert extract_tier_label("Battle Report\nTier: 6\n") == "6"
    assert extract_tier_label("Battle Report\nTier\t3+\n") == "3+"
    assert extract_tier_label("Battle Report\nWave: 1\n") is None


def test_tournament_bracket_normalizes_numeric_plus_label() -> None:
    """Return a normalized bracket label for tournament Tier inputs."""

    assert tournament_bracket("Battle Report\nTier: 3+\n") == "3+"
    assert tournament_bracket("Battle Report\nTier:\t  8 + \n") == "8+"
    assert tournament_bracket("Battle Report\nTier: 6\n") is None


def test_is_tournament_accepts_battlereport_like_objects() -> None:
    """Classify tournament runs via duck-typed objects containing raw_text."""

    @dataclass(frozen=True)
    class Record:
        raw_text: str

    assert is_tournament(Record(raw_text="Battle Report\nTier: 5+\n")) is True
    assert is_tournament(Record(raw_text="Battle Report\nTier: 12\n")) is False


def test_is_tournament_accepts_progress_like_objects() -> None:
    """Classify tournament runs via objects that expose battle_report.raw_text."""

    @dataclass(frozen=True)
    class Report:
        raw_text: str

    @dataclass(frozen=True)
    class Progress:
        battle_report: Report

    assert is_tournament(Progress(battle_report=Report(raw_text="Battle Report\nTier: 3+\n"))) is True
    assert tournament_bracket(Progress(battle_report=Report(raw_text="Battle Report\nTier: 3+\n"))) == "3+"

