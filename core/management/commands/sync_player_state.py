"""Sync Player State rows from Definitions (idempotent)."""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from player_state.sync import sync_player_state_from_definitions


class Command(BaseCommand):
    """Create/link player progress rows based on current Definitions."""

    help = "Ensure player progress rows exist for all definitions (idempotent)."

    def add_arguments(self, parser) -> None:
        """Add command arguments."""

        parser.add_argument(
            "--player",
            default="default",
            help="Player name to sync (default: default).",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Dry-run: do not write to the database (no-op in this phase).",
        )
        parser.add_argument(
            "--write",
            action="store_true",
            help="Write changes to the database.",
        )

    def handle(self, *args, **options) -> str | None:
        """Run the command."""

        player_name: str = options["player"]
        check: bool = options["check"]
        write: bool = options["write"]

        if check and write:
            raise CommandError("Use either --check or --write, not both.")
        if not check and not write:
            raise CommandError("Refusing to write without explicit intent; pass --check or --write.")

        summary = sync_player_state_from_definitions(player_name=player_name, write=write)
        mode = "CHECK" if check else "WRITE"
        self.stdout.write(f"[{mode}] player={player_name} summary={summary}")
        return None

