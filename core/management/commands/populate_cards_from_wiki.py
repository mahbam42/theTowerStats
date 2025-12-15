"""Populate structured card models from already-ingested WikiData.

This command is intentionally offline: it reads from `core.WikiData` and
creates/updates Phase 3 structural models with `source_wikidata` pointers for
traceability.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from core.wiki_population import (
    populate_all_cards_from_wiki,
    populate_all_from_wiki,
    populate_bots_from_wiki,
    populate_card_levels_from_wiki,
    populate_card_slots_from_wiki,
    populate_cards_from_wiki,
    populate_guardian_chips_from_wiki,
    populate_ultimate_weapons_from_wiki,
)


class Command(BaseCommand):
    """Populate card-related models from existing WikiData revisions."""

    help = "Populate wiki-derived models (cards, bots, guardian chips, ultimate weapons)."

    def add_arguments(self, parser) -> None:
        """Add command arguments."""

        parser.add_argument(
            "--target",
            choices=(
                "slots",
                "cards",
                "levels",
                "bots",
                "guardian_chips",
                "ultimate_weapons",
                "cards_all",
                "all",
            ),
            default="all",
            help="Which models to populate from WikiData.",
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
        elif target == "bots":
            summary = populate_bots_from_wiki(write=do_write)
        elif target == "guardian_chips":
            summary = populate_guardian_chips_from_wiki(write=do_write)
        elif target == "ultimate_weapons":
            summary = populate_ultimate_weapons_from_wiki(write=do_write)
        elif target == "cards_all":
            summary = populate_all_cards_from_wiki(write=do_write)
        elif target == "all":
            summary = populate_all_from_wiki(write=do_write)
        else:
            raise CommandError(f"Unknown target: {target!r}")

        self.stdout.write(
            f"[{mode}] target={target} "
            f"card_slots(created={summary.created_card_slots}, updated={summary.updated_card_slots}) "
            f"card_definitions(created={summary.created_card_definitions}, updated={summary.updated_card_definitions}) "
            f"card_parameters(created={summary.created_card_parameters}) "
            f"card_levels(created={summary.created_card_levels}) "
            f"bot_definitions(created={summary.created_bot_definitions}, updated={summary.updated_bot_definitions}) "
            f"bot_levels(created={summary.created_bot_levels}) "
            f"bot_parameters(created={summary.created_bot_parameters}) "
            f"guardian_definitions(created={summary.created_guardian_chip_definitions}, updated={summary.updated_guardian_chip_definitions}) "
            f"guardian_levels(created={summary.created_guardian_chip_levels}) "
            f"guardian_parameters(created={summary.created_guardian_chip_parameters}) "
            f"uw_definitions(created={summary.created_ultimate_weapon_definitions}, updated={summary.updated_ultimate_weapon_definitions}) "
            f"uw_levels(created={summary.created_ultimate_weapon_levels}) "
            f"uw_parameters(created={summary.created_ultimate_weapon_parameters})"
        )
        return None

