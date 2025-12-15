"""Rebuild wiki-derived definition tables (Definitions layer).

This command orchestrates:
1) wiki ingestion into `definitions.WikiData` (optional, online), then
2) offline translation into structured definition + parameter tables.

It must not delete Player State or GameData rows.
"""

from __future__ import annotations

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from definitions.wiki_rebuild import (
    rebuild_bots_from_wikidata,
    rebuild_cards_from_wikidata,
    rebuild_guardian_chips_from_wikidata,
    rebuild_ultimate_weapons_from_wikidata,
)


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
        check: bool = options["check"]
        write: bool = options["write"]

        if check and write:
            raise CommandError("Use either --check or --write, not both.")
        if not check and not write:
            raise CommandError("Refusing to write without explicit intent; pass --check or --write.")

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
            call_command("fetch_wiki_data", target="cards_list", check=check, write=write)
        if target in {"bots", "all"}:
            call_command("fetch_wiki_data", target="bots", check=check, write=write)
        if target in {"guardians", "all"}:
            call_command("fetch_wiki_data", target="guardian_chips", check=check, write=write)
        if target in {"ultimate_weapons", "all"}:
            call_command("fetch_wiki_data", target="ultimate_weapons", check=check, write=write)

