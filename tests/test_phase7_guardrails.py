"""Phase 7 performance guardrail tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest


@pytest.mark.django_db
def test_chart_guardrail_limits_data_points(auth_client, player) -> None:
    """Fail safely when chart label counts exceed the maximum."""

    from gamedata.models import BattleReport, BattleReportProgress

    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    reports = []
    for idx in range(405):
        reports.append(
            BattleReport(
                player=player,
                raw_text="Battle Report\nCoins earned\t1\n",
                checksum=f"guardrail{idx}".ljust(64, "x"),
            )
        )
    BattleReport.objects.bulk_create(reports)

    progresses = []
    for idx, report in enumerate(
        BattleReport.objects.filter(player=player, checksum__startswith="guardrail").order_by("id")
    ):
        progresses.append(
            BattleReportProgress(
                battle_report=report,
                player=player,
                battle_date=start + timedelta(days=idx),
                tier=1,
                wave=10,
                real_time_seconds=60,
                coins_earned=1,
            )
    )
    BattleReportProgress.objects.bulk_create(progresses)

    response = auth_client.get("/", {"charts": ["coins_earned"], "start_date": "2025-01-01"})
    assert response.status_code == 200

    panel = next(p for p in response.context["chart_panels"] if p["id"] == "coins_earned")
    assert panel["error"] and "Too many data points" in panel["error"]
