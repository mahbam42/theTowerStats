"""Django app configuration for Player State."""

from __future__ import annotations

from django.apps import AppConfig


class PlayerStateConfig(AppConfig):
    """AppConfig for player-owned state."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "player_state"

