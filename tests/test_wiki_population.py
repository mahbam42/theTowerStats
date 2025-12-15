from pathlib import Path

import pytest

from core.models import (
    BotDefinition,
    BotLevel,
    BotParameter,
    CardDefinition,
    CardParameter,
    CardSlot,
    GuardianChipLevel,
    GuardianChipParameter,
    UltimateWeaponLevel,
)
from core.parameter_registry import PARAMETER_KEY_REGISTRY
from core.wiki_ingestion import (
    ScrapedWikiRow,
    compute_content_hash,
    ingest_wiki_rows,
    make_entity_id,
    scrape_entity_rows,
)
from core.wiki_population import (
    populate_bots_from_wiki,
    populate_card_slots_from_wiki,
    populate_cards_from_wiki,
    populate_guardian_chips_from_wiki,
    populate_ultimate_weapons_from_wiki,
)


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

    # Idempotent for the same revision.
    summary_again = populate_card_slots_from_wiki(write=True)
    assert summary_again.created_card_slots == 0
    assert summary_again.updated_card_slots == 0


@pytest.mark.django_db
def test_populate_cards_from_wiki_records_metadata_and_no_parameters() -> None:
    """Populate CardDefinition rows and retain metadata without parameters."""

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
    assert summary.created_card_parameters == 0

    card = CardDefinition.objects.get(name="Coin Bonus")
    assert card.wiki_entity_id == "coin_bonus"
    assert card.rarity == "Common"
    assert CardParameter.objects.count() == 0


@pytest.mark.django_db
def test_parameters_require_level_fk() -> None:
    """Parameter models enforce a level foreign key."""

    bot = BotDefinition.objects.create(name="Amplify Bot")
    with pytest.raises(ValueError):
        BotParameter.objects.create(bot_definition=bot, bot_level=None, key="Damage", raw_value="10")


@pytest.mark.django_db
def test_unknown_headers_do_not_create_parameters() -> None:
    """Unregistered wiki headers are stored as WikiData only."""

    raw_row = {"Guardian": "Ally", "Level": "1", "Mystery": "???"}
    scraped = ScrapedWikiRow(
        canonical_name="Ally",
        entity_id=make_entity_id("Ally"),
        raw_row=raw_row,
        content_hash=compute_content_hash(raw_row),
    )
    ingest_wiki_rows(
        [scraped],
        page_url="https://example.test/wiki/Guardian",
        source_section="guardian_table",
        parse_version="guardian_chips_v1",
        write=True,
    )

    populate_guardian_chips_from_wiki(write=True)
    assert GuardianChipLevel.objects.count() == 1
    assert GuardianChipParameter.objects.count() == 0


@pytest.mark.django_db
def test_registry_enforces_three_parameters_per_level() -> None:
    """Guardian and UW ingestion enforces entity-scoped parameter keys."""

    guardian_row = {"Guardian": "Ally", "Level": "1", "Damage": "10", "Duration": "2", "Cooldown": "5"}
    guardian_scraped = ScrapedWikiRow(
        canonical_name="Ally",
        entity_id="ally",
        raw_row=guardian_row,
        content_hash=compute_content_hash(guardian_row),
    )
    uw_row = {
        "Ultimate Weapon": "Black Hole",
        "Level": "1",
        "Damage": "100",
        "Proc Chance": "20%",
        "Cooldown": "30",
    }
    uw_scraped = ScrapedWikiRow(
        canonical_name="Black Hole",
        entity_id="black_hole",
        raw_row=uw_row,
        content_hash=compute_content_hash(uw_row),
    )
    ingest_wiki_rows(
        [guardian_scraped],
        page_url="https://example.test/wiki/Items",
        source_section="combined",
        parse_version="guardian_chips_v1",
        write=True,
    )
    ingest_wiki_rows(
        [uw_scraped],
        page_url="https://example.test/wiki/Weapons",
        source_section="uw_table",
        parse_version="ultimate_weapons_v1",
        write=True,
    )

    populate_guardian_chips_from_wiki(write=True)
    populate_ultimate_weapons_from_wiki(write=True)

    guardian_level = GuardianChipLevel.objects.get(level=1)
    assert guardian_level.parameters.count() == 3

    uw_level = UltimateWeaponLevel.objects.get(level=1)
    assert uw_level.parameters.count() == 3


@pytest.mark.django_db
def test_registry_keys_unique() -> None:
    """Registry entries are unique per (system, entity, parameter)."""

    triples = {(entry.system, entry.entity_slug, entry.parameter) for entry in PARAMETER_KEY_REGISTRY}
    assert len(triples) == len(PARAMETER_KEY_REGISTRY)


@pytest.mark.django_db
def test_bot_population_skips_unknown_headers() -> None:
    """Bots only persist parameters that match the registry."""

    raw_row = {"Bot": "Amplify", "Level": "1", "Damage": "10", "Unknown": "5"}
    scraped = ScrapedWikiRow(
        canonical_name="Amplify",
        entity_id="amplify",
        raw_row=raw_row,
        content_hash=compute_content_hash(raw_row),
    )
    ingest_wiki_rows(
        [scraped],
        page_url="https://example.test/wiki/Bots",
        source_section="bots",
        parse_version="bots_v1",
        write=True,
    )

    populate_bots_from_wiki(write=True)

    level = BotLevel.objects.get(level=1)
    assert level.parameters.count() == 1
    param = level.parameters.get()
    assert param.key == "Damage"
