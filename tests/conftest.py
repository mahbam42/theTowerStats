"""Pytest fixtures shared across Django integration tests."""

from __future__ import annotations

from collections.abc import Sequence

import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def user(db):
    """Return a logged-in capable User with an associated Player."""

    user_model = get_user_model()
    return user_model.objects.create_user(username="alice", password="password")


@pytest.fixture
def player(user):
    """Return the Player associated with the default test user."""

    return user.player


@pytest.fixture
def auth_client(client, user):
    """Return a Django test client authenticated as the default test user."""

    client.force_login(user)
    return client


def pytest_collection_modifyitems(items: Sequence[pytest.Item]) -> None:
    """Enforce that every test has exactly one speed marker.

    Phase 10B requires the suite to be runnable by intent:
    - `unit`: pure, fast tests with no database access.
    - `integration`: tests touching Django, database, views, commands, or IO.

    Each test must have exactly one of these markers.
    """

    invalid: list[str] = []
    for item in items:
        has_unit = item.get_closest_marker("unit") is not None
        has_integration = item.get_closest_marker("integration") is not None
        if has_unit == has_integration:
            markers = []
            if has_unit:
                markers.append("unit")
            if has_integration:
                markers.append("integration")
            invalid.append(f"{item.nodeid} (markers={markers or 'none'})")

    if invalid:
        joined = "\n".join(f"- {nodeid}" for nodeid in invalid)
        raise pytest.UsageError(
            "Each test must have exactly one speed marker: `@pytest.mark.unit` or "
            "`@pytest.mark.integration`.\n"
            f"Offending tests:\n{joined}"
        )
