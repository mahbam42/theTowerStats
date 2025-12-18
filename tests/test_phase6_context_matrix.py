"""Golden tests for Phase 6 context precedence and empty-state behavior."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

import pytest

from gamedata.models import BattleReport, BattleReportProgress
from player_state.models import Player, Preset


@pytest.mark.django_db
def test_context_matrix_same_metric_schema_across_contexts(client) -> None:
    """Keep metric schema stable while context changes only scope."""

    player = Player.objects.create(name="default")
    preset_a = Preset.objects.create(player=player, name="Preset A")
    preset_b = Preset.objects.create(player=player, name="Preset B")

    def _make_run(*, checksum: str, battle_day: int, tier: int, preset: Preset | None) -> None:
        report = BattleReport.objects.create(
            raw_text="Battle Report\nCoins earned    1,200\n",
            checksum=checksum.ljust(64, "x"),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            battle_date=datetime(2025, 12, battle_day, tzinfo=timezone.utc),
            tier=tier,
            wave=100,
            real_time_seconds=600,
            preset=preset,
        )

    _make_run(checksum="ctx-a", battle_day=10, tier=1, preset=preset_a)
    _make_run(checksum="ctx-b", battle_day=11, tier=1, preset=None)
    _make_run(checksum="ctx-c", battle_day=12, tier=2, preset=preset_b)

    base_params = {"charts": ["coins_earned"], "start_date": date(2025, 12, 9), "end_date": date(2025, 12, 31)}

    # Context 1: date range only (expect all 3 runs in range).
    response = client.get("/", base_params)
    assert response.status_code == 200
    panel = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}["coins_earned"]
    assert panel["labels"] == ["2025-12-10", "2025-12-11", "2025-12-12"]
    assert isinstance(panel["datasets"], list)
    assert len(panel["datasets"]) == 1
    assert set(panel["datasets"][0].keys()) >= {"label", "metricKey", "unit", "data"}

    # Context 2: date range + preset (expect only preset A run).
    response = client.get("/", {**base_params, "preset": preset_a.pk})
    assert response.status_code == 200
    panel = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}["coins_earned"]
    assert panel["labels"] == ["2025-12-10"]
    assert len(panel["datasets"]) == 1
    assert set(panel["datasets"][0].keys()) >= {"label", "metricKey", "unit", "data"}

    # Context 3: preset + tier mismatch should not fall back to tier-only.
    response = client.get("/", {**base_params, "preset": preset_a.pk, "tier": 2})
    assert response.status_code == 200
    panel = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}["coins_earned"]
    assert panel["labels"] == []
    assert len(panel["datasets"]) == 1
    assert panel["datasets"][0]["data"] == []
