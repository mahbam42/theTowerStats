"""Integration tests for the Cards dashboard interactions."""

from __future__ import annotations

import re

import pytest
from django.urls import reverse

from definitions.models import CardDefinition, WikiData
from player_state.models import PlayerCard, Preset

pytestmark = pytest.mark.integration


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
def test_cards_dashboard_unlocks_next_slot_until_max(auth_client, player) -> None:
    """Unlock Next Slot increments player card_slots_unlocked up to the wiki max."""

    player.card_slots_unlocked = 0
    player.save(update_fields=["card_slots_unlocked"])
    _wikidata_row(canonical_name="1", entity_id="1", raw_row={"Slots": "1", "Cost": "10"}, content_hash="a" * 64)
    _wikidata_row(canonical_name="2", entity_id="2", raw_row={"Slots": "2", "Cost": "20"}, content_hash="b" * 64)

    url = reverse("core:cards")
    auth_client.post(url, data={"action": "unlock_slot"})
    player.refresh_from_db()
    assert player.card_slots_unlocked == 1

    auth_client.post(url, data={"action": "unlock_slot"})
    player.refresh_from_db()
    assert player.card_slots_unlocked == 2

    auth_client.post(url, data={"action": "unlock_slot"})
    player.refresh_from_db()
    assert player.card_slots_unlocked == 2


@pytest.mark.django_db
def test_cards_dashboard_handles_missing_slot_wikidata(auth_client, player) -> None:
    """Cards dashboard stays usable when card slot wiki data is missing."""

    player.card_slots_unlocked = 0
    player.save(update_fields=["card_slots_unlocked"])

    url = reverse("core:cards")
    response = auth_client.get(url)
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Not tracked yet" in content

    auth_client.post(url, data={"action": "unlock_slot"})
    player.refresh_from_db()
    assert player.card_slots_unlocked == 0


