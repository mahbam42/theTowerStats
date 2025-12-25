"""Integration tests for the Goals dashboard and widgets."""

from __future__ import annotations

from uuid import uuid4

import pytest
from django.urls import reverse

from core.goals import goal_key_for_parameter
from definitions.models import (
    BotDefinition,
    BotParameterDefinition,
    BotParameterLevel,
    Currency,
    GuardianChipDefinition,
    GuardianChipParameterDefinition,
    GuardianChipParameterLevel,
    ParameterKey,
    WikiData,
)
from player_state.models import (
    GoalTarget,
    GoalType,
    PlayerBot,
    PlayerBotParameter,
    PlayerGuardianChip,
    PlayerGuardianChipParameter,
)

pytestmark = pytest.mark.integration


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


def _bot_with_parameters(*, slug: str, name: str, count: int = 4) -> BotDefinition:
    """Create a bot definition with N parameter definitions and level rows."""

    wiki = _wiki(suffix=slug)
    bot = BotDefinition.objects.create(name=name, slug=slug, source_wikidata=wiki)
    params = (
        (ParameterKey.DAMAGE, "Damage"),
        (ParameterKey.RANGE, "Range"),
        (ParameterKey.DURATION, "Duration"),
        (ParameterKey.COOLDOWN, "Cooldown"),
    )
    for key, display in params[:count]:
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
            cost_raw="7",
            currency=Currency.MEDALS,
            source_wikidata=wiki,
        )
        BotParameterLevel.objects.create(
            parameter_definition=param_def,
            level=3,
            value_raw="14",
            cost_raw="9",
            currency=Currency.MEDALS,
            source_wikidata=wiki,
        )
    return bot


def _guardian_with_parameters(*, slug: str, name: str) -> GuardianChipDefinition:
    """Create a guardian chip definition with one parameter and level rows."""

    wiki = _wiki(suffix=slug)
    guardian = GuardianChipDefinition.objects.create(name=name, slug=slug, source_wikidata=wiki)
    param_def = GuardianChipParameterDefinition.objects.create(
        guardian_chip_definition=guardian,
        key=ParameterKey.COOLDOWN,
        display_name="Cooldown",
    )
    for level, cost in ((1, "5"), (2, "7"), (3, "9")):
        GuardianChipParameterLevel.objects.create(
            parameter_definition=param_def,
            level=level,
            value_raw=str(level),
            cost_raw=cost,
            currency=Currency.BITS,
            source_wikidata=wiki,
        )
    return guardian


@pytest.mark.django_db
def test_goals_dashboard_can_set_and_clear_goal(auth_client, player) -> None:
    """Players can create and clear a goal target from the Goals dashboard."""

    bot_def = _bot_with_parameters(slug="golden_bot", name="Golden Bot", count=1)
    param_def = bot_def.parameter_definitions.get()
    goal_key = goal_key_for_parameter(
        goal_type=str(GoalType.BOT),
        entity_slug=bot_def.slug,
        parameter_key=param_def.key,
    )

    url = reverse("core:goals_dashboard")
    response = auth_client.post(
        url,
        data={
            "action": "create_goal",
            "goal_type": str(GoalType.BOT),
            "goal_key": goal_key,
            "target_level": "3",
            "notes": "Test notes",
        },
    )
    assert response.status_code == 302
    assert GoalTarget.objects.filter(player=player, goal_type=str(GoalType.BOT), goal_key=goal_key).exists()

    response = auth_client.get(url, data={"goal_type": str(GoalType.BOT)})
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "21 medals" in content
    assert "Per-level breakdown" in content
    assert "L0 → L1" in content
    assert "L1 → L2" in content
    assert "L2 → L3" in content

    response = auth_client.post(
        url,
        data={"action": "clear_goal", "goal_type": str(GoalType.BOT), "goal_key": goal_key},
    )
    assert response.status_code == 302
    assert not GoalTarget.objects.filter(player=player, goal_type=str(GoalType.BOT), goal_key=goal_key).exists()


