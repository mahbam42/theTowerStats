"""Django app configuration for the Definitions layer."""

from __future__ import annotations

from django.apps import AppConfig


class DefinitionsConfig(AppConfig):
    """AppConfig for wiki-derived definitions."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "definitions"

