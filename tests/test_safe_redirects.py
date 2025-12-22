"""Unit tests for centralized safe redirects."""

from __future__ import annotations

import pytest
from django.test import RequestFactory

from core.redirects import safe_redirect

pytestmark = pytest.mark.unit


def test_safe_redirect_allows_relative_url() -> None:
    """Relative paths are treated as safe and are redirected to directly."""

    request = RequestFactory().get("/source")
    response = safe_redirect(request, candidates=["/destination"], fallback="/fallback")
    assert response.status_code == 302
    assert response["Location"] == "/destination"


def test_safe_redirect_rejects_external_url() -> None:
    """External hosts are rejected and fall back to the provided safe URL."""

    request = RequestFactory().get("/source")
    response = safe_redirect(
        request,
        candidates=["https://example.invalid/evil"],
        fallback="/fallback",
    )
    assert response.status_code == 302
    assert response["Location"] == "/fallback"


def test_safe_redirect_rejects_http_when_secure_request() -> None:
    """HTTPS requests reject `http://` redirect targets."""

    request = RequestFactory().get("/source", secure=True)
    response = safe_redirect(
        request,
        candidates=["http://testserver/insecure"],
        fallback="/fallback",
    )
    assert response.status_code == 302
    assert response["Location"] == "/fallback"

