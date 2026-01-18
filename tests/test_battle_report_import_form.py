"""Unit tests for BattleReportImportForm."""

from __future__ import annotations

import pytest

from core.forms import BattleReportImportForm


@pytest.mark.regression
@pytest.mark.unit
def test_import_form_accepts_new_preset_name() -> None:
    """New presets can be supplied when the Create new preset option is selected."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Tier: 1",
            "Wave: 10",
            "Real Time: 00:10:00",
            "Coins earned: 1200",
        ]
    )
    form = BattleReportImportForm(
        data={"raw_text": raw_text, "preset_name": "__new__", "new_preset_name": "Farming"}
    )
    assert form.is_valid()
    assert form.cleaned_data["preset_name"] == "Farming"


@pytest.mark.unit
def test_import_form_requires_tournament_rank() -> None:
    """Tournament imports require a rank selection."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Tier: 1",
            "Wave: 10",
            "Real Time: 00:10:00",
            "Coins earned: 1200",
        ]
    )
    form = BattleReportImportForm(data={"raw_text": raw_text, "is_tournament": "on"})
    assert not form.is_valid()
    assert "tournament_rank" in form.errors


@pytest.mark.unit
def test_import_form_accepts_tournament_rank() -> None:
    """Tournament imports validate when a rank is provided."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Tier: 1",
            "Wave: 10",
            "Real Time: 00:10:00",
            "Coins earned: 1200",
        ]
    )
    form = BattleReportImportForm(
        data={"raw_text": raw_text, "is_tournament": "on", "tournament_rank": "gold"}
    )
    assert form.is_valid()
