"""Fetch and version wiki-derived data.

Phase 2.75 scope:
- fetch one table for one entity type (Cards),
- store whitespace-normalized raw strings only,
- version by content hash changes,
- support safe dry-run mode via `--check`.
"""

from __future__ import annotations

import re
import urllib.request

from django.core.management.base import BaseCommand, CommandError

from core.wiki_ingestion import (
    TableMetadata,
    find_table_indexes_by_anchor,
    ingest_wiki_rows,
    list_tables,
    scrape_entity_rows,
)


class Command(BaseCommand):
    """Fetch a single wiki table and store versioned rows.

    This command intentionally does not feed wiki data into analysis or charts.
    It exists only to capture stable, attributable inputs for later phases.
    """

    help = "Fetch a single wiki table and version it into core.WikiData."

    DEFAULT_URL = "https://the-tower-idle-tower-defense.fandom.com/wiki/Cards"
    DEFAULT_TARGET = "slots"
    PARSE_VERSION_SLOTS = "cards_v1"
    PARSE_VERSION_CARDS_LIST = "cards_list_v1"
    CARDS_LIST_ANCHOR_ID = "List_of_Cards"

    def add_arguments(self, parser) -> None:
        """Add command arguments."""

        parser.add_argument(
            "--target",
            choices=("slots", "cards_list"),
            default=self.DEFAULT_TARGET,
            help="Which table(s) to ingest from the page: slots (top table) or cards_list (List_of_Cards section tables).",
        )
        parser.add_argument(
            "--url",
            default=self.DEFAULT_URL,
            help="Wiki page URL to fetch (defaults to the Cards page).",
        )
        parser.add_argument(
            "--table-index",
            type=int,
            action="append",
            help="Zero-based index of an HTML table to scrape (repeatable). When omitted, defaults depend on --target.",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Dry-run: do not write to the database; print a diff summary only.",
        )
        parser.add_argument(
            "--write",
            action="store_true",
            help="Write changes to the database (required to persist results).",
        )

    def handle(self, *args, **options) -> str | None:
        """Run the command."""

        target: str = options["target"]
        url: str = options["url"]
        table_indexes: list[int] | None = options["table_index"]
        check: bool = options["check"]
        write: bool = options["write"]

        if check and write:
            raise CommandError("Use either --check or --write, not both.")
        if not check and not write:
            raise CommandError("Refusing to write without explicit intent; pass --check or --write.")

        html = _fetch_html(url)
        selected_indexes = _resolve_table_indexes(html, target=target, explicit_indexes=table_indexes)
        meta_by_index = {table.index: table for table in list_tables(html)}

        mode = "CHECK" if check else "WRITE"
        totals = {"added": 0, "changed": 0, "unchanged": 0, "deprecated": 0}
        for table_index in selected_indexes:
            table_meta = meta_by_index.get(table_index)
            table_label = _table_label(table_meta, fallback=f"table_{table_index}")

            if target == "cards_list":
                parse_version = self.PARSE_VERSION_CARDS_LIST
                name_column = None
                source_section = f"cards_list_{_slug(table_label)}_{table_index}"
                extra_fields = {"_wiki_table_label": table_label}
            else:
                parse_version = self.PARSE_VERSION_SLOTS
                name_column = None
                source_section = f"cards_table_{table_index}"
                extra_fields = None

            scraped = scrape_entity_rows(
                html,
                table_index=table_index,
                name_column=name_column,
                extra_fields=extra_fields,
            )
            summary = ingest_wiki_rows(
                scraped,
                page_url=url,
                source_section=source_section,
                parse_version=parse_version,
                write=write,
            )
            totals["added"] += summary.added
            totals["changed"] += summary.changed
            totals["unchanged"] += summary.unchanged
            totals["deprecated"] += summary.deprecated

            self.stdout.write(
                f"[{mode}] target={target} url={url} table_index={table_index} source_section={source_section} "
                f"parse_version={parse_version} added={summary.added} changed={summary.changed} "
                f"unchanged={summary.unchanged} deprecated={summary.deprecated}"
            )

        self.stdout.write(
            f"[{mode}] TOTAL target={target} url={url} tables={len(selected_indexes)} "
            f"added={totals['added']} changed={totals['changed']} unchanged={totals['unchanged']} "
            f"deprecated={totals['deprecated']}"
        )
        return None


def _resolve_table_indexes(html: str, *, target: str, explicit_indexes: list[int] | None) -> list[int]:
    """Resolve table indexes based on a target and optional explicit overrides."""

    if explicit_indexes:
        return explicit_indexes
    if target == "slots":
        return [0]
    if target == "cards_list":
        indexes = find_table_indexes_by_anchor(html, anchor_id=Command.CARDS_LIST_ANCHOR_ID)
        if not indexes:
            raise CommandError(
                f"No tables found for anchor #{Command.CARDS_LIST_ANCHOR_ID}. "
                "Pass one or more --table-index values to select tables explicitly."
            )
        return indexes
    raise CommandError(f"Unknown target: {target!r}")


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slug(value: str) -> str:
    """Build a stable slug used only for `source_section` identifiers."""

    return _SLUG_RE.sub("_", value.strip().lower()).strip("_") or "unknown"


def _table_label(meta: TableMetadata | None, *, fallback: str) -> str:
    """Build a user-visible label for a table from metadata."""

    if meta is None:
        return fallback
    if meta.heading:
        return meta.heading
    if meta.caption:
        return meta.caption
    if meta.anchor_id:
        return meta.anchor_id
    return fallback


def _fetch_html(url: str) -> str:
    """Fetch HTML content from a URL.

    Args:
        url: The URL to retrieve.

    Returns:
        The decoded HTML content as a string.

    Raises:
        CommandError: When the page cannot be fetched.
    """

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "theTowerStats/phase2.75 (wiki ingestion)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content_type = response.headers.get("Content-Type", "")
            charset = "utf-8"
            if "charset=" in content_type:
                charset = content_type.split("charset=", 1)[1].split(";", 1)[0].strip() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except Exception as exc:  # noqa: BLE001 - user-visible error wrapper
        raise CommandError(f"Failed to fetch wiki page: {url}") from exc
