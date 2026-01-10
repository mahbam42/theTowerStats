"""Tests for runtime settings behavior during pytest runs."""

import pytest
from django.conf import settings


@pytest.mark.integration
@pytest.mark.regression
def test_secure_ssl_redirect_disabled_for_tests() -> None:
    """Ensure SSL redirect is disabled when running under pytest."""

    assert getattr(settings, "RUNNING_TESTS", False) is True
    assert settings.SECURE_SSL_REDIRECT is False
