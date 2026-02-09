"""Integration tests for the Calculator Tools dashboard view."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from django.urls import reverse

from gamedata.models import BattleReport, BattleReportProgress

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_calculator_tools_game_speed_calculates(auth_client, player) -> None:
    """Game Speed calculator returns results for valid inputs."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned 100\n",
        checksum="calc-game-speed".ljust(64, "x"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2026, 2, 8, 12, 0, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=3500,
    )

    response = auth_client.get(
        reverse("core:calculator_tools"),
        {
            "calculator": "game_speed",
            "game_speed-run": report.id,
            "game_speed-game_speed": "1",
        },
    )
    assert response.status_code == 200
    game_result = response.context["game_result"]
    assert game_result is not None
    assert game_result["derived_speed"] == pytest.approx(1.0, rel=1e-6)
