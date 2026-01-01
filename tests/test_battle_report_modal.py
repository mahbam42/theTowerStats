"""Integration tests for the Battle Report modal payload."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from django.urls import reverse

from gamedata.models import BattleReport, BattleReportProgress

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_battle_report_modal_payload_includes_metrics_and_raw_text(auth_client, player) -> None:
    """Modal payload returns raw text and metric link metadata."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="z" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        tier=2,
        wave=100,
        real_time_seconds=600,
        coins_earned=1200,
        coins_earned_raw="1,200",
        gem_blocks_tapped=3,
    )

    response = auth_client.get(reverse("core:battle_report_modal", args=[report.id]))
    assert response.status_code == 200

    payload = response.json()
    assert payload["ok"] is True
    assert payload["report"]["raw_text"].startswith("Battle Report")

    metrics = {metric["key"]: metric for metric in payload["report"]["metrics"]}
    assert metrics["coins_earned"]["chart_id"] == "coins_earned"
    assert metrics["coins_per_hour"]["value"] == "7,200.00"
    assert metrics["gem_blocks_tapped"]["chart_id"] is None
    assert metrics["interest_earned"]["value"] == "—"
