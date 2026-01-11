"""Template context processors for theTowerStats."""

from __future__ import annotations

from datetime import datetime

from django.conf import settings
from django.http import HttpRequest
from django.utils import timezone

from core.changelog import changelog_modified_at, latest_changelog_summary

from core.demo import demo_mode_enabled
from core.session_keys import MOTD_LAST_LOGIN_SESSION_KEY


def demo_mode(request: HttpRequest) -> dict[str, bool]:
    """Expose demo mode state to all templates.

    Args:
        request: Current request object.

    Returns:
        Context dict with `demo_mode` boolean.
    """

    return {"demo_mode": demo_mode_enabled(request)}


def motd_banner(request: HttpRequest) -> dict[str, object]:
    """Expose a one-time MOTD banner when a new deploy is detected."""

    def _parse_session_login(value: object) -> datetime | None:
        """Parse a session-stored login timestamp if available."""

        if not isinstance(value, str) or not value.strip():
            return None
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None
        if timezone.is_naive(parsed):
            return timezone.make_aware(parsed)
        return parsed

    if not request.user.is_authenticated:
        return {}
    modified_at = changelog_modified_at()
    if modified_at is None:
        return {}
    session_value = request.session.get(MOTD_LAST_LOGIN_SESSION_KEY)
    last_login = _parse_session_login(session_value)
    if last_login is None:
        if session_value is not None:
            last_login = timezone.make_aware(datetime.min)
        else:
            last_login = request.user.last_login
    if last_login is None:
        last_login = timezone.make_aware(datetime.min)
    if modified_at <= last_login:
        return {}
    token = modified_at.isoformat()
    if request.session.get("motd_seen") == token:
        return {}
    summary = latest_changelog_summary(max_items=2)
    if summary is None:
        return {}
    request.session["motd_seen"] = token
    return {
        "motd": {
            "version": summary.version,
            "items": summary.items,
            "changelog_url": getattr(settings, "CHANGELOG_GITHUB_URL", ""),
        }
    }
