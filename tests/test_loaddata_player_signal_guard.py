"""Regression tests for fixture loading with player lifecycle signals."""

from __future__ import annotations

import json

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from player_state.models import Player

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_loaddata_does_not_create_duplicate_player_for_user(tmp_path) -> None:
    """Ensure `loaddata` does not trigger Player auto-provisioning on raw saves."""

    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(
        json.dumps(
            [
                {
                    "model": "auth.user",
                    "pk": 1,
                    "fields": {
                        "password": "",
                        "last_login": None,
                        "is_superuser": False,
                        "username": "fixture-user",
                        "first_name": "",
                        "last_name": "",
                        "email": "",
                        "is_staff": False,
                        "is_active": True,
                        "date_joined": "2025-01-01T00:00:00Z",
                        "groups": [],
                        "user_permissions": [],
                    },
                },
                {
                    "model": "player_state.player",
                    "pk": 1,
                    "fields": {
                        "user": 1,
                        "display_name": "fixture-user",
                        "card_slots_unlocked": 0,
                        "created_at": "2025-01-01T00:00:00Z",
                    },
                },
            ]
        ),
        encoding="utf-8",
    )

    call_command("loaddata", str(fixture_path))

    user = get_user_model().objects.get(pk=1)
    assert Player.objects.filter(user=user).count() == 1
