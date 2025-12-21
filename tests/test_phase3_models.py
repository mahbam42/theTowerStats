"""Model smoke tests for structural completeness after Prompt12 refactor."""

from __future__ import annotations

import pytest

from definitions.models import (
    BotDefinition,
    BotParameterDefinition,
    BotParameterLevel,
    CardDefinition,
    Currency,
    GuardianChipDefinition,
    GuardianChipParameterDefinition,
    GuardianChipParameterLevel,
    ParameterKey,
    UltimateWeaponDefinition,
    UltimateWeaponParameterDefinition,
    UltimateWeaponParameterLevel,
    Unit,
    WikiData,
)
from gamedata.models import BattleReport, BattleReportProgress, RunBot
from player_state.models import PlayerBot, PlayerBotParameter, PlayerCard, Preset

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_models_create_minimal_rows(player) -> None:
    """Create minimal rows to ensure migrations apply cleanly."""

    wiki = WikiData.objects.create(
        page_url="https://example.test/wiki",
        canonical_name="Example",
        entity_id="example",
        content_hash="x" * 64,
        raw_row={"Name": "Example"},
        source_section="test",
        parse_version="test_v1",
    )
    Unit.objects.create(name="seconds", symbol="s", kind=Unit.Kind.SECONDS)

    card = CardDefinition.objects.create(name="Coin Bonus", slug="coin_bonus", source_wikidata=wiki)

    bot = BotDefinition.objects.create(name="Amplify Bot", slug="amplify_bot", source_wikidata=wiki)
    bot_param = BotParameterDefinition.objects.create(
        bot_definition=bot, key=ParameterKey.COOLDOWN, display_name="Cooldown", unit_kind=Unit.Kind.SECONDS
    )
    BotParameterLevel.objects.create(
        parameter_definition=bot_param,
        level=1,
        value_raw="100",
        cost_raw="10",
        currency=Currency.MEDALS,
        source_wikidata=wiki,
    )

    uw = UltimateWeaponDefinition.objects.create(name="Golden Tower", slug="golden_tower", source_wikidata=wiki)
    uw_param = UltimateWeaponParameterDefinition.objects.create(
        ultimate_weapon_definition=uw,
        key=ParameterKey.COOLDOWN,
        display_name="Cooldown",
        unit_kind=Unit.Kind.SECONDS,
    )
    UltimateWeaponParameterLevel.objects.create(
        parameter_definition=uw_param,
        level=1,
        value_raw="100",
        cost_raw="5",
        currency=Currency.STONES,
        source_wikidata=wiki,
    )

    guardian = GuardianChipDefinition.objects.create(name="Ally", slug="ally", source_wikidata=wiki)
    guardian_param = GuardianChipParameterDefinition.objects.create(
        guardian_chip_definition=guardian,
        key=ParameterKey.COOLDOWN,
        display_name="Cooldown",
        unit_kind=Unit.Kind.SECONDS,
    )
    GuardianChipParameterLevel.objects.create(
        parameter_definition=guardian_param,
        level=1,
        value_raw="100",
        cost_raw="1",
        currency=Currency.BITS,
        source_wikidata=wiki,
    )

    preset = Preset.objects.create(player=player, name="Farming")
    PlayerCard.objects.create(player=player, card_definition=card, card_slug=card.slug, stars_unlocked=1)

    player_bot = PlayerBot.objects.create(
        player=player, bot_definition=bot, bot_slug=bot.slug, unlocked=True
    )
    PlayerBotParameter.objects.create(player=player, player_bot=player_bot, parameter_definition=bot_param, level=1)

    report = BattleReport.objects.create(player=player, raw_text="Battle Report\n", checksum="c" * 64)
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        tier=1,
        wave=10,
        real_time_seconds=60,
        preset=preset,
    )
    RunBot.objects.create(player=player, battle_report=report, bot_definition=bot, notes="")
