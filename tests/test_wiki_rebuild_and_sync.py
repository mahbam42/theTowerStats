"""Tests for rebuild + sync utilities (WikiData -> Definitions -> Player State)."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.wiki_ingestion import ingest_wiki_rows, make_entity_id, scrape_leveled_entity_rows
from definitions.models import BotDefinition, BotParameterDefinition, BotParameterLevel
from definitions.wiki_rebuild import rebuild_bots_from_wikidata
from player_state.models import PlayerBot, PlayerBotParameter
from player_state.sync import sync_player_state_from_definitions


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _read_fixture(name: str) -> str:
    """Read a fixture file from tests/fixtures."""

    return (FIXTURES_DIR / name).read_text(encoding="utf-8", errors="ignore")


@pytest.mark.django_db
def test_rebuild_bots_is_repeatable_for_same_wikidata() -> None:
    """Rebuilding bot tables twice yields stable counts (no duplicates)."""

    html = _read_fixture("wiki_bot_amplify_bot_v1.html")
    name = "Amplify Bot"
    entity_id = make_entity_id(name)
    scraped = scrape_leveled_entity_rows(
        html,
        table_index=0,
        entity_name=name,
        entity_id=entity_id,
        entity_field="Bot",
    )
    ingest_wiki_rows(
        scraped,
        page_url="https://example.test/wiki/Amplify_Bot",
        source_section="bots_amplify_bot_table_0",
        parse_version="bots_v1",
        write=True,
    )

    rebuild_bots_from_wikidata(write=True)
    first_defs = BotDefinition.objects.count()
    first_param_defs = BotParameterDefinition.objects.count()
    first_param_levels = BotParameterLevel.objects.count()

    rebuild_bots_from_wikidata(write=True)
    assert BotDefinition.objects.count() == first_defs
    assert BotParameterDefinition.objects.count() == first_param_defs
    assert BotParameterLevel.objects.count() == first_param_levels


@pytest.mark.django_db
def test_sync_player_state_is_idempotent(player) -> None:
    """sync_player_state_from_definitions can be run repeatedly."""

    BotDefinition.objects.create(name="Amplify Bot", slug="amplify_bot")

    sync_player_state_from_definitions(player=player, write=True)
    assert PlayerBot.objects.filter(player=player, bot_slug="amplify_bot").exists()

    summary2 = sync_player_state_from_definitions(player=player, write=True)
    assert summary2.created_player_rows == 0
    assert summary2.created_parameter_rows == 0

    bot = PlayerBot.objects.get(player=player, bot_slug="amplify_bot")
    assert PlayerBotParameter.objects.filter(player_bot=bot).count() == 0
