"""Regression tests for Admin link visibility in navigation."""

from __future__ import annotations

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_admin_link_hidden_for_non_staff(auth_client) -> None:
    """Non-staff users should not see an Admin link in the global navigation."""

    response = auth_client.get(reverse("core:dashboard"))
    assert response.status_code == 200
    assert "/admin/" not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_admin_link_visible_for_staff(client, user) -> None:
    """Staff users should see an Admin link in the global navigation."""

    user.is_staff = True
    user.save(update_fields=["is_staff"])
    client.force_login(user)

    response = client.get(reverse("core:dashboard"))
    assert response.status_code == 200
    assert "/admin/" in response.content.decode("utf-8")

