"""Integration tests for dashboard context default injection."""

from __future__ import annotations

import re
from datetime import datetime, timezone

import pytest

from gamedata.models import BattleReport, BattleReportProgress

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_dashboard_renders_start_and_end_values_on_initial_load(auth_client) -> None:
    """Start/end inputs should include values even when omitted from the URL."""

    response = auth_client.get("/")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert re.search(r'name="start_date"[^>]*value="[^"]+"', content)
    assert re.search(r'name="end_date"[^>]*value="[^"]+"', content)


@pytest.mark.django_db
def test_dashboard_all_button_redirects_to_first_run_through_today(auth_client, player) -> None:
    """All range should redirect to earliest run date through today."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="c" * 64,
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

    response = auth_client.get("/", {"event_shift": "all"})
    assert response.status_code == 302
    location = response["Location"]
    assert "start_date=2025-12-10" in location
    assert "end_date=" in location


@pytest.mark.django_db
def test_dashboard_context_buttons_are_in_requested_order(auth_client) -> None:
    """Arrange the Context controls as fields, nav buttons, then actions."""

    response = auth_client.get("/")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    end_idx = content.index('name="end_date"')
    prev_idx = content.index('value="-1">Previous')
    builder_idx = content.index('id="open-chart-builder"')
    assert end_idx < prev_idx < builder_idx