@pytest.mark.django_db
def test_cards_dashboard_updates_inventory_and_presets(auth_client, player) -> None:
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
        wiki_page_url="https://example.test/wiki/Coin_Bonus",
        effect_raw="+5%",
        description="Increase coins earned.",
        source_wikidata=wiki,
    )
    definition2 = CardDefinition.objects.create(name="Wave Skip", slug="wave_skip", rarity="Rare", effect_raw="Skip 1 wave")

    card1 = PlayerCard.objects.create(player=player, card_definition=definition1, card_slug=definition1.slug)
    PlayerCard.objects.create(player=player, card_definition=definition2, card_slug=definition2.slug)
    preset = Preset.objects.create(player=player, name="Farming")
    assert preset.color

    url = reverse("core:cards")
    auth_client.post(
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

    auth_client.post(
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

    response = auth_client.get(url, data={"presets": [preset.id]})
    content = response.content.decode("utf-8")
    assert "Coin Bonus" in content
    assert "Wave Skip" not in content
    assert "Increase coins earned." in content
    assert "+<strong>5</strong>% (Level 3)" in content
    assert 'href="https://example.test/wiki/Coin_Bonus"' in content


def _card_names_in_table(html: str) -> list[str]:
    """Extract card names from the Cards table body, in rendered order."""

    match = re.search(r"<tbody>(?P<body>.*?)</tbody>", html, flags=re.DOTALL)
    if match is None:
        return []
    body = match.group("body")
    names = re.findall(
        r'<tr[^>]*class="[^"]*card-row[^"]*"[^>]*>.*?<td[^>]*class="[^"]*card-name[^"]*"[^>]*>\s*(?P<name>[^<]+)',
        body,
        flags=re.DOTALL,
    )
    return [name.strip() for name in names]


@pytest.mark.django_db
def test_cards_dashboard_supports_sorting_and_maxed_filter(auth_client, player) -> None:
    """Cards table supports sortable columns plus maxed/unmaxed filtering."""

    alpha = CardDefinition.objects.create(
        name="Alpha",
        slug="alpha",
        rarity="Common",
        effect_raw="+5%",
        description="Increase coins earned.",
    )
    beta = CardDefinition.objects.create(
        name="Beta",
        slug="beta",
        rarity="Rare",
        effect_raw="Skip 1 wave",
        description="Skip waves.",
    )

    PlayerCard.objects.create(
        player=player,
        card_definition=alpha,
        card_slug=alpha.slug,
        stars_unlocked=7,
        inventory_count=32,
    )
    PlayerCard.objects.create(
        player=player,
        card_definition=beta,
        card_slug=beta.slug,
        stars_unlocked=3,
        inventory_count=1,
    )

    url = reverse("core:cards")

    response = auth_client.get(url)
    assert _card_names_in_table(response.content.decode("utf-8")) == ["Alpha", "Beta"]

    response = auth_client.get(url, data={"sort": "-name"})
    assert _card_names_in_table(response.content.decode("utf-8")) == ["Beta", "Alpha"]

    response = auth_client.get(url, data={"maxed": "maxed"})
    assert _card_names_in_table(response.content.decode("utf-8")) == ["Alpha"]

    response = auth_client.get(url, data={"maxed": "unmaxed", "sort": "-level"})
    assert _card_names_in_table(response.content.decode("utf-8")) == ["Beta"]


@pytest.mark.django_db
def test_cards_dashboard_preserves_filter_state_in_links(auth_client, player) -> None:
    """Sortable headers and preset badges preserve the current filter state."""

    definition = CardDefinition.objects.create(name="Alpha", slug="alpha", rarity="Common")
    card = PlayerCard.objects.create(player=player, card_definition=definition, card_slug=definition.slug)
    preset = Preset.objects.create(player=player, name="Farming")
    card.presets.add(preset, through_defaults={"player": player})

    url = reverse("core:cards")
    response = auth_client.get(url, data={"maxed": "unmaxed", "sort": "-level"})
    content = response.content.decode("utf-8")

    assert re.search(r'href="\\?[^"]*maxed=unmaxed[^"]*sort=level', content)
    assert re.search(r'href="\\?[^"]*presets=.*maxed=unmaxed[^"]*sort=-level', content) or re.search(
        r'href="\\?[^"]*maxed=unmaxed[^"]*sort=-level[^"]*presets=', content
    )


@pytest.mark.django_db
def test_cards_dashboard_inventory_rollover_and_clamps(auth_client, player) -> None:
    """Inventory rollover advances stars and clamps at max."""

    definition = CardDefinition.objects.create(name="Coin Bonus", slug="coin_bonus", rarity="Common")
    card = PlayerCard.objects.create(
        player=player,
        card_definition=definition,
        card_slug=definition.slug,
        stars_unlocked=6,
        inventory_count=18,
    )

    url = reverse("core:cards")
    auth_client.post(
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

    auth_client.post(
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


@pytest.mark.django_db
def test_cards_dashboard_bulk_assigns_presets(auth_client, player) -> None:
    """Bulk preset edit adds presets to multiple selected cards."""

    alpha = CardDefinition.objects.create(name="Alpha", slug="alpha", rarity="Common")
    beta = CardDefinition.objects.create(name="Beta", slug="beta", rarity="Rare")
    card_a = PlayerCard.objects.create(player=player, card_definition=alpha, card_slug=alpha.slug)
    card_b = PlayerCard.objects.create(player=player, card_definition=beta, card_slug=beta.slug)
    preset = Preset.objects.create(player=player, name="Farming")

    url = reverse("core:cards")
    auth_client.post(
        url,
        data={
            "action": "bulk_update_presets",
            "card_ids": [card_a.id, card_b.id],
            "presets": [preset.id],
            "new_preset_name": "",
        },
    )

    card_a.refresh_from_db()
    card_b.refresh_from_db()
    assert list(card_a.presets.values_list("name", flat=True)) == ["Farming"]
    assert list(card_b.presets.values_list("name", flat=True)) == ["Farming"]


@pytest.mark.django_db
def test_cards_dashboard_parameters_replace_placeholders_with_level_value(auth_client, player) -> None:
    """Placeholder descriptions are substituted with the best-effort value for the current level."""

    critical = CardDefinition.objects.create(
        name="Critical Coin",
        slug="critical_coin",
        rarity="Epic",
        description="Increase critical chance by +#%",
        effect_raw="+15% / +18% / +21% / +24% / +27% / +30% / +33%",
    )
    damage = CardDefinition.objects.create(
        name="Damage",
        slug="damage",
        rarity="Common",
        description="Increase tower damage by x #",
        effect_raw="x 1.60 / x 2.00 / x 2.40 / x 2.80 / x 3.20 / x 3.60 / x 4.00",
    )

    PlayerCard.objects.create(player=player, card_definition=critical, card_slug=critical.slug, stars_unlocked=5)
    PlayerCard.objects.create(player=player, card_definition=damage, card_slug=damage.slug, stars_unlocked=7)

    url = reverse("core:cards")
    response = auth_client.get(url)
    content = response.content.decode("utf-8")
    assert "Increase critical chance by +<strong>27</strong>%" in content
    assert "Increase tower damage by x <strong>4.00</strong>" in content


@pytest.mark.django_db
def test_cards_dashboard_allows_placeholders_when_level_is_zero(auth_client, player) -> None:
    """Level 0 cards may display placeholder descriptions unchanged."""

    critical = CardDefinition.objects.create(
        name="Critical Coin",
        slug="critical_coin",
        rarity="Epic",
        description="Increase critical chance by +#%",
        effect_raw="+15% / +18% / +21% / +24% / +27% / +30% / +33%",
    )
    PlayerCard.objects.create(
        player=player,
        card_definition=critical,
        card_slug=critical.slug,
        stars_unlocked=0,
        inventory_count=0,
    )

    url = reverse("core:cards")
    response = auth_client.get(url)
    content = response.content.decode("utf-8")
    assert "Increase critical chance by +#%" in content
