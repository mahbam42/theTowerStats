"""Phase 10 regression tests for global search."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from definitions.models import BotDefinition, CardDefinition, GuardianChipDefinition, UltimateWeaponDefinition
from player_state.models import ChartSnapshot, Preset


@pytest.mark.django_db
def test_search_api_returns_navigation_and_docs_results(client) -> None:
    """Unauthenticated search includes navigation items and docs forwarding."""

    response = client.get(reverse("core:search_api"), {"q": "charts"})
    assert response.status_code == 200
    payload = response.json()
    titles = [row["title"] for row in payload["results"]]
    assert any(title == "Charts" for title in titles)
    assert any(title.startswith("Search docs for") for title in titles)
    assert any(row.get("external") is True for row in payload["results"] if row["kind"] == "docs")


@pytest.mark.django_db
def test_search_api_scopes_presets_to_current_player(auth_client, player) -> None:
    """Preset results are restricted to the authenticated player's rows."""

    Preset.objects.create(player=player, name="Farming")

    user_model = get_user_model()
    other_user = user_model.objects.create_user(username="bob", password="password")
    Preset.objects.create(player=other_user.player, name="Farming")

    response = auth_client.get(reverse("core:search_api"), {"q": "farm"})
    assert response.status_code == 200
    payload = response.json()
    titles = [row["title"] for row in payload["results"]]

    assert "Preset: Farming" in titles
    assert titles.count("Preset: Farming") == 1


@pytest.mark.django_db
def test_search_api_includes_chart_snapshot_links(auth_client, player) -> None:
    """Snapshot results link to the appropriate target view."""

    snapshot = ChartSnapshot.objects.create(player=player, name="Before UW unlock", target="charts")
    response = auth_client.get(reverse("core:search_api"), {"q": "before"})
    assert response.status_code == 200
    payload = response.json()

    matches = [row for row in payload["results"] if row["title"] == "Snapshot: Before UW unlock"]
    assert matches
    assert f"snapshot_id={snapshot.id}" in matches[0]["url"]


@pytest.mark.django_db
def test_search_api_includes_entity_dashboard_items_by_name(client) -> None:
    """Entity definition matches include dashboard links with a query parameter."""

    CardDefinition.objects.create(name="Damage", slug="damage")
    UltimateWeaponDefinition.objects.create(name="Chrono Field", slug="chrono-field")
    GuardianChipDefinition.objects.create(name="Aegis", slug="aegis")
    BotDefinition.objects.create(name="Golden Bot", slug="golden-bot")

    response = client.get(reverse("core:search_api"), {"q": "gold"})
    assert response.status_code == 200
    payload = response.json()
    results = payload["results"]

    bot_rows = [row for row in results if row["title"] == "Bot: Golden Bot"]
    assert bot_rows
    assert bot_rows[0]["url"].startswith(reverse("core:bots_progress"))
    assert "q=Golden+Bot" in bot_rows[0]["url"]
