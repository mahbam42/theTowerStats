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

from definitions.models import WikiData

_WHITESPACE_RE = re.compile(r"\s+")
_ENTITY_ID_RE = re.compile(r"[^a-z0-9]+")
_DEDUP_HEADER_RE = re.compile(r"__\d+$")
_SKIPPABLE_CELL_RE = re.compile(r"^(?:-|—|–|null|none)?$", re.IGNORECASE)


def _is_skippable_cell(value: str) -> bool:
    """Return True when a cell value is non-informational for ingestion.

    Args:
        value: A whitespace-normalized cell value.

    Returns:
        True when the value is empty/placeholder (ex: "", "-", "null").
    """

    return _SKIPPABLE_CELL_RE.match(value.strip()) is not None


def _should_skip_scraped_row(row: ScrapedWikiRow) -> bool:
    """Return True when a scraped row should be ignored.

    The wiki sometimes includes non-entity summary rows such as "Total", or rows
    that are effectively empty placeholders. These are ignored during ingestion
    to avoid creating noisy revisions and false drift.

    Rules (conservative):
    - Skip when canonical_name is "total" or a placeholder.
    - Skip when all non-metadata cell values are placeholders.
    - Skip when any cell is "total" and every other cell is a placeholder.
    """

    canonical = normalize_whitespace(row.canonical_name).casefold()
    if canonical == "total" or _is_skippable_cell(canonical):
        return True

    values: list[str] = []
    for key, value in row.raw_row.items():
        if str(key).startswith("_"):
            continue
        values.append(normalize_whitespace(str(value)))

    if not values:
        return True
    if all(_is_skippable_cell(value) for value in values):
        return True

    has_total = any(value.casefold() == "total" for value in values)
    if has_total and all(_is_skippable_cell(value) or value.casefold() == "total" for value in values):
        return True
    return False


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


@dataclass(frozen=True, slots=True)
class TableMetadata:
    """Metadata for an extracted HTML table.

    Attributes:
        index: Zero-based index of the table in document order.
        anchor_id: Closest mw-headline anchor id preceding the table, if any.
        section_anchor_id: Closest section (h2) anchor id preceding the table, if any.
        heading: Closest heading text (h2/h3/h4) preceding the table, if any.
        caption: Table caption text, if any.
    """

    index: int
    anchor_id: str | None
    section_anchor_id: str | None
    heading: str
    caption: str


