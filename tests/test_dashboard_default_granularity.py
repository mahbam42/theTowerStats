"""Integration tests for dashboard default granularity."""

from __future__ import annotations

import pytest
from django.urls import reverse

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_dashboard_defaults_to_per_run_granularity(auth_client, player) -> None:
    """Charts dashboard should default to per-run granularity."""

    response = auth_client.get(reverse("core:dashboard"))
    assert response.status_code == 200

    chart_form = response.context["chart_form"]
    assert chart_form.cleaned_data["granularity"] == "per_run"
