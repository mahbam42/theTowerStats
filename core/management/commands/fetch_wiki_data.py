"""Fetch and version wiki-derived data.

This command fetches selected wiki pages and versions extracted table rows into
`core.WikiData` for later offline population steps.

Design goals:
- store whitespace-normalized raw strings only,
- version by deterministic content hashes (no overwrites),
- support safe dry-run mode via `--check`,
- keep parsing strict but resilient to wiki layout changes.
"""

from __future__ import annotations

import re
import urllib.request

from django.core.management.base import BaseCommand, CommandError

from core.wiki_ingestion import (
    ScrapedWikiRow,
    TableMetadata,
    extract_table,
    find_table_indexes_by_anchor,
    ingest_wiki_rows,
    list_tables,
    make_entity_id,
    scrape_entity_rows,
    scrape_leveled_entity_rows,
)


class Command(BaseCommand):
    """Fetch a single wiki table and store versioned rows.

    This command intentionally does not feed wiki data into analysis or charts.
    It exists only to capture stable, attributable inputs for later phases.
    """

    help = "Fetch a single wiki table and version it into core.WikiData."

    DEFAULT_CARDS_URL = "https://the-tower-idle-tower-defense.fandom.com/wiki/Cards"
    DEFAULT_GUARDIAN_URL = "https://the-tower-idle-tower-defense.fandom.com/wiki/Guardian"
    DEFAULT_UW_INDEX_URL = "https://the-tower-idle-tower-defense.fandom.com/wiki/Ultimate_Weapons"
    DEFAULT_TARGET = "slots"
    PARSE_VERSION_SLOTS = "cards_v1"
    PARSE_VERSION_CARDS_LIST = "cards_list_v1"
    PARSE_VERSION_BOTS = "bots_v1"
    PARSE_VERSION_GUARDIAN_CHIPS = "guardian_chips_v1"
    PARSE_VERSION_ULTIMATE_WEAPONS = "ultimate_weapons_v1"
    CARDS_LIST_ANCHOR_ID = "List_of_Cards"

    BOT_PAGES: tuple[tuple[str, str], ...] = (
        ("Amplify Bot", "https://the-tower-idle-tower-defense.fandom.com/wiki/Amplify_Bot"),
        ("Flame Bot", "https://the-tower-idle-tower-defense.fandom.com/wiki/Flame_Bot"),
        ("Thunder Bot", "https://the-tower-idle-tower-defense.fandom.com/wiki/Thunder_Bot"),
        ("Golden Bot", "https://the-tower-idle-tower-defense.fandom.com/wiki/Golden_Bot"),
    )

    UW_PAGES: tuple[tuple[str, str], ...] = (
        ("Chain Lightning", "https://the-tower-idle-tower-defense.fandom.com/wiki/Chain_Lightning"),
        ("Smart Missiles", "https://the-tower-idle-tower-defense.fandom.com/wiki/Smart_Missiles"),
        ("Death Wave", "https://the-tower-idle-tower-defense.fandom.com/wiki/Death_Wave"),
        ("Chrono Field", "https://the-tower-idle-tower-defense.fandom.com/wiki/Chrono_Field"),
        ("Inner Land Mines", "https://the-tower-idle-tower-defense.fandom.com/wiki/Inner_Land_Mines"),
        ("Golden Tower", "https://the-tower-idle-tower-defense.fandom.com/wiki/Golden_Tower"),
        ("Poison Swamp", "https://the-tower-idle-tower-defense.fandom.com/wiki/Poison_Swamp"),
        ("Black Hole", "https://the-tower-idle-tower-defense.fandom.com/wiki/Black_Hole"),
        ("Spotlight", "https://the-tower-idle-tower-defense.fandom.com/wiki/Spotlight"),
    )

    def add_arguments(self, parser) -> None:
        """Add command arguments."""

        parser.add_argument(
            "--target",
            choices=("slots", "cards_list", "bots", "guardian_chips", "ultimate_weapons"),
            default=self.DEFAULT_TARGET,
            help=(
                "Which table(s) to ingest from the page: "
                "slots (top Cards table), cards_list (tables under #List_of_Cards), "
                "bots (bot upgrade tables), guardian_chips (Guardian chip tables), "
                "ultimate_weapons (ultimate weapon upgrade tables)."
            ),
        )
        parser.add_argument(
            "--url",
            default=None,
            help="Wiki page URL to fetch (defaults depend on --target).",
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
        url: str | None = options["url"]
        table_indexes: list[int] | None = options["table_index"]
        check: bool = options["check"]
        write: bool = options["write"]

        if check and write:
            raise CommandError("Use either --check or --write, not both.")
        if not check and not write:
            raise CommandError("Refusing to write without explicit intent; pass --check or --write.")

        mode = "CHECK" if check else "WRITE"
        totals = {"added": 0, "changed": 0, "unchanged": 0, "deprecated": 0}
        specs_by_url: dict[str, list[_IngestionSpec]] = {}
        for page_url, spec in _iter_ingestion_specs(target=target, url_override=url):
            specs_by_url.setdefault(page_url, []).append(spec)

        for page_url, specs in specs_by_url.items():
            html = _fetch_html(page_url)
            meta_by_index = {table.index: table for table in list_tables(html)}

            for spec in specs:
                selected_indexes = _resolve_table_indexes(
                    html,
                    target=target,
                    explicit_indexes=table_indexes,
                    spec=spec,
                )
                for table_index in selected_indexes:
                    table_meta = meta_by_index.get(table_index)
                    table_label = _table_label(table_meta, fallback=f"table_{table_index}")

                    scraped, parse_version, source_section = _scrape_for_spec(
                        html,
                        table_index=table_index,
                        table_label=table_label,
                        spec=spec,
                    )
                    summary = ingest_wiki_rows(
                        scraped,
                        page_url=page_url,
                        source_section=source_section,
                        parse_version=parse_version,
                        write=write,
                    )
                    totals["added"] += summary.added
                    totals["changed"] += summary.changed
                    totals["unchanged"] += summary.unchanged
                    totals["deprecated"] += summary.deprecated

                    self.stdout.write(
                        f"[{mode}] target={target} url={page_url} table_index={table_index} source_section={source_section} "
                        f"parse_version={parse_version} added={summary.added} changed={summary.changed} "
                        f"unchanged={summary.unchanged} deprecated={summary.deprecated}"
                    )

        self.stdout.write(
            f"[{mode}] TOTAL target={target} tables=* "
            f"added={totals['added']} changed={totals['changed']} unchanged={totals['unchanged']} "
            f"deprecated={totals['deprecated']}"
        )
        return None


def _resolve_table_indexes(
    html: str, *, target: str, explicit_indexes: list[int] | None, spec: "_IngestionSpec"
) -> list[int]:
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
    if target == "bots":
        return _find_table_indexes_with_headers(html, required={"Level", "Cost"})
    if target == "ultimate_weapons":
        indexes = _find_table_indexes_with_header_substrings(
            html,
            required_substrings={"Stones"},
            require_min_non_matching_headers=2,
        )
        return indexes
    if target == "guardian_chips":
        if spec.section_anchor_id is None:
            raise CommandError("Internal error: guardian_chips spec missing section_anchor_id.")
        indexes = find_table_indexes_by_anchor(html, anchor_id=spec.section_anchor_id)
        if not indexes:
            raise CommandError(
                f"No tables found for anchor #{spec.section_anchor_id}. "
                "Pass one or more --table-index values to select tables explicitly."
            )
        candidate = _filter_tables_by_any_headers(html, indexes=indexes, required_any={"Bits", "Cooldown", "Recovery"})
        return candidate or indexes
    raise CommandError(f"Unknown target: {target!r}")


def _find_table_indexes_with_headers(html: str, *, required: set[str]) -> list[int]:
    """Return table indexes that include all required headers."""

    indexes: list[int] = []
    for meta in list_tables(html):
        try:
            headers, _ = extract_table(html, table_index=meta.index)
        except ValueError:
            continue
        if required.issubset(set(headers)):
            indexes.append(meta.index)
    return indexes


def _find_table_indexes_with_header_substrings(
    html: str, *, required_substrings: set[str], require_min_non_matching_headers: int = 0
) -> list[int]:
    """Return table indexes that include all required header substrings.

    Args:
        html: Source HTML.
        required_substrings: Substrings that must appear in at least one header.
        require_min_non_matching_headers: Require at least this many headers
            that do *not* match any of the substrings (helps avoid transposed
            "level-as-columns" tables).
    """

    indexes: list[int] = []
    for meta in list_tables(html):
        try:
            headers, _ = extract_table(html, table_index=meta.index)
        except ValueError:
            continue
        if not all(any(token in header for header in headers) for token in required_substrings):
            continue
        non_matching = [
            header for header in headers if not any(token in header for token in required_substrings)
        ]
        if len(non_matching) < require_min_non_matching_headers:
            continue
        indexes.append(meta.index)
    return indexes


def _filter_tables_by_any_headers(
    html: str, *, indexes: list[int], required_any: set[str]
) -> list[int]:
    """Filter a set of candidate table indexes by requiring at least one matching header substring."""

    selected: list[int] = []
    for idx in indexes:
        try:
            headers, _ = extract_table(html, table_index=idx)
        except ValueError:
            continue
        if any(any(token in header for token in required_any) for header in headers):
            selected.append(idx)
    return selected


class _IngestionSpec:
    """Target-specific scrape configuration for one page (and optional section)."""

    def __init__(
        self,
        *,
        kind: str,
        parse_version: str,
        source_prefix: str,
        entity_name: str | None = None,
        entity_field: str | None = None,
        entity_id: str | None = None,
        add_level_if_missing: bool = False,
        header_aliases: dict[str, str] | None = None,
        section_anchor_id: str | None = None,
        wiki_table_label: str | None = None,
    ) -> None:
        self.kind = kind
        self.parse_version = parse_version
        self.source_prefix = source_prefix
        self.entity_name = entity_name
        self.entity_field = entity_field
        self.entity_id = entity_id
        self.add_level_if_missing = add_level_if_missing
        self.header_aliases = header_aliases or {}
        self.section_anchor_id = section_anchor_id
        self.wiki_table_label = wiki_table_label


def _iter_ingestion_specs(*, target: str, url_override: str | None) -> list[tuple[str, _IngestionSpec]]:
    """Build page+spec entries for the requested target."""

    if target in {"slots", "cards_list"}:
        url = url_override or Command.DEFAULT_CARDS_URL
        kind = "cards_list" if target == "cards_list" else "slots"
        source_prefix = "cards_list" if target == "cards_list" else "cards_table"
        parse_version = Command.PARSE_VERSION_CARDS_LIST if target == "cards_list" else Command.PARSE_VERSION_SLOTS
        return [(url, _IngestionSpec(kind=kind, parse_version=parse_version, source_prefix=source_prefix))]

    if target == "bots":
        if url_override:
            name = _name_from_url(url_override)
            return [
                (
                    url_override,
                    _IngestionSpec(
                        kind="leveled_entity",
                        parse_version=Command.PARSE_VERSION_BOTS,
                        source_prefix=f"bots_{_slug(make_entity_id(name))}",
                        entity_name=name,
                        entity_field="Bot",
                        entity_id=make_entity_id(name),
                    ),
                )
            ]
        specs: list[tuple[str, _IngestionSpec]] = []
        for name, page_url in Command.BOT_PAGES:
            specs.append(
                (
                    page_url,
                    _IngestionSpec(
                        kind="leveled_entity",
                        parse_version=Command.PARSE_VERSION_BOTS,
                        source_prefix=f"bots_{_slug(make_entity_id(name))}",
                        entity_name=name,
                        entity_field="Bot",
                        entity_id=make_entity_id(name),
                    ),
                )
            )
        return specs

    if target == "ultimate_weapons":
        if url_override and url_override != Command.DEFAULT_UW_INDEX_URL:
            name = _name_from_url(url_override)
            return [
                (
                    url_override,
                    _IngestionSpec(
                        kind="leveled_entity",
                        parse_version=Command.PARSE_VERSION_ULTIMATE_WEAPONS,
                        source_prefix=f"ultimate_weapons_{_slug(make_entity_id(name))}",
                        entity_name=name,
                        entity_field="Ultimate Weapon",
                        entity_id=make_entity_id(name),
                        add_level_if_missing=True,
                        header_aliases={
                            "Cooldown (s)": "Cooldown",
                            "Cooldown(s)": "Cooldown",
                        },
                    ),
                )
            ]
        specs = []
        for name, page_url in Command.UW_PAGES:
            specs.append(
                (
                    page_url,
                    _IngestionSpec(
                        kind="leveled_entity",
                        parse_version=Command.PARSE_VERSION_ULTIMATE_WEAPONS,
                        source_prefix=f"ultimate_weapons_{_slug(make_entity_id(name))}",
                        entity_name=name,
                        entity_field="Ultimate Weapon",
                        entity_id=make_entity_id(name),
                        add_level_if_missing=True,
                        header_aliases={
                            "Cooldown (s)": "Cooldown",
                            "Cooldown(s)": "Cooldown",
                        },
                    ),
                )
            )
        return specs

    if target == "guardian_chips":
        guardian_url = url_override or Command.DEFAULT_GUARDIAN_URL
        html = _fetch_html(guardian_url)
        section_ids = _guardian_chip_section_ids(html)
        if not section_ids:
            raise CommandError("No guardian chip sections found (expected headings ending in '_Chip').")
        specs = []
        for section_id in section_ids:
            chip_name = _chip_name_from_section_id(section_id)
            chip_id = make_entity_id(chip_name)
            specs.append(
                (
                    guardian_url,
                    _IngestionSpec(
                        kind="leveled_entity",
                        parse_version=Command.PARSE_VERSION_GUARDIAN_CHIPS,
                        source_prefix=f"guardian_chips_{_slug(chip_id)}",
                        entity_name=chip_name,
                        entity_field="Guardian",
                        entity_id=chip_id,
                        add_level_if_missing=True,
                        header_aliases={
                            "Cooldown (s)": "Cooldown",
                            "Cooldown(s)": "Cooldown",
                            "Max Recovey": "Max Recovery",
                            "Max Recovery": "Max Recovery",
                        },
                        section_anchor_id=section_id,
                    ),
                )
            )
        return specs

    raise CommandError(f"Unknown target: {target!r}")


def _scrape_for_spec(
    html: str, *, table_index: int, table_label: str, spec: _IngestionSpec
) -> tuple[list[ScrapedWikiRow], str, str]:
    """Scrape rows for one (html, table_index) using a spec."""

    if spec.kind in {"slots", "cards_list"}:
        if spec.kind == "cards_list":
            source_section = f"{spec.source_prefix}_{_slug(table_label)}_{table_index}"
            scraped = scrape_entity_rows(
                html,
                table_index=table_index,
                name_column=None,
                extra_fields={"_wiki_table_label": table_label},
            )
        else:
            source_section = f"{spec.source_prefix}_{table_index}"
            scraped = scrape_entity_rows(html, table_index=table_index, name_column=None)
        return scraped, spec.parse_version, source_section

    if spec.kind == "leveled_entity":
        if not spec.entity_name or not spec.entity_field or not spec.entity_id:
            raise CommandError("Internal error: leveled_entity spec missing entity metadata.")
        source_section = f"{spec.source_prefix}_table_{table_index}"
        scraped = scrape_leveled_entity_rows(
            html,
            table_index=table_index,
            entity_name=spec.entity_name,
            entity_id=spec.entity_id,
            entity_field=spec.entity_field,
            add_level_if_missing=spec.add_level_if_missing,
            header_aliases=spec.header_aliases,
        )
        return scraped, spec.parse_version, source_section

    raise CommandError(f"Internal error: unknown spec kind: {spec.kind!r}")


_CHIP_SECTION_RE = re.compile(r'<span\s+class="mw-headline"\s+id="([^"]+_Chip)"')


def _guardian_chip_section_ids(html: str) -> list[str]:
    """Return Guardian chip section headline ids (ex: Ally_Chip)."""

    seen: set[str] = set()
    ordered: list[str] = []
    for match in _CHIP_SECTION_RE.finditer(html):
        section_id = match.group(1)
        if section_id not in seen:
            seen.add(section_id)
            ordered.append(section_id)
    return ordered


def _chip_name_from_section_id(section_id: str) -> str:
    """Convert a wiki section id like 'Ally_Chip' into a display name."""

    return section_id.replace("_Chip", "").replace("_", " ").strip() or section_id


def _name_from_url(url: str) -> str:
    """Best-effort conversion from a wiki URL slug to a human-readable name."""

    tail = url.rstrip("/").rsplit("/", 1)[-1]
    return tail.replace("_", " ").strip() or tail


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
