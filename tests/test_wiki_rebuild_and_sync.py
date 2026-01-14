"""Tests for rebuild + sync utilities (WikiData -> Definitions -> Player State)."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.wiki_ingestion import ingest_wiki_rows, make_entity_id, scrape_leveled_entity_rows
from definitions.models import BotDefinition, BotParameterDefinition, BotParameterLevel, ParameterKey
from definitions.wiki_rebuild import rebuild_bots_from_wikidata
from player_state.models import PlayerBot, PlayerBotParameter
from player_state.sync import sync_player_state_from_definitions

pytestmark = pytest.mark.integration


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
@pytest.mark.regression
@pytest.mark.parametrize(
    ("fixture_name", "bot_name", "expected"),
    [
        (
            "wiki_bot_thunder_bot_v1.html",
            "Thunder Bot",
            {
                ParameterKey.DURATION.value: "5.0s",
                ParameterKey.COOLDOWN.value: "120s",
                ParameterKey.LINGER.value: "20%",
                ParameterKey.RANGE.value: "28m",
            },
        ),
        (
            "wiki_bot_flame_bot_v1.html",
            "Flame Bot",
            {
                ParameterKey.DAMAGE_REDUCTION.value: "20%",
                ParameterKey.COOLDOWN.value: "75s",
                ParameterKey.DAMAGE.value: "x50",
                ParameterKey.RANGE.value: "30m",
            },
        ),
        (
            "wiki_bot_golden_bot_v1.html",
            "Golden Bot",
            {
                ParameterKey.DURATION.value: "20s",
                ParameterKey.COOLDOWN.value: "120s",
                ParameterKey.MULTIPLIER.value: "2.0x",
                ParameterKey.RANGE.value: "20m",
            },
        ),
        (
            "wiki_bot_amplify_bot_v1.html",
            "Amplify Bot",
            {
                ParameterKey.DURATION.value: "20s",
                ParameterKey.COOLDOWN.value: "120s",
                ParameterKey.MULTIPLIER.value: "3.50%",
                ParameterKey.RANGE.value: "25m",
            },
        ),
    ],
)
def test_rebuild_bots_injects_level_zero_defaults(
    fixture_name: str,
    bot_name: str,
    expected: dict[str, str],
) -> None:
    """Rebuilds inject configured level 0 values for bot parameters."""

    html = _read_fixture(fixture_name)
    entity_id = make_entity_id(bot_name)
    scraped = scrape_leveled_entity_rows(
        html,
        table_index=0,
        entity_name=bot_name,
        entity_id=entity_id,
        entity_field="Bot",
    )
    ingest_wiki_rows(
        scraped,
        page_url=f"https://example.test/wiki/{entity_id}",
        source_section=f"bots_{entity_id}_table_0",
        parse_version="bots_v1",
        write=True,
    )

    rebuild_bots_from_wikidata(write=True)
    bot_def = BotDefinition.objects.get(slug=entity_id)
    for key, value_raw in expected.items():
        param_def = BotParameterDefinition.objects.get(bot_definition=bot_def, key=key)
        level_zero = BotParameterLevel.objects.filter(parameter_definition=param_def, level=0).first()
        assert level_zero is not None
        assert level_zero.value_raw == value_raw
        assert level_zero.cost_raw == "0"


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