@pytest.mark.django_db
def test_goals_dashboard_hides_completed_by_default(auth_client, player) -> None:
    """Completed goals are hidden unless show_completed is enabled."""

    bot_def = _bot_with_parameters(slug="flame_bot", name="Flame Bot", count=1)
    param_def = bot_def.parameter_definitions.get()
    bot = PlayerBot.objects.create(
        player=player,
        bot_definition=bot_def,
        bot_slug=bot_def.slug,
        unlocked=True,
    )
    PlayerBotParameter.objects.create(
        player=player,
        player_bot=bot,
        parameter_definition=param_def,
        level=3,
    )

    goal_key = goal_key_for_parameter(
        goal_type=str(GoalType.BOT),
        entity_slug=bot_def.slug,
        parameter_key=param_def.key,
    )
    GoalTarget.objects.create(
        player=player,
        goal_type=str(GoalType.BOT),
        goal_key=goal_key,
        target_level=2,
        is_current_level_assumed=False,
    )

    url = reverse("core:goals_dashboard")
    response = auth_client.get(url, data={"goal_type": str(GoalType.BOT)})
    assert response.status_code == 200
    assert param_def.display_name not in response.content.decode("utf-8")

    response = auth_client.get(url, data={"goal_type": str(GoalType.BOT), "show_completed": "on"})
    assert response.status_code == 200
    assert param_def.display_name in response.content.decode("utf-8")


@pytest.mark.django_db
def test_bots_progress_includes_goals_widget(auth_client, player) -> None:
    """Bots dashboard shows a Goals widget when goals are set."""

    bot_def = _bot_with_parameters(slug="thunder_bot", name="Thunder Bot", count=4)
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
        level=1,
    )
    goal_key = goal_key_for_parameter(
        goal_type=str(GoalType.BOT),
        entity_slug=bot_def.slug,
        parameter_key=param_def.key,
    )
    GoalTarget.objects.create(
        player=player,
        goal_type=str(GoalType.BOT),
        goal_key=goal_key,
        target_level=3,
        is_current_level_assumed=False,
    )

    url = reverse("core:bots_progress")
    response = auth_client.get(url)
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Upgrade targets" in content
    assert f'href="{reverse("core:goals_dashboard")}?goal_type={str(GoalType.BOT)}"' in content


@pytest.mark.django_db
def test_bots_progress_hides_goals_widget_when_empty(auth_client, player) -> None:
    """Bots dashboard hides the goals widget when the player has no active goals."""

    bot_def = _bot_with_parameters(slug="no_goals_bot", name="No Goals Bot", count=4)
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
    assert "Upgrade targets" not in content


@pytest.mark.django_db
def test_goals_dashboard_shows_total_to_target_for_guardian(auth_client, player) -> None:
    """Goals dashboard shows both remaining and total-to-target values."""

    guardian = _guardian_with_parameters(slug="summon", name="Summon")
    param_def = guardian.parameter_definitions.get()
    chip = PlayerGuardianChip.objects.create(
        player=player,
        guardian_chip_definition=guardian,
        guardian_chip_slug=guardian.slug,
        unlocked=True,
        active=False,
    )
    PlayerGuardianChipParameter.objects.create(
        player=player,
        player_guardian_chip=chip,
        parameter_definition=param_def,
        level=2,
    )

    goal_key = goal_key_for_parameter(
        goal_type=str(GoalType.GUARDIAN_CHIP),
        entity_slug=guardian.slug,
        parameter_key=param_def.key,
    )
    GoalTarget.objects.create(
        player=player,
        goal_type=str(GoalType.GUARDIAN_CHIP),
        goal_key=goal_key,
        target_level=3,
        is_current_level_assumed=False,
    )

    url = reverse("core:goals_dashboard")
    response = auth_client.get(url, data={"goal_type": str(GoalType.GUARDIAN_CHIP)})
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "9 bits" in content
    assert "21 bits" in content

