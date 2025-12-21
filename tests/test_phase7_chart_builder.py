"""Phase 7 tests for the Chart Builder runtime chart output."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_chart_builder_renders_runtime_chart(auth_client, player) -> None:
    """Render a runtime ChartConfig generated from Chart Builder inputs."""

    from gamedata.models import BattleReport, BattleReportProgress

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned\t1,200\nCoins From Golden Tower\t200\n",
        checksum="builderchart".ljust(64, "x"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        coins_earned=1200,
    )

    response = auth_client.get(
        "/",
        {
            "builder": "1",
            "title": "Custom coins",
            "metric_keys": ["coins_earned", "coins_from_golden_tower"],
            "chart_type": "line",
            "group_by": "time",
            "comparison": "none",
            "smoothing": "none",
            "charts": ["coins_earned"],
            "start_date": "2025-12-09",
        },
    )
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    assert "chart_builder_custom" in panels
    assert panels["chart_builder_custom"]["labels"] == ["2025-12-10"]
