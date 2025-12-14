"""Minimal smoke tests for initial scaffolding."""

from __future__ import annotations


def test_analysis_engine_imports() -> None:
    """Import the analysis engine and verify the public entry point exists."""

    from analysis.engine import analyze_runs

    assert callable(analyze_runs)


def test_django_project_loads() -> None:
    """Import and initialize Django to verify settings are valid."""

    import os

    import django
    from django.conf import settings

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "theTowerStats.settings")
    django.setup()
    assert "core.apps.CoreConfig" in settings.INSTALLED_APPS
