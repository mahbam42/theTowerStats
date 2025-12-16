"""Tests for Phase 2.75 wiki ingestion (versioned, non-destructive)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from definitions.models import WikiData
from core.wiki_ingestion import (
    ScrapedWikiRow,
    compute_content_hash,
    find_table_indexes_by_anchor,
    ingest_wiki_rows,
    list_tables,
    make_entity_id,
    scrape_entity_rows,
    scrape_leveled_entity_rows,
)


def _fixture_html(name: str) -> str:
    """Load HTML fixture content from the tests fixture directory."""

    fixture_path = Path(__file__).parent / "fixtures" / name
    return fixture_path.read_text(encoding="utf-8")


def test_compute_content_hash_is_stable_for_equivalent_input() -> None:
    """Hash the same normalized payload and assert the digest is stable."""

    payload_a = {"Name": "Coin Bonus", "Effect": "+5%"}
    payload_b = {"Effect": "+5%", "Name": "Coin Bonus"}
    assert compute_content_hash(payload_a) == compute_content_hash(payload_b)


def test_find_table_indexes_by_anchor_selects_list_of_cards_tables() -> None:
    """Select the tables under the List_of_Cards section anchor."""

    html = _fixture_html("wiki_cards_page_list_of_cards_v1.html")
    tables = list_tables(html)
    assert len(tables) == 4

    indexes = find_table_indexes_by_anchor(html, anchor_id="List_of_Cards")
    assert indexes == [1, 2, 3]


@pytest.mark.django_db
def test_ingest_wiki_rows_creates_records_for_new_entities(monkeypatch) -> None:
    """New scraped entities insert new WikiData rows."""

    from core import wiki_ingestion

    monkeypatch.setattr(
        wiki_ingestion.timezone,
        "now",
        lambda: datetime(2025, 12, 14, 12, 0, tzinfo=timezone.utc),
    )

    html = _fixture_html("wiki_cards_table_v1.html")
    rows = scrape_entity_rows(html, table_index=0, name_column="Name")
    summary = ingest_wiki_rows(
        rows,
        page_url="https://example.test/wiki/Cards",
        source_section="cards_table_0",
        parse_version="cards_v1",
        write=True,
    )

    assert summary.added == 2
    assert summary.changed == 0
    assert summary.unchanged == 0
    assert summary.deprecated == 0
    assert WikiData.objects.count() == 2


@pytest.mark.django_db
def test_ingest_wiki_rows_creates_new_revision_on_change(monkeypatch) -> None:
    """Changed content inserts a new revision instead of overwriting."""

    from core import wiki_ingestion

    html_v1 = _fixture_html("wiki_cards_table_v1.html")
    rows_v1 = scrape_entity_rows(html_v1, table_index=0, name_column="Name")

    monkeypatch.setattr(
        wiki_ingestion.timezone,
        "now",
        lambda: datetime(2025, 12, 14, 12, 0, tzinfo=timezone.utc),
    )
    ingest_wiki_rows(
        rows_v1,
        page_url="https://example.test/wiki/Cards",
        source_section="cards_table_0",
        parse_version="cards_v1",
        write=True,
    )

    html_v2 = html_v1.replace("+5%", "+6%")
    rows_v2 = scrape_entity_rows(html_v2, table_index=0, name_column="Name")
    monkeypatch.setattr(
        wiki_ingestion.timezone,
        "now",
        lambda: datetime(2025, 12, 15, 12, 0, tzinfo=timezone.utc),
    )
    summary = ingest_wiki_rows(
        rows_v2,
        page_url="https://example.test/wiki/Cards",
        source_section="cards_table_0",
        parse_version="cards_v1",
        write=True,
    )

    assert summary.added == 0
    assert summary.changed == 1
    assert summary.unchanged == 1
    assert summary.deprecated == 0

    entity_id = make_entity_id("Coin Bonus")
    revisions = list(WikiData.objects.filter(entity_id=entity_id).order_by("first_seen", "id"))
    assert len(revisions) == 2
    assert revisions[0].raw_row["Effect"] == "+5%"
    assert revisions[1].raw_row["Effect"] == "+6%"
    assert revisions[0].content_hash != revisions[1].content_hash


@pytest.mark.django_db
def test_ingest_wiki_rows_check_mode_performs_no_writes(monkeypatch) -> None:
    """Dry-run mode returns a summary without mutating the database."""

    from core import wiki_ingestion

    html = _fixture_html("wiki_cards_table_v1.html")
    rows = scrape_entity_rows(html, table_index=0, name_column="Name")

    monkeypatch.setattr(
        wiki_ingestion.timezone,
        "now",
        lambda: datetime(2025, 12, 14, 12, 0, tzinfo=timezone.utc),
    )
    summary = ingest_wiki_rows(
        rows,
        page_url="https://example.test/wiki/Cards",
        source_section="cards_table_0",
        parse_version="cards_v1",
        write=False,
    )
    assert summary.added == 2
    assert WikiData.objects.count() == 0

    ingest_wiki_rows(
        rows,
        page_url="https://example.test/wiki/Cards",
        source_section="cards_table_0",
        parse_version="cards_v1",
        write=True,
    )
    record = WikiData.objects.get(entity_id=make_entity_id("Coin Bonus"))
    original_last_seen = record.last_seen

    monkeypatch.setattr(
        wiki_ingestion.timezone,
        "now",
        lambda: datetime(2025, 12, 20, 12, 0, tzinfo=timezone.utc),
    )
    ingest_wiki_rows(
        rows,
        page_url="https://example.test/wiki/Cards",
        source_section="cards_table_0",
        parse_version="cards_v1",
        write=False,
    )
    record.refresh_from_db()
    assert record.last_seen == original_last_seen


@pytest.mark.django_db
def test_ingest_wiki_rows_marks_missing_entities_deprecated(monkeypatch) -> None:
    """Entities missing from the latest scrape are marked deprecated."""

    from core import wiki_ingestion

    html = _fixture_html("wiki_cards_table_v1.html")
    all_rows = scrape_entity_rows(html, table_index=0, name_column="Name")

    monkeypatch.setattr(
        wiki_ingestion.timezone,
        "now",
        lambda: datetime(2025, 12, 14, 12, 0, tzinfo=timezone.utc),
    )
    ingest_wiki_rows(
        all_rows,
        page_url="https://example.test/wiki/Cards",
        source_section="cards_table_0",
        parse_version="cards_v1",
        write=True,
    )

    only_one = [row for row in all_rows if row.entity_id == make_entity_id("Coin Bonus")]
    monkeypatch.setattr(
        wiki_ingestion.timezone,
        "now",
        lambda: datetime(2025, 12, 16, 12, 0, tzinfo=timezone.utc),
    )
    summary = ingest_wiki_rows(
        only_one,
        page_url="https://example.test/wiki/Cards",
        source_section="cards_table_0",
        parse_version="cards_v1",
        write=True,
    )
    assert summary.deprecated == 1

    missing = WikiData.objects.get(entity_id=make_entity_id("Wave Skip"))
    assert missing.deprecated is True


@pytest.mark.django_db
def test_scrape_entity_rows_can_add_table_label_extra_fields() -> None:
    """Merge extra fields into raw_row so multiple tables can be distinguished."""

    html = _fixture_html("wiki_cards_page_list_of_cards_v1.html")
    rows = scrape_entity_rows(
        html,
        table_index=1,
        name_column=None,
        extra_fields={"_wiki_table_label": "Common"},
    )
    assert rows[0].canonical_name == "Coin Bonus"
    assert rows[0].raw_row["_wiki_table_label"] == "Common"


def test_extract_table_dedupes_duplicate_headers_without_loss() -> None:
    """Duplicate headers are made unique so no values are overwritten."""

    from core.wiki_ingestion import extract_table

    html = _fixture_html("wiki_guardian_ally_chip_table_v1.html")
    headers, rows = extract_table(html, table_index=0)
    assert headers == [
        "Recovery Amount",
        "Bits",
        "Cooldown(s)",
        "Bits__2",
        "Max Recovey",
        "Bits__3",
    ]
    assert rows[0]["Bits"] == "0"
    assert rows[0]["Bits__2"] == "0"
    assert rows[0]["Bits__3"] == "0"


def test_find_table_indexes_by_anchor_selects_guardian_chip_section_tables() -> None:
    """Select tables under a chip-specific h2 anchor (section-based matching)."""

    html = _fixture_html("wiki_guardian_ally_chip_table_v1.html")
    indexes = find_table_indexes_by_anchor(html, anchor_id="Ally_Chip")
    assert indexes == [0]


@pytest.mark.django_db
def test_ingest_wiki_rows_skips_total_and_placeholder_rows() -> None:
    """Skip non-entity summary rows such as 'Total' or all-placeholder rows."""

    total_row = {"Name": "Total", "Effect": "-", "Notes": ""}
    placeholder_row = {"Name": "—", "Effect": "-", "Notes": "null"}
    valid_row = {"Name": "Coin Bonus", "Effect": "+5%"}

    scraped = [
        ScrapedWikiRow(
            canonical_name=total_row["Name"],
            entity_id=make_entity_id(total_row["Name"]),
            raw_row=total_row,
            content_hash=compute_content_hash(total_row),
        ),
        ScrapedWikiRow(
            canonical_name=placeholder_row["Name"],
            entity_id=make_entity_id(placeholder_row["Name"]),
            raw_row=placeholder_row,
            content_hash=compute_content_hash(placeholder_row),
        ),
        ScrapedWikiRow(
            canonical_name=valid_row["Name"],
            entity_id=make_entity_id(valid_row["Name"]),
            raw_row=valid_row,
            content_hash=compute_content_hash(valid_row),
        ),
    ]

    summary = ingest_wiki_rows(
        scraped,
        page_url="https://example.test/wiki/Cards",
        source_section="cards_table_0",
        parse_version="cards_v1",
        write=True,
    )

    assert summary.added == 1
    assert WikiData.objects.count() == 1
    assert WikiData.objects.get().canonical_name == "Coin Bonus"


def test_scrape_leveled_entity_rows_injects_level_and_alias_keys() -> None:
    """Leveled scraping can add a Level field and header aliases."""

    html = _fixture_html("wiki_guardian_ally_chip_table_v1.html")
    rows = scrape_leveled_entity_rows(
        html,
        table_index=0,
        entity_name="Ally",
        entity_id=make_entity_id("Ally"),
        entity_field="Guardian",
        add_level_if_missing=True,
        header_aliases={"Cooldown(s)": "Cooldown", "Max Recovey": "Max Recovery"},
    )
    assert len(rows) == 2
    assert rows[0].canonical_name == "Ally"
    assert rows[0].raw_row["_wiki_entity_id"] == "ally"
    assert rows[0].raw_row["Guardian"] == "Ally"
    assert rows[0].raw_row["Level"] == "1"
    assert rows[0].raw_row["Cooldown(s)"] == "120"
    assert rows[0].raw_row["Cooldown"] == "120"
    assert rows[0].raw_row["Max Recovery"] == "1.1x"
