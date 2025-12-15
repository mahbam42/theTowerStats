"""Tests for populating Phase 3 card models from WikiData."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.models import CardDefinition, CardParameter, CardSlot
from core.wiki_ingestion import ingest_wiki_rows, scrape_entity_rows
from core.wiki_population import populate_card_slots_from_wiki, populate_cards_from_wiki


def _fixture_html(name: str) -> str:
    """Load HTML fixture content from the tests fixture directory."""

    fixture_path = Path(__file__).parent / "fixtures" / name
    return fixture_path.read_text(encoding="utf-8")


@pytest.mark.django_db
def test_populate_card_slots_from_wiki_creates_slots_with_source_revision() -> None:
    """Populate CardSlot rows from the wiki card-slots table."""

    html = _fixture_html("wiki_cards_page_list_of_cards_v1.html")
    rows = scrape_entity_rows(html, table_index=0, name_column=None)
    ingest_wiki_rows(
        rows,
        page_url="https://example.test/wiki/Cards",
        source_section="cards_table_0",
        parse_version="cards_v1",
        write=True,
    )

    summary = populate_card_slots_from_wiki(write=True)
    assert summary.created_card_slots == 1
    assert summary.updated_card_slots == 0

    slot = CardSlot.objects.get(slot_number=1)
    assert slot.unlock_cost_raw == "10"
    assert slot.source_wikidata is not None
    assert slot.source_wikidata.raw_row["Slots"] == "1"

    # Idempotent for the same revision.
    summary_again = populate_card_slots_from_wiki(write=True)
    assert summary_again.created_card_slots == 0
    assert summary_again.updated_card_slots == 0


@pytest.mark.django_db
def test_populate_cards_from_wiki_creates_definitions_and_parameters() -> None:
    """Populate CardDefinition + CardParameter rows from the wiki cards list tables."""

    html = _fixture_html("wiki_cards_page_list_of_cards_v1.html")
    common_rows = scrape_entity_rows(
        html,
        table_index=1,
        name_column=None,
        extra_fields={"_wiki_table_label": "Common"},
    )
    ingest_wiki_rows(
        common_rows,
        page_url="https://example.test/wiki/Cards",
        source_section="cards_list_common_1",
        parse_version="cards_list_v1",
        write=True,
    )

    summary = populate_cards_from_wiki(write=True)
    assert summary.created_card_definitions == 1
    assert summary.created_card_parameters >= 2

    card = CardDefinition.objects.get(name="Coin Bonus")
    assert card.wiki_entity_id == "coin_bonus"
    assert CardParameter.objects.filter(card_definition=card, key="Effect", raw_value="+5%").exists()
    assert CardParameter.objects.filter(card_definition=card, key="Rarity", raw_value="Common").exists()

    # Idempotent for the same revision.
    summary_again = populate_cards_from_wiki(write=True)
    assert summary_again.created_card_definitions == 0
    assert summary_again.created_card_parameters == 0


@pytest.mark.django_db
def test_populate_cards_from_wiki_check_mode_performs_no_writes() -> None:
    """Dry-run mode reports counts without creating rows."""

    html = _fixture_html("wiki_cards_page_list_of_cards_v1.html")
    common_rows = scrape_entity_rows(
        html,
        table_index=1,
        name_column=None,
        extra_fields={"_wiki_table_label": "Common"},
    )
    ingest_wiki_rows(
        common_rows,
        page_url="https://example.test/wiki/Cards",
        source_section="cards_list_common_1",
        parse_version="cards_list_v1",
        write=True,
    )

    summary = populate_cards_from_wiki(write=False)
    assert summary.created_card_definitions == 1
    assert summary.created_card_parameters >= 1
    assert CardDefinition.objects.count() == 0
    assert CardParameter.objects.count() == 0
