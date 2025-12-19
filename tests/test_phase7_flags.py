"""Phase 7 data quality flag tests."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest


@pytest.mark.django_db
def test_chart_flags_mark_incomplete_runs(auth_client, player) -> None:
    """Flag dates that contain incomplete run metadata without altering values."""

    from gamedata.models import BattleReport, BattleReportProgress

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned\t1,200\n",
        checksum="flagrun".ljust(64, "x"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc),
        tier=1,
        wave=None,
        real_time_seconds=600,
        coins_earned=1200,
    )

    response = auth_client.get("/", {"charts": ["coins_earned"], "start_date": "2025-12-09"})
    assert response.status_code == 200
    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    datasets = panels["coins_earned"]["datasets"]
    assert datasets
    reasons = datasets[0].get("flagReasons")
    assert reasons and "Incomplete run metadata" in (reasons[0] or "")
