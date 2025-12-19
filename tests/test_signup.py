"""Regression tests for sign-in page account creation."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.mark.django_db
def test_login_page_includes_account_creation_form(client) -> None:
    """Login page includes both sign-in and create-account forms."""

    response = client.get(reverse("login"))
    assert response.status_code == 200

    html = response.content.decode("utf-8")
    assert "<h2>Sign in</h2>" in html
    assert "<h2>Create account</h2>" in html
    assert "signup_submit" in html


@pytest.mark.django_db
def test_signup_creates_user_and_logs_in(client) -> None:
    """Posting the create-account form creates a User, Player, and session."""

    response = client.post(
        reverse("login"),
        data={
            "signup_submit": "1",
            "username": "new_user",
            "password1": "a-strong-password-123",
            "password2": "a-strong-password-123",
            "next": reverse("core:dashboard"),
        },
    )
    assert response.status_code == 302
    assert response["Location"] == reverse("core:dashboard")

    user_model = get_user_model()
    created = user_model.objects.get(username="new_user")
    assert hasattr(created, "player")

    dashboard = client.get(reverse("core:dashboard"))
    assert dashboard.status_code == 200