class _TableExtractor(HTMLParser):
    """Minimal HTML table extractor for wiki pages.

    This intentionally supports only a subset of HTML needed to pull basic
    tables and does not attempt to preserve markup.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[dict[str, Any]] = []
        self._current_anchor_id: str | None = None
        self._current_heading_text = ""
        self._current_section_anchor_id: str | None = None
        self._current_section_heading_text = ""
        self._in_table = False
        self._in_caption = False
        self._in_row = False
        self._in_cell = False
        self._in_heading = False
        self._heading_level: int | None = None
        self._cell_text: list[str] = []
        self._current_table: dict[str, Any] | None = None
        self._current_row: list[str] | None = None
        self._heading_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key: value for key, value in attrs}
        if tag == "span":
            span_id = attrs_dict.get("id")
            span_class = attrs_dict.get("class") or ""
            if span_id and "mw-headline" in span_class.split():
                self._current_anchor_id = span_id
                if self._in_heading and self._heading_level == 2:
                    self._current_section_anchor_id = span_id

        if tag in {"h2", "h3", "h4"}:
            self._in_heading = True
            self._heading_level = int(tag[1])
            self._heading_text = []

        if tag == "table":
            self._in_table = True
            self._current_table = {
                "caption": "",
                "rows": [],
                "anchor_id": self._current_anchor_id,
                "section_anchor_id": self._current_section_anchor_id,
                "heading": self._current_heading_text,
                "section_heading": self._current_section_heading_text,
            }
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
        if tag in {"h2", "h3", "h4"} and self._in_heading:
            self._in_heading = False
            self._current_heading_text = normalize_whitespace("".join(self._heading_text))
            if self._heading_level == 2:
                self._current_section_heading_text = self._current_heading_text
            self._heading_text = []
            self._heading_level = None
            return

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
        if self._in_heading:
            self._heading_text.append(data)
            return

        if not self._in_table or self._current_table is None:
            return
        if self._in_caption:
            self._current_table["caption"] += data
            return
        if self._in_cell:
            self._cell_text.append(data)


def list_tables(html: str) -> list[TableMetadata]:
    """List tables available in an HTML page with simple section metadata.

    Args:
        html: Full HTML content for a wiki page.

    Returns:
        A list of TableMetadata entries in document order.
    """

    parser = _TableExtractor()
    parser.feed(html)
    tables: list[TableMetadata] = []
    for idx, table in enumerate(parser.tables):
        tables.append(
            TableMetadata(
                index=idx,
                anchor_id=table.get("anchor_id"),
                section_anchor_id=table.get("section_anchor_id"),
                heading=normalize_whitespace(table.get("heading", "")),
                caption=normalize_whitespace(table.get("caption", "")),
            )
        )
    return tables


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

    normalized_headers = _dedupe_headers([normalize_whitespace(h) or f"col_{idx}" for idx, h in enumerate(headers)])
    mapped: list[dict[str, str]] = []
    for row in data_rows:
        values = row + [""] * max(0, len(normalized_headers) - len(row))
        mapped.append(dict(zip(normalized_headers, values[: len(normalized_headers)], strict=False)))
    return normalized_headers, mapped


def _dedupe_headers(headers: Sequence[str]) -> list[str]:
    """Make table headers unique while preserving order.

    Wiki tables sometimes include repeated column labels (ex: multiple "Cost" or
    "Bits" columns). A naive mapping would overwrite earlier values.

    Args:
        headers: Header labels in document order.

    Returns:
        A list of unique header labels where repeated labels are suffixed with
        `__2`, `__3`, ... deterministically.
    """

    seen: dict[str, int] = {}
    unique: list[str] = []
    for header in headers:
        base = _DEDUP_HEADER_RE.sub("", header)
        count = seen.get(base, 0) + 1
        seen[base] = count
        unique.append(base if count == 1 else f"{base}__{count}")
    return unique


def scrape_leveled_entity_rows(
    html: str,
    *,
    table_index: int,
    entity_name: str,
    entity_id: str,
    entity_field: str,
    level_field: str = "Level",
    star_field: str = "Star",
    add_level_if_missing: bool = False,
    header_aliases: Mapping[str, str] | None = None,
    extra_fields: Mapping[str, str] | None = None,
) -> list[ScrapedWikiRow]:
    """Scrape a table containing many levels for a single entity.

    Many wiki pages store per-level values in a table where each row represents
    a level (or star tier) for a single entity (bot, guardian chip, ultimate
    weapon). These tables often do not include an entity name column, and some
    omit a `Level` column entirely (implicit level-by-row).

    This helper:
    - injects a stable entity identifier via `_wiki_entity_id`,
    - injects `entity_field` (ex: "Bot") so downstream population can resolve
      names consistently,
    - optionally adds an implicit `level_field` when missing,
    - optionally adds alias keys for headers (without removing raw headers),
    - assigns a composite `ScrapedWikiRow.entity_id` per (entity, level, star)
      so ingestion versions each row independently.

    Args:
        html: Wiki page HTML.
        table_index: Table index to extract.
        entity_name: Human-readable entity name (ex: "Amplify Bot").
        entity_id: Stable base identifier for the entity (ex: "amplify_bot").
        entity_field: Key injected into each raw_row (ex: "Bot").
        level_field: Column name used to represent level.
        star_field: Column name used to represent star/tier.
        add_level_if_missing: When True, add `level_field` as a 1-based row
            index if missing from the extracted table.
        header_aliases: Optional mapping of `{raw_header: alias_header}` to add
            alias keys while preserving the original header.
        extra_fields: Optional additional key/value pairs to merge into each
            row before hashing.

    Returns:
        A list of ScrapedWikiRow entries suitable for ingestion.
    """

    _, rows = extract_table(html, table_index=table_index)
    normalized_extras = {k: normalize_whitespace(v) for k, v in (extra_fields or {}).items()}
    aliases = header_aliases or {}

    scraped: list[ScrapedWikiRow] = []
    for idx, row in enumerate(rows, start=1):
        normalized_row = {k: normalize_whitespace(v) for k, v in row.items()}
        normalized_row.update(normalized_extras)
        normalized_row.setdefault("_wiki_entity_id", entity_id)
        normalized_row.setdefault(entity_field, entity_name)

        if add_level_if_missing and level_field not in normalized_row:
            normalized_row[level_field] = str(idx)

        for raw_header, alias_header in aliases.items():
            if raw_header in normalized_row and alias_header not in normalized_row:
                normalized_row[alias_header] = normalized_row[raw_header]

        level_value = normalize_whitespace(normalized_row.get(level_field, ""))
        star_value = normalize_whitespace(normalized_row.get(star_field, ""))
        composite_id = _composite_level_entity_id(entity_id, level_value, star_value)
        content_hash = compute_content_hash(normalized_row)
        scraped.append(
            ScrapedWikiRow(
                canonical_name=normalize_whitespace(entity_name) or "Unknown",
                entity_id=composite_id,
                raw_row=normalized_row,
                content_hash=content_hash,
            )
        )
    return scraped


def _composite_level_entity_id(entity_id: str, level_raw: str, star_raw: str) -> str:
    """Build a stable row-level identity for (entity, level, star).

    Args:
        entity_id: Base entity identifier.
        level_raw: Raw level string (already whitespace-normalized).
        star_raw: Raw star string (already whitespace-normalized).

    Returns:
        A composite identifier suitable for per-row ingestion versioning.
    """

    level_key = level_raw or "unknown"
    star_key = star_raw or "none"
    return f"{entity_id}__level_{level_key}__star_{star_key}"


def scrape_entity_rows(
    html: str,
    *,
    table_index: int = 0,
    name_column: str | None = None,
    extra_fields: Mapping[str, str] | None = None,
) -> list[ScrapedWikiRow]:
    """Scrape entity rows from a wiki HTML table.

    Args:
        html: Wiki page HTML.
        table_index: Table index to extract.
        name_column: Optional column header to use for `canonical_name`. When
            omitted, the first header is used.
        extra_fields: Optional extra key/value pairs to merge into each row
            before hashing and ingestion.

    Returns:
        A list of ScrapedWikiRow entries suitable for ingestion.
    """

    headers, rows = extract_table(html, table_index=table_index)
    if name_column is not None:
        chosen_column = name_column
    elif "Name" in headers:
        chosen_column = "Name"
    elif "Card" in headers:
        chosen_column = "Card"
    else:
        chosen_column = headers[0]
    normalized_extras = {k: normalize_whitespace(v) for k, v in (extra_fields or {}).items()}
    scraped: list[ScrapedWikiRow] = []
    for row in rows:
        canonical_name = normalize_whitespace(row.get(chosen_column, "")) or "Unknown"
        entity_id = make_entity_id(canonical_name)
        normalized_row = {k: normalize_whitespace(v) for k, v in row.items()}
        normalized_row.update(normalized_extras)
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


def find_table_indexes_by_anchor(html: str, *, anchor_id: str) -> list[int]:
    """Find table indexes that belong to a section anchor.

    Args:
        html: Full HTML content for a wiki page.
        anchor_id: The mw-headline id to match (e.g., "List_of_Cards").

    Returns:
        A list of matching table indexes (may be empty).
    """

    tables = list_tables(html)
    by_section = [table.index for table in tables if table.section_anchor_id == anchor_id]
    if by_section:
        return by_section
    return [table.index for table in tables if table.anchor_id == anchor_id]


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
    filtered_rows = [row for row in rows if not _should_skip_scraped_row(row)]
    seen_entity_ids = {row.entity_id for row in filtered_rows}

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
            for scraped in filtered_rows:
                apply_one(scraped)
    else:
        for scraped in filtered_rows:
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
