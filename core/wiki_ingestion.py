"""Wiki ingestion helpers for versioned, non-destructive data capture.

This module is Phase 2.75 scoped:
- fetch a single table from a single wiki page,
- store raw cell text (whitespace-normalized) without interpretation,
- detect changes by deterministic hashing,
- version content by inserting new rows when hashes change.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any, Mapping, Sequence

from django.db import transaction
from django.utils import timezone

from core.models import WikiData

_WHITESPACE_RE = re.compile(r"\s+")
_ENTITY_ID_RE = re.compile(r"[^a-z0-9]+")


def normalize_whitespace(value: str) -> str:
    """Normalize whitespace for deterministic hashing and storage.

    Args:
        value: Raw text extracted from HTML nodes.

    Returns:
        A trimmed string with internal whitespace collapsed to single spaces.
    """

    return _WHITESPACE_RE.sub(" ", value).strip()


def compute_content_hash(raw_row: Mapping[str, str]) -> str:
    """Compute a deterministic SHA-256 hash for a scraped row.

    Args:
        raw_row: Mapping of column header -> raw cell text. Values should already
            be whitespace-normalized.

    Returns:
        A lowercase hex digest of the canonical JSON representation.
    """

    payload = json.dumps(raw_row, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def make_entity_id(canonical_name: str) -> str:
    """Build a stable internal entity identifier from a canonical name.

    Args:
        canonical_name: Human-readable entity name (e.g., card name).

    Returns:
        A lowercase, ASCII-only slug suitable for stable identity comparisons.
    """

    cleaned = normalize_whitespace(canonical_name).lower()
    slug = _ENTITY_ID_RE.sub("_", cleaned).strip("_")
    return slug or "unknown"


@dataclass(frozen=True, slots=True)
class ScrapedWikiRow:
    """A single scraped entity row from a wiki table.

    Attributes:
        canonical_name: Human-readable entity name.
        entity_id: Stable internal identifier derived from `canonical_name`.
        raw_row: Mapping of header -> value for the row (whitespace-normalized).
        content_hash: Deterministic hash of `raw_row`.
    """

    canonical_name: str
    entity_id: str
    raw_row: dict[str, str]
    content_hash: str


class _TableExtractor(HTMLParser):
    """Minimal HTML table extractor for wiki pages.

    This intentionally supports only a subset of HTML needed to pull basic
    tables and does not attempt to preserve markup.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[dict[str, Any]] = []
        self._in_table = False
        self._in_caption = False
        self._in_row = False
        self._in_cell = False
        self._cell_text: list[str] = []
        self._current_table: dict[str, Any] | None = None
        self._current_row: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            self._in_table = True
            self._current_table = {"caption": "", "rows": []}
            return
        if not self._in_table:
            return
        if tag == "caption":
            self._in_caption = True
            return
        if tag == "tr":
            self._in_row = True
            self._current_row = []
            return
        if tag in {"td", "th"} and self._in_row:
            self._in_cell = True
            self._cell_text = []
            return

    def handle_endtag(self, tag: str) -> None:
        if tag == "table" and self._in_table:
            if self._current_table is not None:
                self.tables.append(self._current_table)
            self._current_table = None
            self._in_table = False
            self._in_caption = False
            self._in_row = False
            self._in_cell = False
            self._cell_text = []
            self._current_row = None
            return
        if not self._in_table:
            return
        if tag == "caption":
            self._in_caption = False
            return
        if tag in {"td", "th"} and self._in_cell:
            self._in_cell = False
            text = normalize_whitespace("".join(self._cell_text))
            if self._current_row is not None:
                self._current_row.append(text)
            self._cell_text = []
            return
        if tag == "tr" and self._in_row:
            self._in_row = False
            if self._current_table is not None and self._current_row is not None:
                if any(cell for cell in self._current_row):
                    self._current_table["rows"].append(self._current_row)
            self._current_row = None
            return

    def handle_data(self, data: str) -> None:
        if not self._in_table or self._current_table is None:
            return
        if self._in_caption:
            self._current_table["caption"] += data
            return
        if self._in_cell:
            self._cell_text.append(data)


def extract_table(html: str, *, table_index: int = 0) -> tuple[list[str], list[dict[str, str]]]:
    """Extract a basic header + row mapping from the HTML's Nth table.

    Args:
        html: Full HTML content for a wiki page.
        table_index: Zero-based index of the table to extract.

    Returns:
        A tuple of (headers, rows) where:
        - headers is the normalized header list
        - rows is a list of dictionaries keyed by headers

    Raises:
        ValueError: If no such table exists or it has no rows.
    """

    parser = _TableExtractor()
    parser.feed(html)
    if table_index < 0 or table_index >= len(parser.tables):
        raise ValueError(f"Expected table_index={table_index} but found {len(parser.tables)} tables.")

    rows: list[list[str]] = parser.tables[table_index]["rows"]
    if not rows:
        raise ValueError("Selected table contained no rows.")

    headers = rows[0]
    data_rows = rows[1:]

    normalized_headers = [normalize_whitespace(h) or f"col_{idx}" for idx, h in enumerate(headers)]
    mapped: list[dict[str, str]] = []
    for row in data_rows:
        values = row + [""] * max(0, len(normalized_headers) - len(row))
        mapped.append(dict(zip(normalized_headers, values[: len(normalized_headers)], strict=False)))
    return normalized_headers, mapped


