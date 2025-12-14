"""App configuration for the core Django app."""

from __future__ import annotations

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for the `core` app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

