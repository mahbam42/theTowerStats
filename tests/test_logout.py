"""Regression tests for logout UX and HTTP method correctness."""

from __future__ import annotations

import pytest
from django.urls import reverse

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_base_template_renders_logout_as_post_form(auth_client) -> None:
    """Signed-in navigation renders logout as a POST form (not a GET link)."""

    response = auth_client.get(reverse("core:dashboard"))
    assert response.status_code == 200

    html = response.content.decode("utf-8")
    assert f'action="{reverse("logout")}"' in html
    assert 'method="post"' in html
    assert "csrfmiddlewaretoken" in html
    assert f'href="{reverse("logout")}"' not in html


@pytest.mark.django_db
def test_logout_post_ends_session(auth_client) -> None:
    """POSTing to logout ends the session and redirects to login."""

    response = auth_client.post(reverse("logout"), data={"next": reverse("login")})
    assert response.status_code == 302
    assert response["Location"] == reverse("login")

    after = auth_client.get(reverse("core:dashboard"))
    assert after.status_code == 302
    assert after["Location"].startswith(reverse("login"))
