"""Django integration tests for Battle History table rendering."""

from __future__ import annotations

import pytest
from django.urls import reverse

from core.services import ingest_battle_report


@pytest.mark.django_db
def test_battle_history_renders_import_widget_and_sort_links(client) -> None:
    """Battle History includes quick import and clickable sort headers."""

    ingest_battle_report(
        "\n".join(
            [
                "Battle Report",
                "Battle Date: 2025-12-01 13:45:00",
                "Tier: 6",
                "Wave: 1234",
                "Real Time: 1h 2m 3s",
                "Killed By: Boss",
                "Coins Earned: 1.00M",
            ]
        )
    )

    response = client.get(reverse("core:battle_history"))
    assert response.status_code == 200

    content = response.content.decode("utf-8")
    assert "Add Battle Report" in content
    assert "Import Battle Report" in content
    assert "<details" in content
    assert "sort=run_progress__battle_date" in content
    assert "sort=-run_progress__wave" in content
    assert "sort=-run_progress__coins_earned" in content
    assert "Highest wave" in content
    assert "1234" in content
    assert "Gem blocks" in content


@pytest.mark.django_db
def test_battle_history_import_panel_opens_on_form_errors(client) -> None:
    """Import panel expands when the import form is invalid."""

    response = client.post(reverse("core:battle_history"), data={})
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "<details open" in content
