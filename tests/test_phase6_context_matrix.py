"""Golden/regression tests for Phase 6 context handling and empty states."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from typing import Any

import pytest

from gamedata.models import BattleReport, BattleReportProgress
from player_state.models import Preset


def _panel(response, *, chart_id: str) -> dict[str, Any]:
    """Return a chart panel payload from the dashboard response context."""

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    return panels[chart_id]


@pytest.mark.django_db
def test_phase6_context_matrix_schema_is_stable_across_contexts(auth_client, player) -> None:
    """Keep chart schema stable while context inputs change."""

    farming = Preset.objects.create(player=player, name="Farming")
    tournament = Preset.objects.create(player=player, name="Tournament")

    def _run(*, checksum: str, battle_date: datetime, tier: int, preset: Preset) -> None:
        report = BattleReport.objects.create(
            player=player,
            raw_text=f"Battle Report\nCoins earned\t{tier * 100}\n",
            checksum=checksum.ljust(64, "x"),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=player,
            battle_date=battle_date,
            tier=tier,
            wave=10,
            real_time_seconds=10,
            preset=preset,
            preset_name_snapshot=preset.name,
            preset_color_snapshot=preset.badge_color(),
        )

    _run(checksum="ctx1", battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc), tier=1, preset=farming)
    _run(checksum="ctx2", battle_date=datetime(2025, 12, 11, tzinfo=timezone.utc), tier=2, preset=farming)
    _run(checksum="ctx3", battle_date=datetime(2025, 12, 12, tzinfo=timezone.utc), tier=1, preset=tournament)

    contexts = (
        {"charts": ["coins_earned"], "start_date": date(2025, 12, 9)},
        {"charts": ["coins_earned"], "start_date": date(2025, 12, 9), "tier": 1},
        {"charts": ["coins_earned"], "start_date": date(2025, 12, 9), "preset": farming.pk},
        {"charts": ["coins_earned"], "start_date": date(2025, 12, 11), "preset": farming.pk},
    )

    panels = []
    for params in contexts:
        response = auth_client.get("/", params)
        assert response.status_code == 200
        panels.append(_panel(response, chart_id="coins_earned"))

    panel_keys = [set(panel.keys()) for panel in panels]
    assert all(keys == panel_keys[0] for keys in panel_keys)

    dataset_keys = [set(panel["datasets"][0].keys()) for panel in panels]
    assert all(keys == dataset_keys[0] for keys in dataset_keys)


@pytest.mark.django_db
def test_phase6_context_edge_case_preset_with_no_runs_does_not_fallback(auth_client, player) -> None:
    """Do not silently fallback when the selected preset has no matching runs."""

    farming = Preset.objects.create(player=player, name="Farming")
    empty = Preset.objects.create(player=player, name="No Runs")

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned\t100\n",
        checksum="ctx".ljust(64, "c"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc),
        tier=1,
        wave=10,
        real_time_seconds=10,
        preset=farming,
        preset_name_snapshot=farming.name,
        preset_color_snapshot=farming.badge_color(),
    )

    response = auth_client.get(
        "/",
        {
            "charts": ["coins_earned"],
            "start_date": date(2025, 12, 9),
            "preset": empty.pk,
        },
    )
    assert response.status_code == 200
    assert response.context["chart_empty_state"] == "No runs match the current filters."

    panel = _panel(response, chart_id="coins_earned")
    assert panel["labels"] == []
    assert panel["datasets"][0]["data"] == []