def scrape_entity_rows(
    html: str,
    *,
    table_index: int = 0,
    name_column: str | None = None,
) -> list[ScrapedWikiRow]:
    """Scrape entity rows from a wiki HTML table.

    Args:
        html: Wiki page HTML.
        table_index: Table index to extract.
        name_column: Optional column header to use for `canonical_name`. When
            omitted, the first header is used.

    Returns:
        A list of ScrapedWikiRow entries suitable for ingestion.
    """

    headers, rows = extract_table(html, table_index=table_index)
    chosen_column = name_column or headers[0]
    scraped: list[ScrapedWikiRow] = []
    for row in rows:
        canonical_name = normalize_whitespace(row.get(chosen_column, "")) or "Unknown"
        entity_id = make_entity_id(canonical_name)
        normalized_row = {k: normalize_whitespace(v) for k, v in row.items()}
        content_hash = compute_content_hash(normalized_row)
        scraped.append(
            ScrapedWikiRow(
                canonical_name=canonical_name,
                entity_id=entity_id,
                raw_row=normalized_row,
                content_hash=content_hash,
            )
        )
    return scraped


@dataclass(frozen=True, slots=True)
class WikiIngestionSummary:
    """Summary counts for a wiki ingestion run."""

    added: int
    changed: int
    unchanged: int
    deprecated: int


def ingest_wiki_rows(
    rows: Sequence[ScrapedWikiRow],
    *,
    page_url: str,
    source_section: str,
    parse_version: str,
    write: bool,
) -> WikiIngestionSummary:
    """Ingest scraped wiki rows, versioning changes and tracking deprecations.

    Args:
        rows: Scraped rows for a single entity type and a single table.
        page_url: Source page URL.
        source_section: Stable identifier for the table/section scraped.
        parse_version: Parser version string (bump to change parsing rules).
        write: When False, compute the summary without writing to the database.

    Returns:
        A summary of added/changed/unchanged/deprecated entities.
    """

    now = timezone.now()
    seen_entity_ids = {row.entity_id for row in rows}

    existing = list(
        WikiData.objects.filter(
            page_url=page_url,
            source_section=source_section,
            parse_version=parse_version,
        ).order_by("entity_id", "-last_seen", "-first_seen", "-id")
    )
    latest_by_entity: dict[str, WikiData] = {}
    for record in existing:
        latest_by_entity.setdefault(record.entity_id, record)

    added = 0
    changed = 0
    unchanged = 0

    def apply_one(scraped: ScrapedWikiRow) -> None:
        nonlocal added, changed, unchanged

        latest = latest_by_entity.get(scraped.entity_id)
        if latest is None:
            added += 1
            if not write:
                return
            latest_by_entity[scraped.entity_id] = WikiData.objects.create(
                page_url=page_url,
                canonical_name=scraped.canonical_name,
                entity_id=scraped.entity_id,
                content_hash=scraped.content_hash,
                raw_row=scraped.raw_row,
                source_section=source_section,
                first_seen=now,
                last_seen=now,
                parse_version=parse_version,
                deprecated=False,
            )
            return

        if latest.content_hash == scraped.content_hash:
            unchanged += 1
            if not write:
                return
            fields_to_update: list[str] = []
            if latest.last_seen != now:
                latest.last_seen = now
                fields_to_update.append("last_seen")
            if latest.deprecated:
                latest.deprecated = False
                fields_to_update.append("deprecated")
            if fields_to_update:
                latest.save(update_fields=fields_to_update)
            return

        changed += 1
        if not write:
            return
        latest_by_entity[scraped.entity_id] = WikiData.objects.create(
            page_url=page_url,
            canonical_name=scraped.canonical_name,
            entity_id=scraped.entity_id,
            content_hash=scraped.content_hash,
            raw_row=scraped.raw_row,
            source_section=source_section,
            first_seen=now,
            last_seen=now,
            parse_version=parse_version,
            deprecated=False,
        )

    if write:
        with transaction.atomic():
            for scraped in rows:
                apply_one(scraped)
    else:
        for scraped in rows:
            apply_one(scraped)

    deprecated = 0
    missing_entity_ids = set(latest_by_entity.keys()) - seen_entity_ids
    if write:
        for entity_id in missing_entity_ids:
            record = latest_by_entity[entity_id]
            if not record.deprecated:
                record.deprecated = True
                record.save(update_fields=["deprecated"])
                deprecated += 1
    else:
        deprecated = len([entity_id for entity_id in missing_entity_ids if not latest_by_entity[entity_id].deprecated])

    return WikiIngestionSummary(added=added, changed=changed, unchanged=unchanged, deprecated=deprecated)

