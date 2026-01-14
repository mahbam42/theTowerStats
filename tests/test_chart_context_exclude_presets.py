"""Integration tests for chart context preset exclusions."""

from __future__ import annotations

from datetime import date

import pytest
from django.urls import reverse

from core.services import ingest_battle_report
from player_state.models import Preset

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_chart_context_excludes_selected_presets(auth_client, player) -> None:
    """Exclude presets removes those runs from the chart scope."""

    ingest_battle_report(
        "\n".join(
            [
                "Battle Report",
                "Battle Date: 2025-12-05 10:00:00",
                "Tier: 6",
                "Wave: 123",
                "Real Time: 1h 0m 0s",
                "Coins Earned: 1.00M",
            ]
        ),
        player=player,
        preset_name="Farm",
    )
    ingest_battle_report(
        "\n".join(
            [
                "Battle Report",
                "Battle Date: 2025-12-06 10:00:00",
                "Tier: 6",
                "Wave: 234",
                "Real Time: 1h 0m 0s",
                "Coins Earned: 2.00M",
            ]
        ),
        player=player,
        preset_name="Tournament",
    )

    exclude_preset = Preset.objects.get(player=player, name="Tournament")
    response = auth_client.get(
        reverse("core:dashboard"),
        {
            "start_date": date(2025, 12, 1),
            "end_date": date(2025, 12, 31),
            "exclude_presets": [exclude_preset.id],
        },
    )
    assert response.status_code == 200
    scope_summary = response.context["scope_summary"]
    assert scope_summary["runs_in_scope"] == 1
    assert "Excluded presets: Tournament." in response.context["why_panel"]["excluded"]


@pytest.mark.django_db
def test_chart_context_exclude_and_include_preset_yields_empty_scope(auth_client, player) -> None:
    """Including and excluding the same preset yields no runs."""

    ingest_battle_report(
        "\n".join(
            [
                "Battle Report",
                "Battle Date: 2025-12-05 10:00:00",
                "Tier: 6",
                "Wave: 123",
                "Real Time: 1h 0m 0s",
                "Coins Earned: 1.00M",
            ]
        ),
        player=player,
        preset_name="Farm",
    )
    preset = Preset.objects.get(player=player, name="Farm")
    response = auth_client.get(
        reverse("core:dashboard"),
        {
            "start_date": date(2025, 12, 1),
            "end_date": date(2025, 12, 31),
            "preset": preset.id,
            "exclude_presets": [preset.id],
        },
    )
    assert response.status_code == 200
    scope_summary = response.context["scope_summary"]
    assert scope_summary["runs_in_scope"] == 0
    assert response.context["chart_empty_state"] == "No runs match the current filters."
