"""Django app configuration for GameData."""

from __future__ import annotations

from django.apps import AppConfig


class GameDataConfig(AppConfig):
    """AppConfig for runtime game data."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "gamedata"

