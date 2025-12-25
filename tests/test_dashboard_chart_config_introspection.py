"""Integration tests for dashboard chart config introspection/rendering."""

from __future__ import annotations

import json
from datetime import datetime

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_dashboard_form_chart_choices_come_from_chart_configs(auth_client) -> None:
    """Populate the charts multiselect from ChartConfig introspection."""

    response = auth_client.get("/")
    assert response.status_code == 200
    chart_form = response.context["chart_form"]
    flat: dict[str, str] = {}
    for group_label, group_choices in chart_form.fields["charts"].choices:
        _ = group_label
        for value, label in group_choices:
            flat[str(value)] = str(label)
    assert "coins_earned" in flat


@pytest.mark.django_db
def test_dashboard_renders_derived_formula_chart(auth_client, player) -> None:
    """Render a derived chart (coins per wave) from config-driven formulas."""

    from datetime import date as date_type, timezone

    from gamedata.models import BattleReport, BattleReportProgress

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="coinsperwave".ljust(64, "x"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    response = auth_client.get("/", {"charts": ["coins_per_wave"], "start_date": date_type(2025, 12, 9)})
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_per_wave"]
    assert panel["labels"] == ["2025-12-10"]
    assert panel["datasets"][0]["data"] == [12.0]
