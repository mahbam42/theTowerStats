"""Unit tests for MOTD banner context processor."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import cast

import pytest
from django.test import RequestFactory

from core.changelog import ChangelogSummary
from core.context_processors import motd_banner
from core.session_keys import MOTD_LAST_LOGIN_SESSION_KEY


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
        "core.context_processors.latest_changelog_summaries",
        lambda max_items=2, max_sections=2: (
            ChangelogSummary(version="1.2.3", items=("Item one", "Item two")),
            ChangelogSummary(version="1.2.2", items=("Older one",)),
        ),
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
        "core.context_processors.latest_changelog_summaries",
        lambda max_items=2, max_sections=2: (
            ChangelogSummary(version="1.2.3", items=("Item one",)),
        ),
    )

    assert motd_banner(request) == {}


@pytest.mark.unit
def test_motd_banner_uses_session_last_login(monkeypatch) -> None:
    """Prefer the session-stored last login timestamp when available."""

    rf = RequestFactory()
    request = rf.get("/")
    request.user = SimpleNamespace(is_authenticated=True, last_login=datetime(2025, 1, 5, tzinfo=timezone.utc))
    request.session = {MOTD_LAST_LOGIN_SESSION_KEY: datetime(2025, 1, 1, tzinfo=timezone.utc).isoformat()}

    modified_at = datetime(2025, 1, 2, tzinfo=timezone.utc)
    monkeypatch.setattr("core.context_processors.changelog_modified_at", lambda: modified_at)
    monkeypatch.setattr(
        "core.context_processors.latest_changelog_summaries",
        lambda max_items=2, max_sections=2: (
            ChangelogSummary(version="1.2.3", items=("Item one",)),
        ),
    )

    payload = motd_banner(request)
    assert "motd" in payload


@pytest.mark.unit
def test_motd_banner_shows_for_first_login_session(monkeypatch) -> None:
    """Show MOTD when the session indicates a first login."""

    rf = RequestFactory()
    request = rf.get("/")
    request.user = SimpleNamespace(is_authenticated=True, last_login=datetime(2025, 1, 5, tzinfo=timezone.utc))
    request.session = {MOTD_LAST_LOGIN_SESSION_KEY: ""}

    modified_at = datetime(2024, 12, 1, tzinfo=timezone.utc)
    monkeypatch.setattr("core.context_processors.changelog_modified_at", lambda: modified_at)
    monkeypatch.setattr(
        "core.context_processors.latest_changelog_summaries",
        lambda max_items=2, max_sections=2: (
            ChangelogSummary(version="1.2.3", items=("Item one",)),
        ),
    )

    payload = motd_banner(request)
    assert "motd" in payload
