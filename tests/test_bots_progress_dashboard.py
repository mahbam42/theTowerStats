"""Regression tests for the Bots Progress dashboard."""

from __future__ import annotations

from uuid import uuid4

import pytest
from django.urls import reverse

from analysis.event_windows import current_event_window, shift_event_window
from definitions.models import (
    BotDefinition,
    BotParameterDefinition,
    BotParameterLevel,
    Currency,
    ParameterKey,
    WikiData,
)
from player_state.models import GoalTarget, GoalType, PlayerBot, PlayerBotParameter, PlayerBotRespecWindow

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_bots_progress_includes_respec_callout(auth_client, player) -> None:
    """Bots dashboard shows the bot respec affordance."""

    response = auth_client.get(reverse("core:bots_progress"))
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Bot Respec" in content
    assert "Bot Respec (300 Gems)" in content
    assert "Available now." in content
    assert "This resets all bots to locked" in content
    assert response.context["bot_respec"]["available"] is True


@pytest.mark.django_db
@pytest.mark.regression
def test_bots_progress_marks_respec_used_for_current_event(auth_client, player) -> None:
    """Marking Bot Respec used locks the current Event window."""

    url = reverse("core:bots_progress")
    response = auth_client.post(url, data={"action": "mark_bot_respec_used"}, follow=True)
    assert response.status_code == 200

    window = current_event_window()
    assert PlayerBotRespecWindow.objects.filter(
        player=player,
        window_start=window.start,
        window_end=window.end,
    ).exists()

    content = response.content.decode("utf-8")
    assert "Already marked as used for this event window." in content
    assert 'disabled aria-disabled="true"' in content


@pytest.mark.django_db
@pytest.mark.regression
def test_bots_progress_respec_resets_bots_and_clears_bot_goals(auth_client, player) -> None:
    """Bot Respec resets bot levels, locks bots, and removes bot goals."""

    bot_def = _bot_with_four_parameters(slug="respec_bot", name="Respec Bot")
    bot = PlayerBot.objects.create(
        player=player,
        bot_definition=bot_def,
        bot_slug=bot_def.slug,
        unlocked=True,
    )
    param_defs = list(bot_def.parameter_definitions.order_by("id"))
    assert len(param_defs) == 4
    for index, param_def in enumerate(param_defs, start=1):
        PlayerBotParameter.objects.create(
            player=player,
            player_bot=bot,
            parameter_definition=param_def,
            level=min(index, 2),
        )

    GoalTarget.objects.create(
        player=player,
        goal_type=str(GoalType.BOT),
        goal_key=f"bot:{bot_def.slug}:{param_defs[0].key}",
        target_level=2,
    )

    response = auth_client.post(
        reverse("core:bots_progress"),
        data={"action": "mark_bot_respec_used"},
        follow=True,
    )
    assert response.status_code == 200

    bot.refresh_from_db()
    assert bot.unlocked is False
    assert not GoalTarget.objects.filter(player=player, goal_type=str(GoalType.BOT)).exists()
    assert all(
        level == 0
        for level in PlayerBotParameter.objects.filter(player=player, player_bot=bot).values_list("level", flat=True)
    )

    content = response.content.decode("utf-8")
    assert "Locked 1 bots, reset 4 bot parameter rows, and cleared 1 bot goals." in content


@pytest.mark.django_db
@pytest.mark.regression
def test_bots_progress_respec_lock_resets_on_new_event_window(auth_client, player) -> None:
    """A prior Event window usage record does not lock the current Event window."""

    previous_window = shift_event_window(current_event_window(), shift=-1)
    PlayerBotRespecWindow.objects.create(
        player=player,
        window_start=previous_window.start,
        window_end=previous_window.end,
    )

    response = auth_client.get(reverse("core:bots_progress"))
    assert response.status_code == 200

    content = response.content.decode("utf-8")
    assert "Available now." in content
    assert 'disabled aria-disabled="true"' not in content


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
    """Unlocking a bot creates 4 parameter rows at level 0."""

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
    assert all(p.level == 0 for p in params)

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
def test_bots_dashboard_renders_wiki_link_when_available(auth_client, player) -> None:
    """Bot tiles include an external wiki link when available."""

    bot_def = _bot_with_four_parameters(slug="golden_bot", name="Golden Bot")
    bot_def.wiki_page_url = "https://example.test/wiki/Golden_Bot"
    bot_def.save(update_fields=["wiki_page_url"])
    PlayerBot.objects.create(
        player=player,
        bot_definition=bot_def,
        bot_slug=bot_def.slug,
        unlocked=True,
    )

    url = reverse("core:bots_progress")
    response = auth_client.get(url)
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert 'href="https://example.test/wiki/Golden_Bot"' in content


