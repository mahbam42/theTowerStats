"""Regression tests for the Ultimate Weapons Progress dashboard."""

from __future__ import annotations

import json
from uuid import uuid4

import pytest
from django.urls import reverse

from core.services import ingest_battle_report
from definitions.models import (
    BotDefinition,
    BotParameterDefinition,
    Currency,
    ParameterKey,
    UltimateWeaponDefinition,
    UltimateWeaponParameterDefinition,
    UltimateWeaponParameterLevel,
    Unit,
    WikiData,
)
from player_state.models import (
    PlayerBot,
    PlayerBotParameter,
    PlayerUltimateWeapon,
    PlayerUltimateWeaponParameter,
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


def _uw_with_three_parameters(*, slug: str, name: str) -> UltimateWeaponDefinition:
    """Create a UW definition with three parameter definitions and levels."""

    wiki = _wiki(suffix=slug)
    uw = UltimateWeaponDefinition.objects.create(name=name, slug=slug, source_wikidata=wiki)
    params = (
        (ParameterKey.DAMAGE, "Damage"),
        (ParameterKey.QUANTITY, "Quantity"),
        (ParameterKey.COOLDOWN, "Cooldown"),
    )
    for key, display in params:
        param_def = UltimateWeaponParameterDefinition.objects.create(
            ultimate_weapon_definition=uw,
            key=key,
            display_name=display,
        )
        UltimateWeaponParameterLevel.objects.create(
            parameter_definition=param_def,
            level=1,
            value_raw="10",
            cost_raw="5",
            currency=Currency.STONES,
            source_wikidata=wiki,
        )
        UltimateWeaponParameterLevel.objects.create(
            parameter_definition=param_def,
            level=2,
            value_raw="12",
            cost_raw="6",
            currency=Currency.STONES,
            source_wikidata=wiki,
        )
    return uw


def _create_sync_ready_uws(*, player, include_golden_bot: bool = True) -> None:
    """Create Ultimate Weapon and Bot parameters required for the sync chart."""

    for slug, name in (("golden_tower", "Golden Tower"), ("black_hole", "Black Hole"), ("death_wave", "Death Wave")):
        uw_def = UltimateWeaponDefinition.objects.create(name=name, slug=slug)
        cooldown = UltimateWeaponParameterDefinition.objects.create(
            ultimate_weapon_definition=uw_def,
            key=ParameterKey.COOLDOWN.value,
            display_name="Cooldown",
            unit_kind=Unit.Kind.SECONDS,
        )
        duration = UltimateWeaponParameterDefinition.objects.create(
            ultimate_weapon_definition=uw_def,
            key=ParameterKey.DURATION.value,
            display_name="Duration",
            unit_kind=Unit.Kind.SECONDS,
        )
        player_uw = PlayerUltimateWeapon.objects.create(
            player=player,
            ultimate_weapon_definition=uw_def,
            ultimate_weapon_slug=slug,
            unlocked=True,
        )
        PlayerUltimateWeaponParameter.objects.create(
            player=player,
            player_ultimate_weapon=player_uw,
            parameter_definition=cooldown,
            level=1,
            effective_value_raw="120",
        )
        PlayerUltimateWeaponParameter.objects.create(
            player=player,
            player_ultimate_weapon=player_uw,
            parameter_definition=duration,
            level=1,
            effective_value_raw="20",
        )

    if not include_golden_bot:
        return

    bot_def = BotDefinition.objects.create(name="Golden Bot", slug="golden_bot")
    cooldown = BotParameterDefinition.objects.create(
        bot_definition=bot_def,
        key=ParameterKey.COOLDOWN.value,
        display_name="Cooldown",
        unit_kind=Unit.Kind.SECONDS,
    )
    duration = BotParameterDefinition.objects.create(
        bot_definition=bot_def,
        key=ParameterKey.DURATION.value,
        display_name="Duration",
        unit_kind=Unit.Kind.SECONDS,
    )
    player_bot = PlayerBot.objects.create(
        player=player,
        bot_definition=bot_def,
        bot_slug="golden_bot",
        unlocked=True,
    )
    PlayerBotParameter.objects.create(
        player=player,
        player_bot=player_bot,
        parameter_definition=cooldown,
        level=1,
        effective_value_raw="90",
    )
    PlayerBotParameter.objects.create(
        player=player,
        player_bot=player_bot,
        parameter_definition=duration,
        level=1,
        effective_value_raw="15",
    )


@pytest.mark.django_db
def test_uw_unlock_creates_three_parameter_rows(auth_client, player) -> None:
    """Unlocking a UW creates 3 parameter rows at the minimum level."""

    uw = _uw_with_three_parameters(slug="golden_tower", name="Golden Tower")
    player_uw = PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=uw,
        ultimate_weapon_slug=uw.slug,
        unlocked=False,
    )

    url = reverse("core:ultimate_weapon_progress")
    response = auth_client.post(url, data={"action": "unlock_uw", "uw_id": player_uw.id})
    assert response.status_code == 302

    player_uw.refresh_from_db()
    assert player_uw.unlocked is True
    params = list(
        PlayerUltimateWeaponParameter.objects.filter(player_ultimate_weapon=player_uw).order_by("id")
    )
    assert len(params) == 3
    assert all(p.level == 1 for p in params)


