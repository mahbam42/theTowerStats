"""Django integration tests for Phase 3 navigation and page separation."""

from __future__ import annotations

import pytest
from django.urls import reverse


def _assert_nav_links(response) -> None:
    """Assert the global navigation renders and links resolve."""

    content = response.content.decode("utf-8")
    assert 'href="https://mahbam42.github.io/theTowerStats/"' in content
    expected_hrefs = [
        reverse("core:battle_history"),
        reverse("core:dashboard"),
        reverse("core:cards"),
        reverse("core:ultimate_weapon_progress"),
        reverse("core:guardian_progress"),
        reverse("core:bots_progress"),
    ]
    for href in expected_hrefs:
        assert f'href="{href}"' in content


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name",
    [
        "core:dashboard",
        "core:battle_history",
        "core:cards",
        "core:ultimate_weapon_progress",
        "core:guardian_progress",
        "core:bots_progress",
    ],
)
def test_phase3_views_load_and_include_nav(auth_client, url_name: str) -> None:
    """Verify each Phase 3 page loads successfully and includes global navigation."""

    response = auth_client.get(reverse(url_name))
    assert response.status_code == 200
    _assert_nav_links(response)
