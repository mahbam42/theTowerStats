"""Unit tests for MOTD banner context processor."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import cast

import pytest
from django.test import RequestFactory

from core.changelog import ChangelogSummary
from core.context_processors import motd_banner


@pytest.mark.unit
def test_motd_banner_shows_once_per_deploy(monkeypatch) -> None:
    """Show MOTD once per changelog modification timestamp."""

    rf = RequestFactory()
    request = rf.get("/")
    request.user = SimpleNamespace(is_authenticated=True, last_login=datetime(2025, 1, 1, tzinfo=timezone.utc))
    request.session = {}

    modified_at = datetime(2025, 1, 2, tzinfo=timezone.utc)
    monkeypatch.setattr("core.context_processors.changelog_modified_at", lambda: modified_at)
    monkeypatch.setattr(
        "core.context_processors.latest_changelog_summary",
        lambda max_items=2: ChangelogSummary(version="1.2.3", items=("Item one", "Item two")),
    )

    payload = motd_banner(request)
    assert "motd" in payload
    motd = cast(dict[str, object], payload["motd"])
    assert motd["version"] == "1.2.3"
    assert request.session["motd_seen"] == modified_at.isoformat()

    assert motd_banner(request) == {}


@pytest.mark.unit
def test_motd_banner_requires_authenticated_user(monkeypatch) -> None:
    """Skip MOTD when the user is anonymous."""

    rf = RequestFactory()
    request = rf.get("/")
    request.user = SimpleNamespace(is_authenticated=False, last_login=None)
    request.session = {}

    modified_at = datetime(2025, 1, 2, tzinfo=timezone.utc)
    monkeypatch.setattr("core.context_processors.changelog_modified_at", lambda: modified_at)
    monkeypatch.setattr(
        "core.context_processors.latest_changelog_summary",
        lambda max_items=2: ChangelogSummary(version="1.2.3", items=("Item one",)),
    )

    assert motd_banner(request) == {}
