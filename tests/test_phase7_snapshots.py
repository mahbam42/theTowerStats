"""Phase 7 snapshot behavior tests."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest
from django.core.exceptions import ValidationError


@pytest.mark.django_db
def test_chart_snapshot_is_immutable() -> None:
    """Reject updates to a ChartSnapshot after creation."""

    from player_state.models import ChartSnapshot, Player

    player, _ = Player.objects.get_or_create(name="default")
    snapshot = ChartSnapshot.objects.create(
        player=player,
        name="Test snapshot",
        chart_builder={"metric_keys": ["coins_earned"], "chart_type": "line", "group_by": "time", "comparison": "none", "smoothing": "none"},
        chart_context={"start_date": "2025-12-09"},
    )
    snapshot.name = "Renamed"
    with pytest.raises(ValidationError):
        snapshot.save()


@pytest.mark.django_db
def test_snapshot_load_applies_builder_and_context(client) -> None:
    """Loading a snapshot via snapshot_id pre-fills builder inputs and renders its chart."""

    from gamedata.models import BattleReport, BattleReportProgress
    from player_state.models import ChartSnapshot, Player

    report = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned\t1,200\nCoins From Golden Tower\t200\n",
        checksum="snapload".ljust(64, "x"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        coins_earned=1200,
    )

    player, _ = Player.objects.get_or_create(name="default")
    snapshot = ChartSnapshot.objects.create(
        player=player,
        name="Coins snapshot",
        chart_builder={
            "title": "Snapshot chart",
            "metric_keys": ["coins_earned", "coins_from_golden_tower"],
            "chart_type": "line",
            "group_by": "time",
            "comparison": "none",
            "smoothing": "none",
        },
        chart_context={"start_date": "2025-12-09"},
    )

    response = client.get("/", {"snapshot_id": snapshot.id})
    assert response.status_code == 200
    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    assert "chart_builder_custom" in panels

