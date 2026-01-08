"""Rebuild wiki-derived definition tables (Definitions layer).

This command orchestrates:
1) wiki ingestion into `definitions.WikiData` (optional, online), then
2) offline translation into structured definition + parameter tables.

It must not delete Player State or GameData rows.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from core.management.commands import fetch_wiki_data
from core.wiki_ingestion import _should_skip_scraped_row
from definitions.models import WikiData
from definitions.wiki_rebuild import (
    rebuild_bots_from_wikidata,
    rebuild_cards_from_wikidata,
    rebuild_guardian_chips_from_wikidata,
    rebuild_ultimate_weapons_from_wikidata,
)


@dataclass(frozen=True, slots=True)
class _DiffRow:
    """Represents a single field-level diff for wiki rows."""

    entity_id: str
    field: str
    previous: str
    new: str
    status: str


@dataclass(frozen=True, slots=True)
class _DiffGroup:
    """Collects diff rows for a single source section."""

    target: str
    page_url: str
    source_section: str
    parse_version: str
    rows: tuple[_DiffRow, ...]
    added: int
    changed: int
    unchanged: int
    deprecated: int


class Command(BaseCommand):
    """Rebuild Definitions and parameter tables from wiki sources."""

    help = "Rebuild wiki-derived definitions and parameter tables."

    def add_arguments(self, parser) -> None:
        """Add command arguments."""

        parser.add_argument(
            "--target",
            choices=("cards", "bots", "guardians", "ultimate_weapons", "all"),
            default="all",
            help="Which definitions to rebuild.",
        )
        parser.add_argument(
            "--skip-fetch",
            action="store_true",
            help="Skip network wiki ingestion; rebuild only from existing WikiData (offline).",
        )
        parser.add_argument(
            "--diffs",
            action="store_true",
            help=(
                "Preview field-level diffs by fetching live wiki data without writing. "
                "This ignores --skip-fetch and does not rebuild definitions."
            ),
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Dry-run: do not write to the database; print summaries only.",
        )
        parser.add_argument(
            "--write",
            action="store_true",
            help="Write changes to the database (required to persist results).",
        )

    def handle(self, *args, **options) -> str | None:
        """Run the command."""

        target: str = options["target"]
        skip_fetch: bool = options["skip_fetch"]
        diffs: bool = options["diffs"]
        check: bool = options["check"]
        write: bool = options["write"]

        if diffs and write:
            raise CommandError("--diffs cannot be combined with --write.")
        if check and write:
            raise CommandError("Use either --check or --write, not both.")
        if not check and not write and not diffs:
            raise CommandError("Refusing to write without explicit intent; pass --check or --write.")

        if diffs:
            self.stdout.write("[DIFFS] fetching WikiData for preview...")
            self._diffs(target=target)
            return None

        mode = "CHECK" if check else "WRITE"
        if not skip_fetch:
            self.stdout.write(f"[{mode}] fetching WikiData...")
            self._fetch(target=target, write=write)

        self.stdout.write(f"[{mode}] rebuilding definitions from WikiData...")
        rebuilders = {
            "cards": rebuild_cards_from_wikidata,
            "bots": rebuild_bots_from_wikidata,
            "guardians": rebuild_guardian_chips_from_wikidata,
            "ultimate_weapons": rebuild_ultimate_weapons_from_wikidata,
        }
        selected = list(rebuilders.keys()) if target == "all" else [target]
        for key in selected:
            summary = rebuilders[key](write=write)
            self.stdout.write(f"[{mode}] rebuilt={key} summary={summary}")

        return None

    def _fetch(self, *, target: str, write: bool) -> None:
        """Ingest wiki pages into WikiData prior to rebuilding."""

        check = not write
        if target in {"cards", "all"}:
            call_command("fetch_wiki_data", target="slots", check=check, write=write)
            call_command("fetch_wiki_data", target="cards_list", check=check, write=write)
        if target in {"bots", "all"}:
            call_command("fetch_wiki_data", target="bots", check=check, write=write)
        if target in {"guardians", "all"}:
            call_command("fetch_wiki_data", target="guardian_chips", check=check, write=write)
        if target in {"ultimate_weapons", "all"}:
            call_command("fetch_wiki_data", target="ultimate_weapons", check=check, write=write)

    def _diffs(self, *, target: str) -> None:
        """Fetch wiki pages and print field-level diffs without writing."""

        totals = {"added": 0, "changed": 0, "unchanged": 0, "deprecated": 0}
        fetch_targets = _fetch_targets_for_rebuild(target)
        for fetch_target in fetch_targets:
            groups = _diff_target(fetch_target)
            for group in groups:
                if not group.rows:
                    self.stdout.write(
                        f"[DIFFS] target={group.target} page_url={group.page_url} "
                        f"source_section={group.source_section} parse_version={group.parse_version} "
                        "no changes detected"
                    )
                else:
                    self.stdout.write(
                        f"[DIFFS] target={group.target} page_url={group.page_url} "
                        f"source_section={group.source_section} parse_version={group.parse_version}"
                    )
                    for line in _render_diff_table(group.rows):
                        self.stdout.write(line)
                totals["added"] += group.added
                totals["changed"] += group.changed
                totals["unchanged"] += group.unchanged
                totals["deprecated"] += group.deprecated

            self.stdout.write(
                f"[DIFFS] TOTAL target={fetch_target} tables=* added={sum(g.added for g in groups)} "
                f"changed={sum(g.changed for g in groups)} unchanged={sum(g.unchanged for g in groups)} "
                f"deprecated={sum(g.deprecated for g in groups)}"
            )

        self.stdout.write(
            f"[DIFFS] TOTAL target={target} tables=* added={totals['added']} changed={totals['changed']} "
            f"unchanged={totals['unchanged']} deprecated={totals['deprecated']}"
        )


def _fetch_targets_for_rebuild(target: str) -> tuple[str, ...]:
    """Map rebuild targets to fetch_wiki_data targets."""

    mapping = {
        "cards": ("slots", "cards_list"),
        "bots": ("bots",),
        "guardians": ("guardian_chips",),
        "ultimate_weapons": ("ultimate_weapons",),
        "all": ("slots", "cards_list", "bots", "guardian_chips", "ultimate_weapons"),
    }
    return mapping[target]


def _diff_target(target: str) -> list[_DiffGroup]:
    """Fetch and diff wiki rows for a single fetch_wiki_data target."""

    specs_by_url: dict[str, list[fetch_wiki_data._IngestionSpec]] = {}
    for page_url, spec in fetch_wiki_data._iter_ingestion_specs(target=target, url_override=None):
        specs_by_url.setdefault(page_url, []).append(spec)

    groups: list[_DiffGroup] = []
    for page_url, specs in specs_by_url.items():
        html = fetch_wiki_data._fetch_html(page_url)
        meta_by_index = {table.index: table for table in fetch_wiki_data.list_tables(html)}
        for spec in specs:
            table_indexes = fetch_wiki_data._resolve_table_indexes(
                html,
                target=spec.target,
                explicit_indexes=None,
                spec=spec,
            )
            for table_index in table_indexes:
                table_meta = meta_by_index.get(table_index)
                table_label = fetch_wiki_data._table_label(table_meta, fallback=f"table_{table_index}")
                scraped, parse_version, source_section = fetch_wiki_data._scrape_for_spec(
                    html,
                    table_index=table_index,
                    table_label=table_label,
                    spec=spec,
                )
                group = _diff_scraped_rows(
                    target=target,
                    page_url=page_url,
                    source_section=source_section,
                    parse_version=parse_version,
                    scraped=scraped,
                    header_aliases=spec.header_aliases,
                )
                groups.append(group)
    return groups


def _diff_scraped_rows(
    *,
    target: str,
    page_url: str,
    source_section: str,
    parse_version: str,
    scraped: list[fetch_wiki_data.ScrapedWikiRow],
    header_aliases: dict[str, str],
) -> _DiffGroup:
    """Compare scraped rows to stored WikiData and return diff rows."""

    latest_by_entity = _latest_wikidata_by_entity(
        page_url=page_url,
        source_section=source_section,
        parse_version=parse_version,
    )
    filtered_rows = [row for row in scraped if not _should_skip_scraped_row(row)]
    seen_entity_ids = {row.entity_id for row in filtered_rows}
    rows: list[_DiffRow] = []
    added = 0
    changed = 0
    unchanged = 0

    for row in filtered_rows:
        normalized_row = _apply_header_aliases(row.raw_row, header_aliases)
        latest = latest_by_entity.get(row.entity_id)
        if latest is None:
            added += 1
            rows.extend(
                _diff_rows_for_added(entity_id=row.entity_id, raw_row=normalized_row)
            )
            continue
        if latest.content_hash == row.content_hash:
            unchanged += 1
            continue
        changed += 1
        rows.extend(
            _diff_rows_for_changed(
                entity_id=row.entity_id,
                previous=_apply_header_aliases(latest.raw_row, header_aliases),
                new=normalized_row,
            )
        )

    deprecated = 0
    for entity_id, latest in latest_by_entity.items():
        if entity_id in seen_entity_ids:
            continue
        if latest.deprecated:
            continue
        deprecated += 1
        rows.extend(
            _diff_rows_for_deprecated(
                entity_id=entity_id,
                raw_row=_apply_header_aliases(latest.raw_row, header_aliases),
            )
        )

    return _DiffGroup(
        target=target,
        page_url=page_url,
        source_section=source_section,
        parse_version=parse_version,
        rows=tuple(rows),
        added=added,
        changed=changed,
        unchanged=unchanged,
        deprecated=deprecated,
    )


def _latest_wikidata_by_entity(
    *, page_url: str, source_section: str, parse_version: str
) -> dict[str, WikiData]:
    """Return latest WikiData rows keyed by entity_id for the scope."""

    qs = (
        WikiData.objects.filter(
            page_url=page_url,
            source_section=source_section,
            parse_version=parse_version,
        )
        .order_by("entity_id", "-last_seen", "-id")
    )
    latest_by_entity: dict[str, WikiData] = {}
    for record in qs:
        latest_by_entity.setdefault(record.entity_id, record)
    return latest_by_entity


def _diff_rows_for_added(*, entity_id: str, raw_row: dict[str, str]) -> list[_DiffRow]:
    """Build diff rows for a newly added entity."""

    rows: list[_DiffRow] = []
    for field in raw_row:
        rows.append(
            _DiffRow(
                entity_id=entity_id,
                field=field,
                previous="",
                new=str(raw_row.get(field, "")),
                status="added",
            )
        )
    return rows


def _diff_rows_for_deprecated(*, entity_id: str, raw_row: dict[str, str]) -> list[_DiffRow]:
    """Build diff rows for a deprecated entity."""

    rows: list[_DiffRow] = []
    for field in raw_row:
        rows.append(
            _DiffRow(
                entity_id=entity_id,
                field=field,
                previous=str(raw_row.get(field, "")),
                new="",
                status="deprecated",
            )
        )
    return rows


def _diff_rows_for_changed(
    *,
    entity_id: str,
    previous: dict[str, str],
    new: dict[str, str],
) -> list[_DiffRow]:
    """Build diff rows for fields that changed between revisions."""

    rows: list[_DiffRow] = []
    ordered_fields = list(new.keys()) + [key for key in previous.keys() if key not in new]
    seen: set[str] = set()
    for field in ordered_fields:
        if field in seen:
            continue
        seen.add(field)
        prev_value = str(previous.get(field, ""))
        new_value = str(new.get(field, ""))
        if prev_value == new_value:
            continue
        rows.append(
            _DiffRow(
                entity_id=entity_id,
                field=field,
                previous=prev_value,
                new=new_value,
                status="changed",
            )
        )
    return rows


def _apply_header_aliases(raw_row: dict[str, str], header_aliases: dict[str, str]) -> dict[str, str]:
    """Add alias keys for headers without removing existing raw headers."""

    if not header_aliases:
        return dict(raw_row)
    normalized = dict(raw_row)
    for raw_header, alias_header in header_aliases.items():
        if raw_header in normalized and alias_header not in normalized:
            normalized[alias_header] = normalized[raw_header]
    return normalized


def _render_diff_table(rows: tuple[_DiffRow, ...]) -> list[str]:
    """Render diff rows as a plain-text table."""

    headers = ("entity_id", "field", "previous", "new", "status")
    col_widths = {name: len(name) for name in headers}
    for row in rows:
        col_widths["entity_id"] = max(col_widths["entity_id"], len(row.entity_id))
        col_widths["field"] = max(col_widths["field"], len(row.field))
        col_widths["previous"] = max(col_widths["previous"], len(row.previous))
        col_widths["new"] = max(col_widths["new"], len(row.new))
        col_widths["status"] = max(col_widths["status"], len(row.status))

    def fmt_row(entity_id: str, field: str, previous: str, new: str, status: str) -> str:
        return (
            f"{entity_id:<{col_widths['entity_id']}} | "
            f"{field:<{col_widths['field']}} | "
            f"{previous:<{col_widths['previous']}} | "
            f"{new:<{col_widths['new']}} | "
            f"{status:<{col_widths['status']}}"
        )

    lines = [
        fmt_row(*headers),
        fmt_row(
            "-" * col_widths["entity_id"],
            "-" * col_widths["field"],
            "-" * col_widths["previous"],
            "-" * col_widths["new"],
            "-" * col_widths["status"],
        ),
    ]
    for row in rows:
        lines.append(fmt_row(row.entity_id, row.field, row.previous, row.new, row.status))
    return lines
