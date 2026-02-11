"""Run deploy-time steps for Railway releases."""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

DEFAULT_WIKI_REBUILD_TIMEOUT_SECONDS = 300


@dataclass(frozen=True, slots=True)
class WikiRebuildResult:
    """Outcome of the wiki rebuild subprocess."""

    completed: bool
    reason: str | None


def _env_truthy(name: str, *, default: bool = False) -> bool:
    """Return True when an environment variable is set to a truthy value.

    Args:
        name: Environment variable name.
        default: Value returned when the variable is unset.

    Returns:
        Boolean interpretation of the environment variable.
    """

    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def _env_int(name: str, *, default: int) -> int:
    """Parse an integer environment variable.

    Args:
        name: Environment variable name.
        default: Value when the variable is not set or empty.

    Returns:
        Parsed integer value.
    """

    raw = os.getenv(name)
    if raw is None:
        return default
    value = raw.strip()
    if not value:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise CommandError(f"Invalid integer for {name}: {raw!r}") from exc


def _manage_py_path() -> Path:
    """Return the absolute path to manage.py for this repository."""

    manage_py = Path(__file__).resolve().parents[3] / "manage.py"
    if not manage_py.exists():
        raise CommandError(f"manage.py not found at expected path: {manage_py}")
    return manage_py


def _wiki_rebuild_timeout_seconds() -> int | None:
    """Return the timeout for wiki rebuilds, or None when disabled."""

    timeout = _env_int(
        "TOWERSTATS_WIKI_REBUILD_TIMEOUT_SECONDS",
        default=DEFAULT_WIKI_REBUILD_TIMEOUT_SECONDS,
    )
    if timeout <= 0:
        return None
    return timeout


def _wiki_rebuild_command(*, offline_wiki: bool, verbosity: int) -> list[str]:
    """Build the rebuild_wiki_definitions command line."""

    command = [
        sys.executable,
        str(_manage_py_path()),
        "rebuild_wiki_definitions",
        "--target",
        "all",
        "--write",
        "--verbosity",
        str(verbosity),
    ]
    if offline_wiki:
        command.append("--skip-fetch")
    return command


def _run_wiki_rebuild(
    *, offline_wiki: bool, verbosity: int, timeout_seconds: int | None
) -> WikiRebuildResult:
    """Run the wiki rebuild with an optional timeout.

    Args:
        offline_wiki: When True, skip network fetches.
        verbosity: Django verbosity level.
        timeout_seconds: Max seconds to allow before abandoning the rebuild.

    Returns:
        Result describing whether the rebuild completed and any failure reason.
    """

    command = _wiki_rebuild_command(offline_wiki=offline_wiki, verbosity=verbosity)
    try:
        if timeout_seconds is None:
            subprocess.run(command, check=True)
        else:
            subprocess.run(command, check=True, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        return WikiRebuildResult(
            completed=False,
            reason=(
                f"timed out after {timeout_seconds}s" if timeout_seconds is not None else "timed out"
            ),
        )
    except subprocess.CalledProcessError as exc:
        return WikiRebuildResult(completed=False, reason=f"exit code {exc.returncode}")
    return WikiRebuildResult(completed=True, reason=None)


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
        offline_wiki = _env_truthy("TOWERSTATS_WIKI_OFFLINE", default=False)
        wiki_timeout_seconds = _wiki_rebuild_timeout_seconds()

        if not write:
            raise CommandError("Refusing to run without explicit intent; pass --write.")

        if not skip_migrations:
            self.stdout.write("Running migrations...")
            call_command("migrate", interactive=False, verbosity=verbosity)

        if not skip_wiki:
            timeout_label = ""
            if wiki_timeout_seconds is not None:
                timeout_label = f", timeout={wiki_timeout_seconds}s"
            if offline_wiki:
                self.stdout.write(
                    f"Rebuilding wiki definitions (target=all, write, offline{timeout_label})..."
                )
            else:
                self.stdout.write(f"Rebuilding wiki definitions (target=all, write{timeout_label})...")
            result = _run_wiki_rebuild(
                offline_wiki=offline_wiki,
                verbosity=verbosity,
                timeout_seconds=wiki_timeout_seconds,
            )
            if not result.completed:
                reason = result.reason or "unknown error"
                self.stderr.write(
                    "Wiki rebuild failed; deploy continuing. "
                    f"Reason: {reason}. "
                    "Check wiki ingestion logs and consider rerunning rebuild_wiki_definitions."
                )

        if not skip_reparse:
            self.stdout.write("Reparsing battle reports...")
            call_command("reparse_battle_reports", write=True, verbosity=verbosity)

        self.stdout.write("Deploy pipeline complete.")
        return None
