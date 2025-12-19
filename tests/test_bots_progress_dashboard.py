"""Regression tests for the Bots Progress dashboard."""

from __future__ import annotations

from uuid import uuid4

import pytest
from django.urls import reverse

from definitions.models import (
    BotDefinition,
    BotParameterDefinition,
    BotParameterLevel,
    Currency,
    ParameterKey,
    WikiData,
)
from player_state.models import PlayerBot, PlayerBotParameter


def _wiki(*, suffix: str | None = None) -> WikiData:
    """Create a minimal WikiData revision row."""

    if suffix is None:
        suffix = uuid4().hex
    return WikiData.objects.create(
        page_url=f"https://example.test/wiki/{suffix}",
        canonical_name=f"Example {suffix}",
        entity_id=f"example_{suffix}",
        content_hash=(suffix * 64)[:64],
        raw_row={"Name": "Example"},
        source_section="test",
        parse_version=f"test_v1_{suffix}",
    )


def _bot_with_four_parameters(*, slug: str, name: str) -> BotDefinition:
    """Create a bot definition with four parameter definitions and levels."""

    wiki = _wiki(suffix=slug)
    bot = BotDefinition.objects.create(name=name, slug=slug, source_wikidata=wiki)
    params = (
        (ParameterKey.DAMAGE, "Damage"),
        (ParameterKey.RANGE, "Range"),
        (ParameterKey.DURATION, "Duration"),
        (ParameterKey.COOLDOWN, "Cooldown"),
    )
    for key, display in params:
        param_def = BotParameterDefinition.objects.create(
            bot_definition=bot,
            key=key,
            display_name=display,
        )
        BotParameterLevel.objects.create(
            parameter_definition=param_def,
            level=1,
            value_raw="10",
            cost_raw="5",
            currency=Currency.MEDALS,
            source_wikidata=wiki,
        )
        BotParameterLevel.objects.create(
            parameter_definition=param_def,
            level=2,
            value_raw="12",
            cost_raw="6",
            currency=Currency.MEDALS,
            source_wikidata=wiki,
        )
    return bot


@pytest.mark.django_db
def test_bot_unlock_creates_four_parameter_rows(auth_client, player) -> None:
    """Unlocking a bot creates 4 parameter rows at the minimum level."""

    bot_def = _bot_with_four_parameters(slug="golden_bot", name="Golden Bot")
    bot = PlayerBot.objects.create(
        player=player,
        bot_definition=bot_def,
        bot_slug=bot_def.slug,
        unlocked=False,
    )

    url = reverse("core:bots_progress")
    response = auth_client.post(url, data={"action": "unlock_bot", "entity_id": bot.id})
    assert response.status_code == 302

    bot.refresh_from_db()
    assert bot.unlocked is True
    params = list(PlayerBotParameter.objects.filter(player_bot=bot).order_by("id"))
    assert len(params) == 4
    assert all(p.level == 1 for p in params)

    response = auth_client.get(url)
    assert response.status_code == 200
    tiles = response.context["bots"]
    tile = next(entry for entry in tiles if entry["slug"] == bot_def.slug)
    assert tile["summary"]["total_invested"] == 0


@pytest.mark.django_db
def test_bot_level_up_increments_until_max(auth_client, player) -> None:
    """Level-up increments by 1 and stops at max level."""

    bot_def = _bot_with_four_parameters(slug="flame_bot", name="Flame Bot")
    bot = PlayerBot.objects.create(
        player=player,
        bot_definition=bot_def,
        bot_slug=bot_def.slug,
        unlocked=True,
    )
    param_def = bot_def.parameter_definitions.order_by("id").first()
    assert param_def is not None
    player_param = PlayerBotParameter.objects.create(
        player=player,
        player_bot=bot,
        parameter_definition=param_def,
        level=1,
    )

    url = reverse("core:bots_progress")
    response = auth_client.post(url, data={"action": "level_up_bot_param", "param_id": player_param.id})
    assert response.status_code == 302
    player_param.refresh_from_db()
    assert player_param.level == 2

    response = auth_client.post(url, data={"action": "level_up_bot_param", "param_id": player_param.id})
    assert response.status_code == 302
    player_param.refresh_from_db()
    assert player_param.level == 2


@pytest.mark.django_db
def test_bot_level_down_decrements_until_min(auth_client, player) -> None:
    """Level-down decrements by 1 and stops at the minimum level."""

    bot_def = _bot_with_four_parameters(slug="freeze_bot", name="Freeze Bot")
    bot = PlayerBot.objects.create(
        player=player,
        bot_definition=bot_def,
        bot_slug=bot_def.slug,
        unlocked=True,
    )
    param_def = bot_def.parameter_definitions.order_by("id").first()
    assert param_def is not None
    player_param = PlayerBotParameter.objects.create(
        player=player,
        player_bot=bot,
        parameter_definition=param_def,
        level=2,
    )

    url = reverse("core:bots_progress")
    response = auth_client.post(url, data={"action": "level_down_bot_param", "param_id": player_param.id})
    assert response.status_code == 302
    player_param.refresh_from_db()
    assert player_param.level == 1

    response = auth_client.post(url, data={"action": "level_down_bot_param", "param_id": player_param.id})
    assert response.status_code == 302
    player_param.refresh_from_db()
    assert player_param.level == 1


@pytest.mark.django_db
def test_bot_dashboard_omits_invalid_bot_in_production(auth_client, player, settings) -> None:
    """Production mode omits bots that do not have exactly 4 parameters."""

    settings.DEBUG = False
    wiki = _wiki()
    bad = BotDefinition.objects.create(name="Bad Bot", slug="bad_bot", source_wikidata=wiki)
    param_def = BotParameterDefinition.objects.create(
        bot_definition=bad,
        key=ParameterKey.DAMAGE,
        display_name="Damage",
    )
    BotParameterLevel.objects.create(
        parameter_definition=param_def,
        level=1,
        value_raw="10",
        cost_raw="5",
        currency=Currency.MEDALS,
        source_wikidata=wiki,
    )

    PlayerBot.objects.create(
        player=player,
        bot_definition=bad,
        bot_slug=bad.slug,
        unlocked=True,
    )

    url = reverse("core:bots_progress")
    response = auth_client.get(url)
    assert response.status_code == 200
    assert all(tile["slug"] != "bad_bot" for tile in response.context["bots"])


@pytest.mark.django_db
def test_bot_dashboard_deletes_orphaned_parameter_rows(auth_client, player) -> None:
    """Orphaned parameter rows are deleted so the page can render in debug mode."""

    bot_def = _bot_with_four_parameters(slug="thunder_bot", name="Thunder Bot")
    bot = PlayerBot.objects.create(
        player=player,
        bot_definition=bot_def,
        bot_slug=bot_def.slug,
        unlocked=True,
    )
    param_def = bot_def.parameter_definitions.order_by("id").first()
    assert param_def is not None
    orphan = PlayerBotParameter.objects.create(
        player=player,
        player_bot=bot,
        parameter_definition=param_def,
        level=1,
    )
    param_def.delete()
    orphan.refresh_from_db()
    assert orphan.parameter_definition is None

    url = reverse("core:bots_progress")
    response = auth_client.get(url)
    assert response.status_code == 200
    assert PlayerBotParameter.objects.filter(player_bot=bot).count() == 0
