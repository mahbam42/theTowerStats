"""Unit tests for changelog helpers."""

from __future__ import annotations

import pytest

import core.changelog as changelog


@pytest.mark.unit
def test_latest_changelog_summary_reads_latest_section(tmp_path, monkeypatch) -> None:
    """Parse the first changelog section into a summary."""

    content = "\n".join(
        [
            "# Changelog",
            "",
            "## [1.2.3]",
            "- Added new chart filters.",
            "- Fixed compare formatting.",
            "",
            "## [1.2.2]",
            "- Older entry.",
        ]
    )
    path = tmp_path / "CHANGELOG.md"
    path.write_text(content, encoding="utf-8")
    monkeypatch.setattr(changelog, "changelog_path", lambda: path)

    summary = changelog.latest_changelog_summary(max_items=2)
    assert summary is not None
    assert summary.version == "1.2.3"
    assert summary.items == ("Added new chart filters.", "Fixed compare formatting.")


@pytest.mark.unit
def test_changelog_modified_at_returns_none_when_missing(tmp_path, monkeypatch) -> None:
    """Return None when the changelog file is missing."""

    missing = tmp_path / "MISSING.md"
    monkeypatch.setattr(changelog, "changelog_path", lambda: missing)

    assert changelog.changelog_modified_at() is None
