"""Integration tests for per-run chart granularity."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from gamedata.models import BattleReport, BattleReportProgress

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_dashboard_per_run_granularity_emits_distinct_labels(auth_client, player) -> None:
    """Per-run granularity should keep multiple runs on the same date distinct."""

    report_a = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="a" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=report_a,
        player=player,
        battle_date=datetime(2025, 12, 10, 1, 0, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        coins_earned=1200,
    )

    report_b = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="b" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=report_b,
        player=player,
        battle_date=datetime(2025, 12, 10, 1, 0, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        coins_earned=2400,
    )

    response = auth_client.get(
        "/",
        {
            "charts": ["coins_earned"],
            "start_date": "2025-12-09",
            "end_date": "2025-12-22",
            "granularity": "per_run",
        },
    )
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_earned"]
    labels = panel["labels"]
    assert len(labels) == 2
    assert any(f"Run {report_a.id}" in label for label in labels)
    assert any(f"Run {report_b.id}" in label for label in labels)

    values = panel["datasets"][0]["data"]
    assert sorted(v for v in values if v is not None) == [1200.0, 2400.0]

