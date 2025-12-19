"""Template context processors for theTowerStats."""

from __future__ import annotations

from django.http import HttpRequest

from core.demo import demo_mode_enabled


def demo_mode(request: HttpRequest) -> dict[str, bool]:
    """Expose demo mode state to all templates.

    Args:
        request: Current request object.

    Returns:
        Context dict with `demo_mode` boolean.
    """

    return {"demo_mode": demo_mode_enabled(request)}

