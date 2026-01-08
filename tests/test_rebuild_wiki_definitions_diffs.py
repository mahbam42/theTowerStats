"""Integration tests for rebuild_wiki_definitions --diffs output."""

from __future__ import annotations

import io

import pytest
from django.core.management import call_command

from core.management.commands import fetch_wiki_data
from core.wiki_ingestion import compute_content_hash, make_entity_id
from definitions.models import WikiData


@pytest.mark.integration
@pytest.mark.django_db
def test_rebuild_wiki_definitions_diffs_outputs_statuses(monkeypatch) -> None:
    """Preview diffs include added, changed, and deprecated entries."""

    url = "https://example.test/bot#Cost"
    bot_name = "Test Bot"
    bot_id = make_entity_id(bot_name)
    source_section = f"bots_{bot_id}_table_0"
    parse_version = fetch_wiki_data.Command.PARSE_VERSION_BOTS

    monkeypatch.setattr(fetch_wiki_data.Command, "BOT_PAGES", ((bot_name, url),))

    html = (
        "<html><body>"
        '<h2><span class="mw-headline" id="Cost">Cost</span></h2>'
        "<table>"
        "<tr><th>Level</th><th>Cost</th><th>Cooldown</th></tr>"
        "<tr><td>1</td><td>12</td><td>5</td></tr>"
        "<tr><td>3</td><td>30</td><td>3</td></tr>"
        "</table>"
        "</body></html>"
    )
    monkeypatch.setattr(fetch_wiki_data, "_fetch_html", lambda _url: html)

    def create_row(level: int, cost: int, cooldown: int) -> None:
        raw_row = {
            "Level": str(level),
            "Cost": str(cost),
            "Cooldown": str(cooldown),
            "_wiki_entity_id": bot_id,
            "Bot": bot_name,
        }
        WikiData.objects.create(
            page_url=url,
            canonical_name=bot_name,
            entity_id=f"{bot_id}__level_{level}__star_none",
            content_hash=compute_content_hash(raw_row),
            raw_row=raw_row,
            source_section=source_section,
            parse_version=parse_version,
        )

    create_row(level=1, cost=10, cooldown=5)
    create_row(level=2, cost=20, cooldown=4)

    stdout = io.StringIO()
    call_command("rebuild_wiki_definitions", "--target", "bots", "--diffs", stdout=stdout)

    output = stdout.getvalue()
    assert "changed" in output
    assert "deprecated" in output
    assert "added" in output
    assert f"{bot_id}__level_1__star_none" in output
    assert "Cost" in output
    assert "10" in output
    assert "12" in output


@pytest.mark.integration
@pytest.mark.django_db
@pytest.mark.regression
def test_rebuild_wiki_definitions_diffs_includes_previous_alias_values(monkeypatch) -> None:
    """Alias headers should show previous values in diff output."""

    url = "https://example.test/uw"
    uw_name = "Test Weapon"
    uw_id = make_entity_id(uw_name)
    source_section = f"ultimate_weapons_{uw_id}_table_0"
    parse_version = fetch_wiki_data.Command.PARSE_VERSION_ULTIMATE_WEAPONS

    monkeypatch.setattr(fetch_wiki_data.Command, "UW_PAGES", ((uw_name, url),))

    html = (
        "<html><body>"
        "<table>"
        "<tr><th>Level</th><th>Cooldown (s)</th><th>Stones</th></tr>"
        "<tr><td>1</td><td>15</td><td>5</td></tr>"
        "</table>"
        "</body></html>"
    )
    monkeypatch.setattr(fetch_wiki_data, "_fetch_html", lambda _url: html)

    raw_row = {
        "Level": "1",
        "Cooldown (s)": "20",
        "Stones": "5",
        "_wiki_entity_id": uw_id,
        "Ultimate Weapon": uw_name,
    }
    WikiData.objects.create(
        page_url=url,
        canonical_name=uw_name,
        entity_id=f"{uw_id}__level_1__star_none",
        content_hash=compute_content_hash(raw_row),
        raw_row=raw_row,
        source_section=source_section,
        parse_version=parse_version,
    )

    stdout = io.StringIO()
    call_command("rebuild_wiki_definitions", "--target", "ultimate_weapons", "--diffs", stdout=stdout)
    output = stdout.getvalue()
    assert "Cooldown" in output
    assert "20" in output
    assert "15" in output


@pytest.mark.integration
@pytest.mark.django_db
@pytest.mark.regression
def test_rebuild_wiki_definitions_diffs_skips_total_rows(monkeypatch) -> None:
    """Diff preview should omit wiki total/summary rows."""

    url = "https://example.test/guardian"
    chip_name = "Ally"
    chip_id = make_entity_id(chip_name)
    source_section = f"guardian_chips_{chip_id}_table_0"
    parse_version = fetch_wiki_data.Command.PARSE_VERSION_GUARDIAN_CHIPS

    monkeypatch.setattr(fetch_wiki_data.Command, "DEFAULT_GUARDIAN_URL", url)

    html = (
        "<html><body>"
        '<h2><span class="mw-headline" id="Ally_Chip">Ally Chip</span></h2>'
        "<table>"
        "<tr><th>Level</th><th>Recovery Amount</th><th>Bits</th></tr>"
        "<tr><td>1</td><td>1%</td><td>5</td></tr>"
        "<tr><td>Total</td><td>Total</td><td>10</td></tr>"
        "</table>"
        "</body></html>"
    )
    monkeypatch.setattr(fetch_wiki_data, "_fetch_html", lambda _url: html)

    raw_row = {
        "Level": "1",
        "Recovery Amount": "",
        "Bits": "",
        "_wiki_entity_id": chip_id,
        "Guardian": chip_name,
    }
    WikiData.objects.create(
        page_url=url,
        canonical_name=chip_name,
        entity_id=f"{chip_id}__level_1__star_none",
        content_hash=compute_content_hash(raw_row),
        raw_row=raw_row,
        source_section=source_section,
        parse_version=parse_version,
    )

    stdout = io.StringIO()
    call_command("rebuild_wiki_definitions", "--target", "guardians", "--diffs", stdout=stdout)
    output = stdout.getvalue()
    assert "Total" not in output
