"""Phase 7 snapshot behavior tests."""

from __future__ import annotations

import json
from datetime import date
from datetime import datetime, timezone

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_chart_snapshot_is_immutable(player) -> None:
    """Reject updates to a ChartSnapshot after creation."""

    from player_state.models import ChartSnapshot

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
def test_snapshot_load_applies_builder_and_context(auth_client, player) -> None:
    """Loading a snapshot via snapshot_id pre-fills builder inputs and renders its chart."""

    from analysis.chart_config_dto import ChartConfigDTO, ChartContextDTO
    from analysis.raw_text_metrics import extract_raw_text_metrics
    from gamedata.models import BattleReport, BattleReportDerivedMetrics, BattleReportProgress
    from core.charting.snapshot_codec import encode_chart_config_dto
    from player_state.models import ChartSnapshot

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned\t1,200\nCoins From Golden Tower\t200\n",
        checksum="snapload".ljust(64, "x"),
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
    extracted = extract_raw_text_metrics(report.raw_text)
    BattleReportDerivedMetrics.objects.create(
        battle_report=report,
        player=player,
        values={key: parsed.value for key, parsed in extracted.items()},
        raw_values={key: parsed.raw_value for key, parsed in extracted.items()},
    )

    dto = ChartConfigDTO(
        metrics=("coins_earned", "coins_from_golden_tower"),
        chart_type="line",
        group_by="time",
        comparison="none",
        smoothing="none",
        context=ChartContextDTO(start_date=date(2025, 12, 9), end_date=None),
    )
    snapshot = ChartSnapshot.objects.create(
        player=player,
        name="Coins snapshot",
        target="charts",
        config=encode_chart_config_dto(dto),
    )

    response = auth_client.get("/", {"snapshot_id": snapshot.id})
    assert response.status_code == 200
    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    assert "chart_builder_custom" in panels


@pytest.mark.django_db
def test_snapshot_can_render_on_ultimate_weapons_dashboard(auth_client, player) -> None:
    """Ultimate Weapons dashboard can render snapshots saved with target=ultimate_weapons."""

    from analysis.chart_config_dto import ChartConfigDTO, ChartContextDTO
    from analysis.raw_text_metrics import extract_raw_text_metrics
    from core.charting.snapshot_codec import encode_chart_config_dto
    from gamedata.models import BattleReport, BattleReportDerivedMetrics, BattleReportProgress
    from player_state.models import ChartSnapshot
    from tests.test_ultimate_weapon_progress_dashboard import _uw_with_three_parameters

    _uw_with_three_parameters(slug="golden_tower", name="Golden Tower")

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned\t1,200\nCoins From Golden Tower\t200\n",
        checksum="uwsnap".ljust(64, "x"),
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
    extracted = extract_raw_text_metrics(report.raw_text)
    BattleReportDerivedMetrics.objects.create(
        battle_report=report,
        player=player,
        values={key: parsed.value for key, parsed in extracted.items()},
        raw_values={key: parsed.raw_value for key, parsed in extracted.items()},
    )

    dto = ChartConfigDTO(
        metrics=("coins_earned",),
        chart_type="line",
        group_by="time",
        comparison="none",
        smoothing="none",
        context=ChartContextDTO(start_date=date(2025, 12, 9), end_date=None),
    )
    snapshot = ChartSnapshot.objects.create(
        player=player,
        name="UW snapshot",
        target="ultimate_weapons",
        config=encode_chart_config_dto(dto),
    )

    response = auth_client.get(reverse("core:ultimate_weapon_progress"), {"uw_snapshot_id": snapshot.id})
    assert response.status_code == 200
    assert response.context["uw_snapshot_chart_json"] is not None
