"""Sync Player State rows from Definitions (idempotent)."""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from player_state.models import Player
from player_state.sync import sync_player_state_from_definitions


class Command(BaseCommand):
    """Create/link player progress rows based on current Definitions."""

    help = "Ensure player progress rows exist for all definitions (idempotent)."

    def add_arguments(self, parser) -> None:
        """Add command arguments."""

        selection = parser.add_mutually_exclusive_group(required=True)
        selection.add_argument(
            "--player",
            default=None,
            help="Username to sync.",
        )
        selection.add_argument(
            "--all",
            action="store_true",
            help="Sync all Player rows.",
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

        username: str | None = options["player"]
        sync_all: bool = options["all"]
        check: bool = options["check"]
        write: bool = options["write"]

        if check and write:
            raise CommandError("Use either --check or --write, not both.")
        if not check and not write:
            raise CommandError("Refusing to write without explicit intent; pass --check or --write.")

        mode = "CHECK" if check else "WRITE"

        if sync_all:
            totals = {
                "players": 0,
                "created_player_rows": 0,
                "updated_player_rows": 0,
                "created_parameter_rows": 0,
            }
            for player in Player.objects.select_related("user").order_by("id"):
                totals["players"] += 1
                summary = sync_player_state_from_definitions(player=player, write=write)
                totals["created_player_rows"] += int(summary.created_player_rows)
                totals["updated_player_rows"] += int(summary.updated_player_rows)
                totals["created_parameter_rows"] += int(summary.created_parameter_rows)
                self.stdout.write(
                    f"[{mode}] user={getattr(player.user, 'username', '<unknown>')} summary={summary}"
                )
            self.stdout.write(f"[{mode}] totals={totals}")
            return None

        user_model = get_user_model()
        user = user_model.objects.filter(username=username).first()
        if user is None:
            raise CommandError(f"Unknown user: {username!r}")
        try:
            player = user.player
        except Exception as exc:  # pragma: no cover
            raise CommandError(f"User {username!r} does not have an associated Player.") from exc

        summary = sync_player_state_from_definitions(player=player, write=write)
        self.stdout.write(f"[{mode}] user={username} summary={summary}")
        return None
