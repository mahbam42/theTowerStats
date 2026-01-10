"""Helpers for loading changelog metadata."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re

from django.conf import settings


@dataclass(frozen=True, slots=True)
class ChangelogSummary:
    """Parsed summary of the latest changelog section."""

    version: str
    items: tuple[str, ...]


_SECTION_RE = re.compile(r"^##\s+\[(?P<version>[^\]]+)\]")


def changelog_path() -> Path:
    """Return the filesystem path to CHANGELOG.md."""

    return Path(settings.BASE_DIR) / "CHANGELOG.md"


def changelog_modified_at() -> datetime | None:
    """Return the last modified timestamp for the changelog."""

    path = changelog_path()
    try:
        stat = path.stat()
    except FileNotFoundError:
        return None
    return datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)


def latest_changelog_summary(*, max_items: int = 3) -> ChangelogSummary | None:
    """Return a short summary of the latest changelog entry.

    Args:
        max_items: Maximum number of bullet items to include.

    Returns:
        ChangelogSummary for the latest version, or None if unavailable.
    """

    path = changelog_path()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return None

    version: str | None = None
    items: list[str] = []
    in_section = False
    for line in lines:
        match = _SECTION_RE.match(line.strip())
        if match:
            if in_section:
                break
            version = match.group("version")
            in_section = True
            continue
        if not in_section:
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
        if len(items) >= max_items:
            break

    if not version:
        return None
    return ChangelogSummary(version=version, items=tuple(items))
