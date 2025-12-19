"""Regression tests for the Guardian Chips Progress dashboard."""

from __future__ import annotations

from uuid import uuid4

import pytest
from django.urls import reverse

from definitions.models import (
    Currency,
    GuardianChipDefinition,
    GuardianChipParameterDefinition,
    GuardianChipParameterLevel,
    ParameterKey,
    WikiData,
)
from player_state.models import PlayerGuardianChip, PlayerGuardianChipParameter


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


def _guardian_with_three_parameters(*, slug: str, name: str) -> GuardianChipDefinition:
    """Create a guardian chip definition with three parameters and levels."""

    wiki = _wiki(suffix=slug)
    guardian = GuardianChipDefinition.objects.create(name=name, slug=slug, source_wikidata=wiki)
    params = (
        (ParameterKey.MULTIPLIER, "Multiplier"),
        (ParameterKey.COOLDOWN, "Cooldown"),
        (ParameterKey.DURATION, "Duration"),
    )
    for key, display in params:
        param_def = GuardianChipParameterDefinition.objects.create(
            guardian_chip_definition=guardian,
            key=key,
            display_name=display,
        )
        GuardianChipParameterLevel.objects.create(
            parameter_definition=param_def,
            level=1,
            value_raw="10",
            cost_raw="5",
            currency=Currency.BITS,
            source_wikidata=wiki,
        )
        GuardianChipParameterLevel.objects.create(
            parameter_definition=param_def,
            level=2,
            value_raw="12",
            cost_raw="6",
            currency=Currency.BITS,
            source_wikidata=wiki,
        )
    return guardian


@pytest.mark.django_db
def test_guardian_unlock_creates_three_parameter_rows(auth_client, player) -> None:
    """Unlocking a guardian chip creates 3 parameter rows at the minimum level."""

    guardian = _guardian_with_three_parameters(slug="recovery", name="Recovery")
    chip = PlayerGuardianChip.objects.create(
        player=player,
        guardian_chip_definition=guardian,
        guardian_chip_slug=guardian.slug,
        unlocked=False,
        active=False,
    )

    url = reverse("core:guardian_progress")
    response = auth_client.post(url, data={"action": "unlock_guardian_chip", "entity_id": chip.id})
    assert response.status_code == 302

    chip.refresh_from_db()
    assert chip.unlocked is True
    params = list(PlayerGuardianChipParameter.objects.filter(player_guardian_chip=chip).order_by("id"))
    assert len(params) == 3
    assert all(p.level == 1 for p in params)

    response = auth_client.get(url)
    assert response.status_code == 200
    tiles = response.context["guardian_chips"]
    tile = next(entry for entry in tiles if entry["slug"] == guardian.slug)
    assert tile["summary"]["total_invested"] == 0


@pytest.mark.django_db
def test_guardian_level_up_increments_until_max(auth_client, player) -> None:
    """Level-up increments by 1 and stops at max level."""

    guardian = _guardian_with_three_parameters(slug="stun", name="Stun")
    chip = PlayerGuardianChip.objects.create(
        player=player,
        guardian_chip_definition=guardian,
        guardian_chip_slug=guardian.slug,
        unlocked=True,
        active=False,
    )
    param_def = guardian.parameter_definitions.order_by("id").first()
    assert param_def is not None
    player_param = PlayerGuardianChipParameter.objects.create(
        player=player,
        player_guardian_chip=chip,
        parameter_definition=param_def,
        level=1,
    )

    url = reverse("core:guardian_progress")
    response = auth_client.post(url, data={"action": "level_up_guardian_param", "param_id": player_param.id})
    assert response.status_code == 302
    player_param.refresh_from_db()
    assert player_param.level == 2

    response = auth_client.post(url, data={"action": "level_up_guardian_param", "param_id": player_param.id})
    assert response.status_code == 302
    player_param.refresh_from_db()
    assert player_param.level == 2


@pytest.mark.django_db
def test_guardian_level_down_decrements_until_min(auth_client, player) -> None:
    """Level-down decrements by 1 and stops at the minimum level."""

    guardian = _guardian_with_three_parameters(slug="aegis", name="Aegis")
    chip = PlayerGuardianChip.objects.create(
        player=player,
        guardian_chip_definition=guardian,
        guardian_chip_slug=guardian.slug,
        unlocked=True,
        active=False,
    )
    param_def = guardian.parameter_definitions.order_by("id").first()
    assert param_def is not None
    player_param = PlayerGuardianChipParameter.objects.create(
        player=player,
        player_guardian_chip=chip,
        parameter_definition=param_def,
        level=2,
    )

    url = reverse("core:guardian_progress")
    response = auth_client.post(url, data={"action": "level_down_guardian_param", "param_id": player_param.id})
    assert response.status_code == 302
    player_param.refresh_from_db()
    assert player_param.level == 1

    response = auth_client.post(url, data={"action": "level_down_guardian_param", "param_id": player_param.id})
    assert response.status_code == 302
    player_param.refresh_from_db()
    assert player_param.level == 1


