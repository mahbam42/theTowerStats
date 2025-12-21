"""Phase 7 patch boundary flag tests."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_patch_boundary_dates_are_flagged_in_charts(auth_client, player) -> None:
    """Flag known patch boundaries deterministically without changing values."""

    from definitions.models import PatchBoundary
    from gamedata.models import BattleReport, BattleReportProgress

    PatchBoundary.objects.create(boundary_date=datetime(2025, 12, 10, tzinfo=timezone.utc).date(), label="vX.Y")

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned\t1,200\n",
        checksum="patchflag".ljust(64, "x"),
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

    response = auth_client.get("/", {"charts": ["coins_earned"], "start_date": "2025-12-09"})
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    dataset = panels["coins_earned"]["datasets"][0]
    reasons = dataset.get("flagReasons")
    assert reasons
    assert "Marked boundary date" in (reasons[0] or "")
