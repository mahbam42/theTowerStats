"""Regression tests for Cards wiki effect ingestion and rendering."""

from __future__ import annotations

import pytest
from django.urls import reverse

from core.wiki_ingestion import ingest_wiki_rows, scrape_entity_rows
from definitions.models import CardDefinition
from definitions.wiki_rebuild import rebuild_cards_from_wikidata
from player_state.models import PlayerCard

pytestmark = pytest.mark.integration


def _cards_list_table_html() -> str:
    """Return a minimal Cards list HTML table using per-level columns."""

    return """
<!doctype html>
<html>
  <body>
    <table class="wikitable">
      <tr>
        <th>Name</th>
        <th>Rarity</th>
        <th>Description</th>
        <th>Lv. 1</th>
        <th>Lv. 2</th>
        <th>Lv. 3</th>
        <th>Lv. 4</th>
        <th>Lv. 5</th>
        <th>Lv. 6</th>
        <th>Lv. 7</th>
      </tr>
      <tr>
        <td>Attack Speed</td>
        <td>Common</td>
        <td>Increase tower attack speed by x #</td>
        <td>1.25</td>
        <td>1.40</td>
        <td>1.55</td>
        <td>1.70</td>
        <td>1.85</td>
        <td>2.00</td>
        <td>2.15</td>
      </tr>
      <tr>
        <td>Critical Coin</td>
        <td>Rare</td>
        <td>If a basic enemy dies from a critical shot it has a chance to drop coins of #%</td>
        <td>15%</td>
        <td>18%</td>
        <td>21%</td>
        <td>24%</td>
        <td>27%</td>
        <td>30%</td>
        <td>33%</td>
      </tr>
      <tr>
        <td>Berserker</td>
        <td>Epic</td>
        <td>Increase damage by [x] of total damage absorbed this round (max of x8 tower damage)</td>
        <td>0.8%</td>
        <td>0.9%</td>
        <td>1.0%</td>
        <td>1.1%</td>
        <td>1.2%</td>
        <td>1.3%</td>
        <td>1.4%</td>
      </tr>
    </table>
  </body>
</html>
""".strip()


@pytest.mark.django_db
def test_rebuild_cards_derives_effect_raw_from_level_columns() -> None:
    """Cards list tables with per-level columns should rebuild into effect_raw."""

    html = _cards_list_table_html()
    scraped = scrape_entity_rows(html, table_index=0, name_column="Name")
    ingest_wiki_rows(
        scraped,
        page_url="https://example.test/wiki/Cards",
        source_section="cards_list_table_0",
        parse_version="cards_list_v1",
        write=True,
    )

    rebuild_cards_from_wikidata(write=True)

    attack_speed = CardDefinition.objects.get(slug="attack_speed")
    assert (
        attack_speed.effect_raw
        == "x 1.25 / x 1.40 / x 1.55 / x 1.70 / x 1.85 / x 2.00 / x 2.15"
    )

    critical = CardDefinition.objects.get(slug="critical_coin")
    assert critical.effect_raw == "15% / 18% / 21% / 24% / 27% / 30% / 33%"

    berserker = CardDefinition.objects.get(slug="berserker")
    assert berserker.effect_raw == "0.8% / 0.9% / 1.0% / 1.1% / 1.2% / 1.3% / 1.4%"


@pytest.mark.django_db
def test_cards_dashboard_renders_level_value_from_rebuilt_effects(auth_client, player) -> None:
    """Cards dashboard should substitute placeholders when rebuilt effects are available."""

    html = _cards_list_table_html()
    scraped = scrape_entity_rows(html, table_index=0, name_column="Name")
    ingest_wiki_rows(
        scraped,
        page_url="https://example.test/wiki/Cards",
        source_section="cards_list_table_0",
        parse_version="cards_list_v1",
        write=True,
    )
    rebuild_cards_from_wikidata(write=True)

    attack_speed = CardDefinition.objects.get(slug="attack_speed")
    critical = CardDefinition.objects.get(slug="critical_coin")

    PlayerCard.objects.create(
        player=player,
        card_definition=attack_speed,
        card_slug=attack_speed.slug,
        stars_unlocked=7,
        inventory_count=0,
    )
    PlayerCard.objects.create(
        player=player,
        card_definition=critical,
        card_slug=critical.slug,
        stars_unlocked=5,
        inventory_count=0,
    )

    response = auth_client.get(reverse("core:cards"))
    content = response.content.decode("utf-8")
    assert "Increase tower attack speed by x <strong>2.15</strong>" in content
    assert "drop coins of <strong>27</strong>%" in content
    assert "Increase tower attack speed by x #" not in content