@pytest.mark.django_db
def test_uw_level_up_increments_until_max(auth_client, player) -> None:
    """Level-up increments by 1 and stops at max level."""

    uw = _uw_with_three_parameters(slug="black_hole", name="Black Hole")
    player_uw = PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=uw,
        ultimate_weapon_slug=uw.slug,
        unlocked=True,
    )
    param_def = uw.parameter_definitions.order_by("id").first()
    assert param_def is not None
    player_param = PlayerUltimateWeaponParameter.objects.create(
        player=player,
        player_ultimate_weapon=player_uw,
        parameter_definition=param_def,
        level=1,
    )

    url = reverse("core:ultimate_weapon_progress")
    response = auth_client.post(url, data={"action": "level_up_uw_param", "param_id": player_param.id})
    assert response.status_code == 302
    player_param.refresh_from_db()
    assert player_param.level == 2

    response = auth_client.post(url, data={"action": "level_up_uw_param", "param_id": player_param.id})
    assert response.status_code == 302
    player_param.refresh_from_db()
    assert player_param.level == 2


@pytest.mark.django_db
def test_uw_level_down_decrements_until_min(auth_client, player) -> None:
    """Level-down decrements by 1 and stops at the minimum level."""

    uw = _uw_with_three_parameters(slug="inner_mines", name="Inner Mines")
    player_uw = PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=uw,
        ultimate_weapon_slug=uw.slug,
        unlocked=True,
    )
    param_def = uw.parameter_definitions.order_by("id").first()
    assert param_def is not None
    player_param = PlayerUltimateWeaponParameter.objects.create(
        player=player,
        player_ultimate_weapon=player_uw,
        parameter_definition=param_def,
        level=2,
    )

    url = reverse("core:ultimate_weapon_progress")
    response = auth_client.post(url, data={"action": "level_down_uw_param", "param_id": player_param.id})
    assert response.status_code == 302
    player_param.refresh_from_db()
    assert player_param.level == 1

    response = auth_client.post(url, data={"action": "level_down_uw_param", "param_id": player_param.id})
    assert response.status_code == 302
    player_param.refresh_from_db()
    assert player_param.level == 1


@pytest.mark.django_db
def test_uw_dashboard_sorts_unlocked_first(auth_client, player) -> None:
    """Unlocked UWs render before locked UWs by default."""

    uw1 = _uw_with_three_parameters(slug="spotlight", name="Spotlight")
    uw2 = _uw_with_three_parameters(slug="death_wave", name="Death Wave")
    PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=uw1,
        ultimate_weapon_slug=uw1.slug,
        unlocked=False,
    )
    PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=uw2,
        ultimate_weapon_slug=uw2.slug,
        unlocked=True,
    )

    url = reverse("core:ultimate_weapon_progress")
    response = auth_client.get(url)
    assert response.status_code == 200
    tiles = response.context["ultimate_weapons"]
    assert tiles[0]["unlocked"] is True


@pytest.mark.django_db
def test_uw_dashboard_omits_invalid_uw_in_production(auth_client, player, settings) -> None:
    """Production mode omits UWs that do not have exactly 3 parameters."""

    settings.DEBUG = False
    wiki = _wiki()
    bad = UltimateWeaponDefinition.objects.create(name="Bad UW", slug="bad_uw", source_wikidata=wiki)
    param_def = UltimateWeaponParameterDefinition.objects.create(
        ultimate_weapon_definition=bad,
        key=ParameterKey.DAMAGE,
        display_name="Damage",
    )
    UltimateWeaponParameterLevel.objects.create(
        parameter_definition=param_def,
        level=1,
        value_raw="10",
        cost_raw="5",
        currency=Currency.STONES,
        source_wikidata=wiki,
    )

    PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=bad,
        ultimate_weapon_slug=bad.slug,
        unlocked=True,
    )

    url = reverse("core:ultimate_weapon_progress")
    response = auth_client.get(url)
    assert response.status_code == 200
    assert all(tile["slug"] != "bad_uw" for tile in response.context["ultimate_weapons"])


@pytest.mark.django_db
def test_uw_sync_toggles_hide_rows_and_persist(auth_client, player) -> None:
    """Sync toggle state is preserved in the response and filters chart labels."""

    _create_sync_ready_uws(player=player, include_golden_bot=True)

    response = auth_client.get(
        reverse("core:ultimate_weapon_progress"),
        {"show_death_wave": "0", "show_golden_bot": "0"},
    )
    assert response.status_code == 200

    summary = response.context["uw_sync_summary"]
    assert summary["show_death_wave"] is False
    assert summary["show_golden_bot"] is False

    chart_data = json.loads(response.context["uw_sync_chart_json"])
    labels = chart_data["labels"]
    assert "Death Wave" not in labels
    assert "Golden Bot" not in labels


