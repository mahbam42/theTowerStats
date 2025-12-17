"""Integration tests for the Cards dashboard interactions."""

from __future__ import annotations

import pytest
from django.urls import reverse

from definitions.models import CardDefinition, WikiData
from player_state.models import Player, PlayerCard, Preset


def _wikidata_row(*, canonical_name: str, entity_id: str, raw_row: dict[str, str], content_hash: str) -> WikiData:
    """Create a minimal WikiData row for test fixtures."""

    return WikiData.objects.create(
        page_url="https://example.test/wiki/Cards",
        canonical_name=canonical_name,
        entity_id=entity_id,
        content_hash=content_hash,
        raw_row=raw_row,
        source_section="cards_table_0",
        parse_version="cards_v1",
    )


@pytest.mark.django_db
def test_cards_dashboard_unlocks_next_slot_until_max(client) -> None:
    """Unlock Next Slot increments player card_slots_unlocked up to the wiki max."""

    player = Player.objects.create(name="default", card_slots_unlocked=0)
    _wikidata_row(canonical_name="1", entity_id="1", raw_row={"Slots": "1", "Cost": "10"}, content_hash="a" * 64)
    _wikidata_row(canonical_name="2", entity_id="2", raw_row={"Slots": "2", "Cost": "20"}, content_hash="b" * 64)

    url = reverse("core:cards")
    client.post(url, data={"action": "unlock_slot"})
    player.refresh_from_db()
    assert player.card_slots_unlocked == 1

    client.post(url, data={"action": "unlock_slot"})
    player.refresh_from_db()
    assert player.card_slots_unlocked == 2

    client.post(url, data={"action": "unlock_slot"})
    player.refresh_from_db()
    assert player.card_slots_unlocked == 2


@pytest.mark.django_db
def test_cards_dashboard_handles_missing_slot_wikidata(client) -> None:
    """Cards dashboard stays usable when card slot wiki data is missing."""

    player = Player.objects.create(name="default", card_slots_unlocked=0)

    url = reverse("core:cards")
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Not tracked yet" in content

    client.post(url, data={"action": "unlock_slot"})
    player.refresh_from_db()
    assert player.card_slots_unlocked == 0


@pytest.mark.django_db
def test_cards_dashboard_updates_inventory_and_presets(client) -> None:
    """Inventory edits persist and presets can be assigned and filtered."""

    wiki = WikiData.objects.create(
        page_url="https://example.test/wiki",
        canonical_name="Coin Bonus",
        entity_id="coin_bonus",
        content_hash="c" * 64,
        raw_row={"Card": "Coin Bonus", "Effect": "+5%", "_wiki_table_label": "Common"},
        source_section="cards_list_common_1",
        parse_version="cards_list_v1",
    )
    definition1 = CardDefinition.objects.create(
        name="Coin Bonus",
        slug="coin_bonus",
        rarity="Common",
        effect_raw="+5%",
        description="Increase coins earned.",
        source_wikidata=wiki,
    )
    definition2 = CardDefinition.objects.create(name="Wave Skip", slug="wave_skip", rarity="Rare", effect_raw="Skip 1 wave")

    player = Player.objects.create(name="default")
    card1 = PlayerCard.objects.create(player=player, card_definition=definition1, card_slug=definition1.slug)
    PlayerCard.objects.create(player=player, card_definition=definition2, card_slug=definition2.slug)
    preset = Preset.objects.create(player=player, name="Farming")
    assert preset.color

    url = reverse("core:cards")
    client.post(
        url,
        data={
            "action": "update_inventory",
            "card_id": card1.id,
            "inventory_count": 7,
        },
    )
    card1.refresh_from_db()
    assert card1.stars_unlocked == 3
    assert card1.inventory_count == 4

    client.post(
        url,
        data={
            "action": "update_presets",
            "card_id": card1.id,
            "presets": [preset.id],
            "new_preset_name": "",
        },
    )
    card1.refresh_from_db()
    assert list(card1.presets.values_list("name", flat=True)) == ["Farming"]

    response = client.get(url, data={"presets": [preset.id]})
    content = response.content.decode("utf-8")
    assert "Coin Bonus" in content
    assert "Wave Skip" not in content
    assert "Increase coins earned." in content


@pytest.mark.django_db
def test_cards_dashboard_inventory_rollover_and_clamps(client) -> None:
    """Inventory rollover advances stars and clamps at max."""

    definition = CardDefinition.objects.create(name="Coin Bonus", slug="coin_bonus", rarity="Common")
    player = Player.objects.create(name="default")
    card = PlayerCard.objects.create(
        player=player,
        card_definition=definition,
        card_slug=definition.slug,
        stars_unlocked=6,
        inventory_count=18,
    )

    url = reverse("core:cards")
    client.post(
        url,
        data={
            "action": "update_inventory",
            "card_id": card.id,
            "inventory_count": 21,
        },
    )
    card.refresh_from_db()
    assert card.stars_unlocked == 7
    assert card.inventory_count == 1

    client.post(
        url,
        data={
            "action": "update_inventory",
            "card_id": card.id,
            "inventory_count": 99,
        },
    )
    card.refresh_from_db()
    assert card.stars_unlocked == 7
    assert card.inventory_count == 32
