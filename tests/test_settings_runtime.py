"""Tests for runtime settings behavior during pytest runs."""

import os

import pytest
from django.conf import settings


@pytest.mark.integration
@pytest.mark.regression
def test_secure_ssl_redirect_disabled_for_tests() -> None:
    """Ensure SSL redirect is disabled when running under pytest."""

    assert getattr(settings, "RUNNING_TESTS", False) is True
    assert settings.SECURE_SSL_REDIRECT is False


@pytest.mark.integration
def test_default_test_database_selection() -> None:
    """Default to SQLite for tests unless CI opts into Postgres."""

    if os.getenv("DJANGO_TEST_DATABASE_URL") or os.getenv("DJANGO_TEST_USE_SQLITE") is not None:
        pytest.skip("Explicit test DB overrides disable the default selection behavior.")

    engine = settings.DATABASES["default"]["ENGINE"]
    if os.getenv("GITHUB_ACTIONS"):
        assert engine == "django.db.backends.postgresql"
    else:
        assert engine == "django.db.backends.sqlite3"