@pytest.mark.django_db
def test_bots_dashboard_mutes_runs_used_for_amplify_bot(auth_client, player) -> None:
    """Amplify Bot uses a muted runs-used indicator."""

    bot_def = _bot_with_four_parameters(slug="amplify_bot", name="Amplify Bot")
    PlayerBot.objects.create(
        player=player,
        bot_definition=bot_def,
        bot_slug=bot_def.slug,
        unlocked=False,
    )

    response = auth_client.get(reverse("core:bots_progress"))
    assert response.status_code == 200

    tiles = response.context["bots"]
    tile = next(entry for entry in tiles if entry["slug"] == bot_def.slug)
    assert tile["summary"]["headline_muted"] is True
    assert tile["summary"]["headline_value"] == "—"
    assert tile["summary"]["headline_tooltip"] == "Runs Used cannot be tracked yet for Amplify Bot."


@pytest.mark.django_db
def test_bot_level_down_decrements_until_min(auth_client, player) -> None:
    """Level-down decrements by 1 and stops at level 0."""

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
    assert player_param.level == 0


@pytest.mark.django_db
@pytest.mark.regression
def test_bot_progress_totals_use_level_zero_baseline(auth_client, player) -> None:
    """Total medals invested include costs up to the current level."""

    bot_def = _bot_with_four_parameters(slug="thunder_bot", name="Thunder Bot")
    bot = PlayerBot.objects.create(
        player=player,
        bot_definition=bot_def,
        bot_slug=bot_def.slug,
        unlocked=True,
    )
    param_def = bot_def.parameter_definitions.order_by("id").first()
    assert param_def is not None
    PlayerBotParameter.objects.create(
        player=player,
        player_bot=bot,
        parameter_definition=param_def,
        level=2,
    )

    url = reverse("core:bots_progress")
    response = auth_client.get(url)
    assert response.status_code == 200

    tiles = response.context["bots"]
    tile = next(entry for entry in tiles if entry["slug"] == bot_def.slug)
    param_levels = {param["name"]: param["level"] for param in tile["parameters"]}
    assert param_levels["Damage"] == 2
    assert param_levels["Range"] == 0
    assert param_levels["Duration"] == 0
    assert param_levels["Cooldown"] == 0
    assert tile["summary"]["total_invested"] == 11


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


@pytest.mark.django_db
def test_bot_progress_rejects_external_next_redirect(auth_client, player) -> None:
    """Bot progress redirects ignore external next targets."""

    bot_def = _bot_with_four_parameters(slug="redirect_bot", name="Redirect Bot")
    bot = PlayerBot.objects.create(
        player=player,
        bot_definition=bot_def,
        bot_slug=bot_def.slug,
        unlocked=False,
    )

    url = reverse("core:bots_progress")
    response = auth_client.post(
        url,
        data={
            "action": "unlock_bot",
            "entity_id": bot.id,
            "next": "https://example.invalid/evil",
        },
    )

    assert response.status_code == 302
    assert response["Location"] == url


@pytest.mark.django_db
def test_bot_unlock_ajax_hides_parameter_validation_errors(auth_client, player, settings) -> None:
    """AJAX unlock hides internal parameter validation errors."""

    settings.DEBUG = False
    wiki = _wiki(suffix="bad_unlock")
    bot_def = BotDefinition.objects.create(name="Bad Bot", slug="bad_unlock_bot", source_wikidata=wiki)
    bot = PlayerBot.objects.create(
        player=player,
        bot_definition=bot_def,
        bot_slug=bot_def.slug,
        unlocked=False,
    )

    url = reverse("core:bots_progress")
    response = auth_client.post(
        url,
        data={"action": "unlock_bot", "entity_id": bot.id},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"] == "Invalid parameter definitions."
