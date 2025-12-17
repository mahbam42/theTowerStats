"""Unit tests for card slot lookup and economy helpers."""

from __future__ import annotations

import pytest

from definitions.models import WikiData
from player_state.card_slots import (
    card_slot_max_slots,
    card_slot_unlock_cost_raw_for_slot,
    next_card_slot_unlock_cost_raw,
)
from player_state.economy import enforce_and_deduct_gems_if_tracked, parse_cost_amount
from player_state.models import Player


def _wikidata_row(*, canonical_name: str, entity_id: str, raw_row: dict[str, str], content_hash: str) -> WikiData:
    """Create a minimal WikiData row for card slot fixtures."""

    return WikiData.objects.create(
        page_url="https://example.test/wiki/Cards",
        canonical_name=canonical_name,
        entity_id=entity_id,
        content_hash=content_hash,
        raw_row=raw_row,
        source_section="cards_table_0",
        parse_version="cards_v1",
    )


@pytest.mark.django_db
def test_card_slot_helpers_return_none_when_wikidata_missing() -> None:
    """Card slot helpers return None when wiki slot data is unavailable."""

    assert card_slot_max_slots() is None
    assert next_card_slot_unlock_cost_raw(unlocked=0) is None
    assert card_slot_unlock_cost_raw_for_slot(slot_number=1) is None


@pytest.mark.django_db
def test_card_slot_helpers_extract_max_and_costs() -> None:
    """Card slot helpers derive max slots and per-slot unlock cost."""

    _wikidata_row(canonical_name="1", entity_id="1", raw_row={"Slots": "1", "Cost": "10 Gems"}, content_hash="a" * 64)
    _wikidata_row(canonical_name="2", entity_id="2", raw_row={"Slots": "2", "Cost": "25 Gems"}, content_hash="b" * 64)

    assert card_slot_max_slots() == 2
    assert next_card_slot_unlock_cost_raw(unlocked=0) == "10 Gems"
    assert next_card_slot_unlock_cost_raw(unlocked=1) == "25 Gems"
    assert card_slot_unlock_cost_raw_for_slot(slot_number=2) == "25 Gems"


def test_parse_cost_amount_extracts_integer() -> None:
    """parse_cost_amount extracts the first integer-like token."""

    assert parse_cost_amount(cost_raw=None) is None
    assert parse_cost_amount(cost_raw="") is None
    assert parse_cost_amount(cost_raw="Not tracked yet") is None
    assert parse_cost_amount(cost_raw="50 Gems") == 50
    assert parse_cost_amount(cost_raw="1,250") == 1250
    assert parse_cost_amount(cost_raw="Cost: 2,500 Gems") == 2500


@pytest.mark.django_db
def test_enforce_and_deduct_gems_is_noop_when_player_has_no_gem_field() -> None:
    """Gem enforcement does not block when gem balance is not tracked."""

    player = Player.objects.create(name="default", card_slots_unlocked=0)
    result, parsed_cost = enforce_and_deduct_gems_if_tracked(player=player, cost_raw="50 Gems")
    assert result is None
    assert parsed_cost == 50

