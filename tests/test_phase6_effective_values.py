"""Golden/regression tests for Phase 6 base vs effective value rendering."""

from __future__ import annotations

from uuid import uuid4

import pytest
from django.urls import reverse

from definitions.models import (
    CardDefinition,
    Currency,
    ParameterKey,
    UltimateWeaponDefinition,
    UltimateWeaponParameterDefinition,
    UltimateWeaponParameterLevel,
    WikiData,
)
from player_state.models import PlayerCard, PlayerUltimateWeapon, PlayerUltimateWeaponParameter


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


def _uw_with_cooldown_param(*, slug: str, name: str) -> UltimateWeaponDefinition:
    """Create a UW definition containing a cooldown parameter with 2 levels."""

    wiki = _wiki(suffix=slug)
    uw = UltimateWeaponDefinition.objects.create(name=name, slug=slug, source_wikidata=wiki)
    param_def = UltimateWeaponParameterDefinition.objects.create(
        ultimate_weapon_definition=uw,
        key=ParameterKey.COOLDOWN,
        display_name="Cooldown",
    )
    UltimateWeaponParameterLevel.objects.create(
        parameter_definition=param_def,
        level=1,
        value_raw="10s",
        cost_raw="5",
        currency=Currency.STONES,
        source_wikidata=wiki,
    )
    UltimateWeaponParameterLevel.objects.create(
        parameter_definition=param_def,
        level=2,
        value_raw="9s",
        cost_raw="6",
        currency=Currency.STONES,
        source_wikidata=wiki,
    )
    # Add two more parameters to satisfy the dashboard invariant.
    for key, display in [(ParameterKey.DAMAGE, "Damage"), (ParameterKey.DURATION, "Duration")]:
        other_def = UltimateWeaponParameterDefinition.objects.create(
            ultimate_weapon_definition=uw,
            key=key,
            display_name=display,
        )
        UltimateWeaponParameterLevel.objects.create(
            parameter_definition=other_def,
            level=1,
            value_raw="10",
            cost_raw="5",
            currency=Currency.STONES,
            source_wikidata=wiki,
        )
        UltimateWeaponParameterLevel.objects.create(
            parameter_definition=other_def,
            level=2,
            value_raw="12",
            cost_raw="6",
            currency=Currency.STONES,
            source_wikidata=wiki,
        )
    return uw


@pytest.mark.django_db
def test_effective_value_schema_and_breakdown_when_present(auth_client, player) -> None:
    """Base and effective values are shown; breakdown renders only when present."""

    uw = _uw_with_cooldown_param(slug="gt", name="Golden Tower")
    player_uw = PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=uw,
        ultimate_weapon_slug=uw.slug,
        unlocked=True,
    )

    cooldown_def = uw.parameter_definitions.get(key=ParameterKey.COOLDOWN)
    param = PlayerUltimateWeaponParameter.objects.create(
        player=player,
        player_ultimate_weapon=player_uw,
        parameter_definition=cooldown_def,
        level=1,
        effective_value_raw="8s",
        effective_notes="−2s from a temporary modifier",
    )
    assert param.level == 1

    card_def = CardDefinition.objects.create(
        name="Cooldown Booster",
        slug="cooldown_booster",
        effect_raw="-10%",
        description="Example",
    )
    PlayerCard.objects.create(player=player, card_definition=card_def, card_slug=card_def.slug, stars_unlocked=1)

    url = reverse("core:ultimate_weapon_progress")
    response = auth_client.get(url)
    assert response.status_code == 200

    tile = next(entry for entry in response.context["ultimate_weapons"] if entry["slug"] == uw.slug)
    cooldown_row = next(p for p in tile["parameters"] if p["name"] == "Cooldown")
    assert cooldown_row["base_value_raw"] == "10s"
    assert cooldown_row["effective_value_raw"] == "8s"
    assert isinstance(cooldown_row["modifier_explanations"], list)
    assert len(cooldown_row["modifier_explanations"]) >= 1

    assert b"Effective Value Breakdown" in response.content

    # Schema remains stable even if explanations are empty for other rows.
    for row in tile["parameters"]:
        assert "base_value_raw" in row
        assert "effective_value_raw" in row
        assert "modifier_explanations" in row


@pytest.mark.django_db
def test_effective_value_breakdown_not_rendered_when_empty(auth_client, player) -> None:
    """UI does not render an empty breakdown container."""

    uw = _uw_with_cooldown_param(slug="bh", name="Black Hole")
    player_uw = PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=uw,
        ultimate_weapon_slug=uw.slug,
        unlocked=True,
    )

    # Create parameter rows without effective overrides/notes.
    for param_def in uw.parameter_definitions.all():
        PlayerUltimateWeaponParameter.objects.create(
            player=player,
            player_ultimate_weapon=player_uw,
            parameter_definition=param_def,
            level=1,
        )

    url = reverse("core:ultimate_weapon_progress")
    response = auth_client.get(url)
    assert response.status_code == 200
    assert b"Effective Value Breakdown" not in response.content
