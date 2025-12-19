"""Pytest fixtures shared across Django integration tests."""

from __future__ import annotations

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
