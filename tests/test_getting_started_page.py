"""Django integration tests for the Getting Started onboarding page."""

from __future__ import annotations

import pytest
from django.urls import reverse

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_getting_started_page_renders_actions(auth_client) -> None:
    """Render Getting Started and ensure primary entry points are present."""

    response = auth_client.get(reverse("core:getting_started"))
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "theTowerStats" in content
    assert f'href="{reverse("core:battle_history")}"' in content
    assert f'action="{reverse("core:enable_demo_mode")}"' in content
    assert 'id="landing-demo-chart"' in content


@pytest.mark.django_db
def test_getting_started_page_renders_signed_out_cta(client) -> None:
    """Render Getting Started for anonymous users and show the signup CTA."""

    response = client.get(reverse("core:getting_started"))
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Create your account" in content
    assert f'href="{reverse("login")}"' in content


@pytest.mark.django_db
def test_home_route_renders_landing_page(client) -> None:
    """Render the default homepage as the landing page."""

    response = client.get("/")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "theTowerStats" in content
