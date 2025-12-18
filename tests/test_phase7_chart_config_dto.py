"""Phase 7 DTO contract tests for ChartConfigDTO."""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest


@pytest.mark.django_db
def test_chart_config_dto_validation_rejects_mixed_units() -> None:
    """ChartConfigDTO validation rejects mixed-unit metric selections."""

    from analysis.chart_config_dto import ChartConfigDTO, ChartContextDTO
    from analysis.chart_config_validator import validate_chart_config_dto
    from analysis.series_registry import DEFAULT_REGISTRY

    dto = ChartConfigDTO(
        metrics=("coins_earned", "waves_reached"),
        chart_type="line",
        group_by="time",
        comparison="none",
        smoothing="none",
        context=ChartContextDTO(start_date=None, end_date=None),
    )
    result = validate_chart_config_dto(dto, registry=DEFAULT_REGISTRY)
    assert result.is_valid is False
    assert any("Mixed units" in err for err in result.errors)


@pytest.mark.django_db
def test_chart_config_dto_analysis_returns_dtos_only() -> None:
    """Analysis executes ChartConfigDTO and returns chart DTO outputs."""

    from analysis.chart_config_dto import ChartConfigDTO, ChartContextDTO
    from analysis.chart_config_engine import ChartDataDTO, analyze_chart_config_dto
    from analysis.series_registry import DEFAULT_REGISTRY
    from gamedata.models import BattleReport, BattleReportProgress

    report = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned\t1,200\n",
        checksum="dtocontract".ljust(64, "x"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        coins_earned=1200,
    )

    dto = ChartConfigDTO(
        metrics=("coins_earned",),
        chart_type="line",
        group_by="time",
        comparison="none",
        smoothing="none",
        context=ChartContextDTO(start_date=date(2025, 12, 9), end_date=None),
    )

    chart = analyze_chart_config_dto(
        BattleReport.objects.select_related("run_progress").order_by("run_progress__battle_date"),
        config=dto,
        registry=DEFAULT_REGISTRY,
        moving_average_window=None,
        entity_selections={},
    )
    assert isinstance(chart, ChartDataDTO)
    assert chart.labels == ["2025-12-10"]
    assert chart.datasets
    assert chart.datasets[0].values == [1200.0]

