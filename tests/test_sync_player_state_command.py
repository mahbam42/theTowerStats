"""Integration tests for the sync_player_state management command."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_sync_player_state_requires_selection_flag(player) -> None:
    """Command refuses to run without --player or --all."""

    with pytest.raises(CommandError, match="one of the arguments"):
        call_command("sync_player_state", "--check")


@pytest.mark.django_db
def test_sync_player_state_runs_for_single_user(user) -> None:
    """Command runs in check mode when targeting a specific user."""

    call_command("sync_player_state", "--player", user.username, "--check")


@pytest.mark.django_db
def test_sync_player_state_runs_for_all_users(user) -> None:
    """Command runs in check mode for all users with Players."""

    user_model = get_user_model()
    _ = user_model.objects.create_user(username="bob", password="password").player

    call_command("sync_player_state", "--all", "--check")
