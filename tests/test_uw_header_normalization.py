import pytest

from definitions.wiki_rebuild import _bot_cost_header, _derive_card_effect_raw, _uw_cost_header, _uw_value_header_key


@pytest.mark.unit
@pytest.mark.regression
def test_uw_cost_header_handles_nbsp_value_header() -> None:
    """Ensure UW cost headers resolve when value headers contain nbsp spacing."""

    raw_row = {
        "Damage\u00a0%": "10x",
        "Cost": "0",
        "Quantity": "3",
        "Cost__2": "0",
    }
    resolved_value_header = _uw_value_header_key(value_header="Damage %", raw_row=raw_row)

    assert resolved_value_header == "Damage\u00a0%"
    assert _uw_cost_header(value_header=resolved_value_header, raw_row=raw_row) == "Cost"


@pytest.mark.unit
@pytest.mark.regression
def test_bot_cost_header_handles_nbsp() -> None:
    """Ensure bot cost headers resolve when headers contain nbsp spacing."""

    raw_row = {
        "Level": "1",
        "Cost\u00a0": "100",
        "Duration": "20",
        "Cooldown": "120",
        "Bonus": "3.5",
        "Range": "25",
    }

    assert _bot_cost_header(raw_row=raw_row) == "Cost\u00a0"


@pytest.mark.unit
@pytest.mark.regression
def test_card_effect_header_handles_nbsp() -> None:
    """Ensure card effect header resolves when it contains nbsp spacing."""

    raw_row: dict[str, object] = {"Effect\u00a0": "x 1.2"}

    assert _derive_card_effect_raw(raw_row, description="") == "x 1.2"
