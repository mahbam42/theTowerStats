"""Fetch and version wiki-derived data.

Phase 2.75 scope:
- fetch one table for one entity type (Cards),
- store whitespace-normalized raw strings only,
- version by content hash changes,
- support safe dry-run mode via `--check`.
"""

from __future__ import annotations

import urllib.request

from django.core.management.base import BaseCommand, CommandError

from core.wiki_ingestion import ingest_wiki_rows, scrape_entity_rows


class Command(BaseCommand):
    """Fetch a single wiki table and store versioned rows.

    This command intentionally does not feed wiki data into analysis or charts.
    It exists only to capture stable, attributable inputs for later phases.
    """

    help = "Fetch a single wiki table and version it into core.WikiData."

    DEFAULT_URL = "https://the-tower-idle-tower-defense.fandom.com/wiki/Cards"
    DEFAULT_TABLE_INDEX = 0
    DEFAULT_SOURCE_SECTION = "cards_table_0"
    PARSE_VERSION = "cards_v1"

    def add_arguments(self, parser) -> None:
        """Add command arguments."""

        parser.add_argument(
            "--url",
            default=self.DEFAULT_URL,
            help="Wiki page URL to fetch (defaults to the Cards page).",
        )
        parser.add_argument(
            "--table-index",
            type=int,
            default=self.DEFAULT_TABLE_INDEX,
            help="Zero-based index of the HTML table to scrape.",
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

        url: str = options["url"]
        table_index: int = options["table_index"]
        check: bool = options["check"]
        write: bool = options["write"]

        if check and write:
            raise CommandError("Use either --check or --write, not both.")
        if not check and not write:
            raise CommandError("Refusing to write without explicit intent; pass --check or --write.")

        html = _fetch_html(url)
        scraped = scrape_entity_rows(html, table_index=table_index, name_column=None)
        summary = ingest_wiki_rows(
            scraped,
            page_url=url,
            source_section=f"cards_table_{table_index}",
            parse_version=self.PARSE_VERSION,
            write=write,
        )

        mode = "CHECK" if check else "WRITE"
        self.stdout.write(
            f"[{mode}] url={url} table_index={table_index} parse_version={self.PARSE_VERSION} "
            f"added={summary.added} changed={summary.changed} unchanged={summary.unchanged} "
            f"deprecated={summary.deprecated}"
        )
        return None


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

