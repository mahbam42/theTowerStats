"""Tests for chart favorites and saved Chart Builder configs."""

from __future__ import annotations

import json

import pytest
from django.urls import reverse

from core.forms import ChartFavoritesForm
from player_state.models import ChartBuilderSavedConfig, ChartDashboardPreference


@pytest.mark.unit
def test_chart_favorites_form_dedupes_and_orders() -> None:
    """Favorites keep order and remove duplicates."""

    form = ChartFavoritesForm(
        data={"favorite_chart_ids": json.dumps(["coins_per_hour", "coins_per_hour", "coins_earned"])},
        available_chart_ids={"coins_per_hour", "coins_earned"},
    )
    assert form.is_valid()
    assert form.cleaned_data["favorite_chart_ids"] == ("coins_per_hour", "coins_earned")


@pytest.mark.django_db
@pytest.mark.integration
def test_dashboard_defaults_to_favorite_charts(auth_client, player) -> None:
    """Dashboard defaults to saved favorite charts when no selection is provided."""

    ChartDashboardPreference.objects.create(
        player=player,
        favorite_chart_ids=["coins_per_hour"],
    )

    response = auth_client.get(reverse("core:dashboard"))
    assert response.status_code == 200
    assert response.context["chart_form"].cleaned_data["charts"] == ["coins_per_hour"]


@pytest.mark.django_db
@pytest.mark.integration
def test_dashboard_saves_chart_builder_creation(auth_client, player) -> None:
    """Saving a chart builder creation persists the payload."""

    response = auth_client.post(
        reverse("core:dashboard"),
        data={
            "action": "save_chart_builder_creation",
            "name": "My saved chart",
            "metric_keys": ["coins_earned"],
            "chart_type": "line",
            "x_axis": "time",
            "group_by": "time",
            "comparison": "none",
            "smoothing": "none",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert ChartBuilderSavedConfig.objects.filter(player=player, name="My saved chart").exists()