@pytest.mark.django_db
def test_uw_dashboard_omits_unknown_parameter_keys_in_production(auth_client, player, settings) -> None:
    """Production mode omits UWs whose parameters are not in the ParameterKey registry."""

    settings.DEBUG = False
    wiki = _wiki()
    uw = UltimateWeaponDefinition.objects.create(name="Weird UW", slug="weird_uw", source_wikidata=wiki)
    params = (
        (ParameterKey.DAMAGE, "Damage"),
        ("not_a_real_key", "Not a real key"),
        (ParameterKey.COOLDOWN, "Cooldown"),
    )
    for key, display in params:
        param_def = UltimateWeaponParameterDefinition.objects.create(
            ultimate_weapon_definition=uw,
            key=key,
            display_name=display,
        )
        UltimateWeaponParameterLevel.objects.create(
            parameter_definition=param_def,
            level=1,
            value_raw="10",
            cost_raw="5",
            currency=Currency.STONES,
            source_wikidata=wiki,
        )

    PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=uw,
        ultimate_weapon_slug=uw.slug,
        unlocked=True,
    )

    url = reverse("core:ultimate_weapon_progress")
    response = auth_client.get(url)
    assert response.status_code == 200
    assert all(tile["slug"] != "weird_uw" for tile in response.context["ultimate_weapons"])


@pytest.mark.django_db
def test_uw_unlock_form_posts_to_page_path(auth_client, player) -> None:
    """Unlock form includes an explicit action attribute to avoid DOM shadowing issues."""

    uw = _uw_with_three_parameters(slug="chain_lightning", name="Chain Lightning")
    PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=uw,
        ultimate_weapon_slug=uw.slug,
        unlocked=False,
    )

    url = reverse("core:ultimate_weapon_progress")
    response = auth_client.get(url)
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert 'action="/ultimate-weapons/"' in content


@pytest.mark.django_db
def test_uw_dashboard_labels_observed_usage_for_locked_vs_unlocked(auth_client, player) -> None:
    """Locked UWs use a distinct observed-from-runs usage label."""

    uw_locked = _uw_with_three_parameters(slug="locked_uw", name="Locked UW")
    uw_unlocked = _uw_with_three_parameters(slug="unlocked_uw", name="Unlocked UW")
    PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=uw_locked,
        ultimate_weapon_slug=uw_locked.slug,
        unlocked=False,
    )
    PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=uw_unlocked,
        ultimate_weapon_slug=uw_unlocked.slug,
        unlocked=True,
    )

    url = reverse("core:ultimate_weapon_progress")
    response = auth_client.get(url)
    assert response.status_code == 200
    tiles = {tile["slug"]: tile for tile in response.context["ultimate_weapons"]}
    assert tiles["locked_uw"]["summary"]["headline_label"] == "Runs used while locked (observed)"
    assert tiles["unlocked_uw"]["summary"]["headline_label"] == "Runs used (observed)"


@pytest.mark.django_db
def test_uw_dashboard_runs_used_reflects_imported_battle_reports(auth_client, player) -> None:
    """Runs used counts Battle Reports that include the Ultimate Weapon."""

    uw = _uw_with_three_parameters(slug="chain_lightning", name="Chain Lightning")
    PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=uw,
        ultimate_weapon_slug=uw.slug,
        unlocked=True,
    )

    ingest_battle_report(
        "\n".join(
            [
                "Battle Report",
                "Chain Lightning Damage\t1",
                "Battle Date: 2025-12-01 13:45:00",
                "Tier: 6",
            ]
        ),
        player=player,
    )

    url = reverse("core:ultimate_weapon_progress")
    response = auth_client.get(url)
    assert response.status_code == 200
    tiles = {tile["slug"]: tile for tile in response.context["ultimate_weapons"]}
    assert tiles["chain_lightning"]["summary"]["headline_value"] == 1


@pytest.mark.django_db
def test_uw_dashboard_renders_wiki_link_when_available(auth_client, player) -> None:
    """Ultimate Weapon tiles include an external wiki link when available."""

    uw = _uw_with_three_parameters(slug="black_hole", name="Black Hole")
    uw.wiki_page_url = "https://example.test/wiki/Black_Hole"
    uw.save(update_fields=["wiki_page_url"])
    PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=uw,
        ultimate_weapon_slug=uw.slug,
        unlocked=True,
    )

    url = reverse("core:ultimate_weapon_progress")
    response = auth_client.get(url)
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert 'href="https://example.test/wiki/Black_Hole"' in content