@pytest.mark.django_db
def test_guardian_active_enforces_max_two(auth_client, player, settings) -> None:
    """Guardian chips enforce a maximum of 2 active at once."""

    settings.DEBUG = False
    g1 = _guardian_with_three_parameters(slug="g1", name="G1")
    g2 = _guardian_with_three_parameters(slug="g2", name="G2")
    g3 = _guardian_with_three_parameters(slug="g3", name="G3")
    chip1 = PlayerGuardianChip.objects.create(
        player=player,
        guardian_chip_definition=g1,
        guardian_chip_slug=g1.slug,
        unlocked=True,
        active=True,
    )
    chip2 = PlayerGuardianChip.objects.create(
        player=player,
        guardian_chip_definition=g2,
        guardian_chip_slug=g2.slug,
        unlocked=True,
        active=True,
    )
    chip3 = PlayerGuardianChip.objects.create(
        player=player,
        guardian_chip_definition=g3,
        guardian_chip_slug=g3.slug,
        unlocked=True,
        active=False,
    )

    url = reverse("core:guardian_progress")
    response = auth_client.post(
        url,
        data={"action": "set_guardian_active", "entity_id": chip3.id, "active": "1"},
    )
    assert response.status_code == 302

    chip1.refresh_from_db()
    chip2.refresh_from_db()
    chip3.refresh_from_db()
    assert chip1.active is True
    assert chip2.active is True
    assert chip3.active is False


@pytest.mark.django_db
def test_guardian_active_checkbox_payload_sets_active(auth_client, player) -> None:
    """Checkbox posts include both hidden and checked values; checked wins."""

    guardian = _guardian_with_three_parameters(slug="ally", name="Ally")
    chip = PlayerGuardianChip.objects.create(
        player=player,
        guardian_chip_definition=guardian,
        guardian_chip_slug=guardian.slug,
        unlocked=True,
        active=False,
    )

    url = reverse("core:guardian_progress")
    response = auth_client.post(
        url,
        data={
            "action": "set_guardian_active",
            "entity_id": chip.id,
            "active": ["0", "1"],
        },
    )
    assert response.status_code == 302
    chip.refresh_from_db()
    assert chip.active is True

    response = auth_client.post(
        url,
        data={
            "action": "set_guardian_active",
            "entity_id": chip.id,
            "active": ["0"],
        },
    )
    assert response.status_code == 302
    chip.refresh_from_db()
    assert chip.active is False


@pytest.mark.django_db
def test_guardian_active_ajax_returns_json(auth_client, player) -> None:
    """AJAX toggle returns JSON and updates state."""

    guardian = _guardian_with_three_parameters(slug="attack", name="Attack")
    chip = PlayerGuardianChip.objects.create(
        player=player,
        guardian_chip_definition=guardian,
        guardian_chip_slug=guardian.slug,
        unlocked=True,
        active=False,
    )

    url = reverse("core:guardian_progress")
    response = auth_client.post(
        url,
        data={"action": "set_guardian_active", "entity_id": chip.id, "active": ["0", "1"]},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True
    chip.refresh_from_db()
    assert chip.active is True


@pytest.mark.django_db
def test_guardian_dashboard_omits_invalid_guardian_in_production(auth_client, player, settings) -> None:
    """Production mode omits guardian chips that do not have exactly 3 parameters."""

    settings.DEBUG = False
    wiki = _wiki()
    bad = GuardianChipDefinition.objects.create(name="Bad Guardian", slug="bad_guardian", source_wikidata=wiki)
    param_def = GuardianChipParameterDefinition.objects.create(
        guardian_chip_definition=bad,
        key=ParameterKey.MULTIPLIER,
        display_name="Multiplier",
    )
    GuardianChipParameterLevel.objects.create(
        parameter_definition=param_def,
        level=1,
        value_raw="10",
        cost_raw="5",
        currency=Currency.BITS,
        source_wikidata=wiki,
    )

    PlayerGuardianChip.objects.create(
        player=player,
        guardian_chip_definition=bad,
        guardian_chip_slug=bad.slug,
        unlocked=True,
        active=False,
    )

    url = reverse("core:guardian_progress")
    response = auth_client.get(url)
    assert response.status_code == 200
    assert all(tile["slug"] != "bad_guardian" for tile in response.context["guardian_chips"])


@pytest.mark.django_db
def test_guardian_dashboard_deletes_orphaned_parameter_rows(auth_client, player) -> None:
    """Orphaned parameter rows are deleted so the page can render in debug mode."""

    guardian = _guardian_with_three_parameters(slug="ally", name="Ally")
    chip = PlayerGuardianChip.objects.create(
        player=player,
        guardian_chip_definition=guardian,
        guardian_chip_slug=guardian.slug,
        unlocked=True,
        active=False,
    )
    param_def = guardian.parameter_definitions.order_by("id").first()
    assert param_def is not None
    orphan = PlayerGuardianChipParameter.objects.create(
        player=player,
        player_guardian_chip=chip,
        parameter_definition=param_def,
        level=1,
    )
    param_def.delete()
    orphan.refresh_from_db()
    assert orphan.parameter_definition is None

    url = reverse("core:guardian_progress")
    response = auth_client.get(url)
    assert response.status_code == 200
    assert PlayerGuardianChipParameter.objects.filter(player_guardian_chip=chip).count() == 0
