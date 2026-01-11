"""Helpers for loading changelog metadata."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re

from django.conf import settings


@dataclass(frozen=True, slots=True)
class ChangelogSummary:
    """Parsed summary of a changelog section."""

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


def _parse_changelog_sections(*, max_items: int, max_sections: int) -> tuple[ChangelogSummary, ...]:
    """Parse changelog sections into summaries.

    Args:
        max_items: Maximum number of bullet items to include per section.
        max_sections: Maximum number of sections to include.

    Returns:
        Tuple of ChangelogSummary entries, newest first.
    """

    path = changelog_path()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return ()

    summaries: list[ChangelogSummary] = []
    version: str | None = None
    items: list[str] = []
    in_section = False
    for line in lines:
        match = _SECTION_RE.match(line.strip())
        if match:
            if in_section and version:
                summaries.append(ChangelogSummary(version=version, items=tuple(items)))
                if len(summaries) >= max_sections:
                    return tuple(summaries)
            version = match.group("version")
            items = []
            in_section = True
            continue
        if not in_section:
            continue
        stripped = line.strip()
        if stripped.startswith("- ") and len(items) < max_items:
            items.append(stripped[2:].strip())

    if in_section and version and len(summaries) < max_sections:
        summaries.append(ChangelogSummary(version=version, items=tuple(items)))

    return tuple(summaries)


def latest_changelog_summary(*, max_items: int = 3) -> ChangelogSummary | None:
    """Return a short summary of the latest changelog entry.

    Args:
        max_items: Maximum number of bullet items to include.

    Returns:
        ChangelogSummary for the latest version, or None if unavailable.
    """

    summaries = _parse_changelog_sections(max_items=max_items, max_sections=1)
    if not summaries:
        return None
    return summaries[0]


def latest_changelog_summaries(
    *, max_items: int = 2, max_sections: int = 2
) -> tuple[ChangelogSummary, ...]:
    """Return summaries for the most recent changelog sections.

    Args:
        max_items: Maximum number of bullet items per section.
        max_sections: Maximum number of sections to include.

    Returns:
        Tuple of summaries for the most recent sections.
    """

    return _parse_changelog_sections(max_items=max_items, max_sections=max_sections)
