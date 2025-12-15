"""Populate structured card models from already-ingested WikiData.

This command is intentionally offline: it reads from `core.WikiData` and
creates/updates Phase 3 structural models with `source_wikidata` pointers for
traceability.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from core.wiki_population import (
    populate_all_cards_from_wiki,
    populate_card_levels_from_wiki,
    populate_card_slots_from_wiki,
    populate_cards_from_wiki,
)


class Command(BaseCommand):
    """Populate card-related models from existing WikiData revisions."""

    help = "Populate card models (slots/definitions/parameters/levels) from core.WikiData."

    def add_arguments(self, parser) -> None:
        """Add command arguments."""

        parser.add_argument(
            "--target",
            choices=("slots", "cards", "levels", "all"),
            default="all",
            help="Which card models to populate from WikiData.",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Dry-run: compute what would change without writing.",
        )
        parser.add_argument(
            "--write",
            action="store_true",
            help="Write changes to the database (required to persist results).",
        )

    def handle(self, *args, **options) -> str | None:
        """Run the command."""

        target: str = options["target"]
        check: bool = options["check"]
        write: bool = options["write"]

        if check and write:
            raise CommandError("Use either --check or --write, not both.")
        if not check and not write:
            raise CommandError("Refusing to write without explicit intent; pass --check or --write.")

        mode = "CHECK" if check else "WRITE"
        do_write = write

        if target == "slots":
            summary = populate_card_slots_from_wiki(write=do_write)
        elif target == "cards":
            summary = populate_cards_from_wiki(write=do_write)
        elif target == "levels":
            summary = populate_card_levels_from_wiki(write=do_write)
        elif target == "all":
            summary = populate_all_cards_from_wiki(write=do_write)
        else:
            raise CommandError(f"Unknown target: {target!r}")

        self.stdout.write(
            f"[{mode}] target={target} "
            f"card_slots(created={summary.created_card_slots}, updated={summary.updated_card_slots}) "
            f"card_definitions(created={summary.created_card_definitions}, updated={summary.updated_card_definitions}) "
            f"card_parameters(created={summary.created_card_parameters}) "
            f"card_levels(created={summary.created_card_levels})"
        )
        return None

