"""Django integration tests for Phase 1 chart view."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from core.models import GameData, RunProgress


@pytest.mark.django_db
def test_dashboard_view_renders(client) -> None:
    """Create minimal records and verify the dashboard view returns HTTP 200."""

    game_data = GameData.objects.create(
        raw_text="Battle Report\nCoins: 12345\n", checksum="x" * 64
    )
    RunProgress.objects.create(
        game_data=game_data,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    response = client.get("/")
    assert response.status_code == 200
