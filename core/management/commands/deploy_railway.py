"""Run deploy-time steps for Railway releases."""

from __future__ import annotations

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Run migrations and rebuild/reparse tasks for Railway deploys."""

    help = "Run deploy-time steps for Railway (migrate, rebuild wiki data, reparse Battle Reports)."

    def add_arguments(self, parser) -> None:
        """Add command arguments."""

        parser.add_argument(
            "--write",
            action="store_true",
            help="Run deploy steps that write to the database.",
        )
        parser.add_argument(
            "--skip-migrations",
            action="store_true",
            help="Skip Django migrations.",
        )
        parser.add_argument(
            "--skip-wiki",
            action="store_true",
            help="Skip rebuild_wiki_definitions (forced scrape).",
        )
        parser.add_argument(
            "--skip-reparse",
            action="store_true",
            help="Skip reparse_battle_reports.",
        )

    def handle(self, *args, **options) -> str | None:
        """Run the deploy pipeline in order."""

        verbosity = int(options.get("verbosity", 1))
        write = bool(options.get("write"))
        skip_migrations = bool(options.get("skip_migrations"))
        skip_wiki = bool(options.get("skip_wiki"))
        skip_reparse = bool(options.get("skip_reparse"))

        if not write:
            raise CommandError("Refusing to run without explicit intent; pass --write.")

        if not skip_migrations:
            self.stdout.write("Running migrations...")
            call_command("migrate", interactive=False, verbosity=verbosity)

        if not skip_wiki:
            self.stdout.write("Rebuilding wiki definitions (target=all, write)...")
            call_command("rebuild_wiki_definitions", target="all", write=True, verbosity=verbosity)

        if not skip_reparse:
            self.stdout.write("Reparsing battle reports...")
            call_command("reparse_battle_reports", write=True, verbosity=verbosity)

        self.stdout.write("Deploy pipeline complete.")
        return None
