"""Regression tests for Prompt 37 chart metrics and guardrails."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pytest

from analysis.engine import analyze_metric_series
from analysis.raw_text_metrics import extract_raw_text_metrics
from analysis.series_registry import DEFAULT_REGISTRY
from core.charting.render import render_chart
from core.charting.schema import ChartConfig, ChartFilters, ChartSeriesConfig, ChartUI, DateRangeFilterConfig

pytestmark = pytest.mark.unit


@dataclass(frozen=True)
class Progress:
    """Minimal run-progress shape for analysis engine tests."""

    battle_date: datetime | None
    wave: int | None
    real_time_seconds: int | None
    cash_earned: int | None = None


@dataclass(frozen=True)
class Record:
    """Record wrapper exposing raw_text and run_progress."""

    raw_text: str
    parsed_at: datetime
    run_progress: Progress
    derived_metrics: object | None = None


def _derived_metrics(raw_text: str) -> object:
    """Return a derived-metrics stub from raw Battle Report text."""

    extracted = extract_raw_text_metrics(raw_text)
    return type(
        "DerivedMetrics",
        (),
        {
            "values": {key: parsed.value for key, parsed in extracted.items()},
            "raw_values": {key: parsed.raw_value for key, parsed in extracted.items()},
        },
    )()


def test_enemies_destroyed_total_ignores_battle_report_totals() -> None:
    """Derive enemies destroyed by summing per-type rows (ignoring Total Enemies/Elites)."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 21, 2025 13:18",
            "Real Time\t2h 46m 15s",
            "Tier\t8",
            "Wave\t1141",
            "Enemies Destroyed",
            "Total Enemies\t79462",
            "Basic\t49365",
            "Fast\t10418",
            "Tank\t11021",
            "Ranged\t7777",
            "Boss\t114",
            "Protector\t130",
            "Total Elites\t51",
            "Vampires\t19",
            "Rays\t12",
            "Scatters\t20",
            "Saboteur\t0",
            "Commander\t0",
            "Overcharge\t0",
            "",
        ]
    )
    record = Record(
        raw_text=raw_text,
        parsed_at=datetime(2025, 12, 21, 13, 20, tzinfo=timezone.utc),
        run_progress=Progress(
            battle_date=datetime(2025, 12, 21, 13, 18, tzinfo=timezone.utc),
            wave=1141,
            real_time_seconds=60,
        ),
        derived_metrics=_derived_metrics(raw_text),
    )

    result = analyze_metric_series([record], metric_key="enemies_destroyed_total")
    assert len(result.points) == 1
    assert result.points[0].value == 78_876.0


def test_cash_residual_derived_from_named_sources() -> None:
    """Compute residual cash as cash earned minus interest and Golden Tower cash."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 21, 2025 13:18",
            "Cash earned\t$43.25M",
            "Interest earned\t$2.26M",
            "Cash From Golden Tower\t$17.75M",
            "",
        ]
    )
    record = Record(
        raw_text=raw_text,
        parsed_at=datetime(2025, 12, 21, 13, 20, tzinfo=timezone.utc),
        run_progress=Progress(
            battle_date=datetime(2025, 12, 21, 13, 18, tzinfo=timezone.utc),
            wave=1,
            real_time_seconds=60,
            cash_earned=43_250_000,
        ),
        derived_metrics=_derived_metrics(raw_text),
    )

    result = analyze_metric_series([record], metric_key="cash_from_other_sources")
    assert len(result.points) == 1
    assert result.points[0].value == 23_240_000.0


def test_donut_renders_percent_labels_and_optional_percent_values() -> None:
    """Render distribution donuts with percent labels, and percent-value mode when requested."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 14, 2025 01:39",
            "Real Time\t17m 35s",
            "Utility",
            "Coins From Death Wave\t2.00K",
            "Coins From Golden Tower\t6.00K",
            "",
        ]
    )
    record = Record(
        raw_text=raw_text,
        parsed_at=datetime(2025, 12, 14, 1, 40, tzinfo=timezone.utc),
        run_progress=Progress(
            battle_date=datetime(2025, 12, 14, 1, 39, tzinfo=timezone.utc),
            wave=1,
            real_time_seconds=60,
        ),
        derived_metrics=_derived_metrics(raw_text),
    )

    config = ChartConfig(
        id="donut_test",
        title="Donut test",
        description=None,
        category="economy",
        domain="economy",
        semantic_type="contribution",
        chart_type="donut",
        donut_value_mode="percent",
        metric_series=(
            ChartSeriesConfig(metric_key="coins_from_death_wave"),
            ChartSeriesConfig(metric_key="coins_from_golden_tower"),
        ),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(
                enabled=True,
                default_start=datetime(2025, 12, 9, tzinfo=timezone.utc),
            )
        ),
        ui=ChartUI(show_by_default=False, selectable=True, order=0),
    )

    rendered = render_chart(
        config=config,
        records=[record],
        registry=DEFAULT_REGISTRY,
        granularity="daily",
        moving_average_window=None,
        entity_selections={},
    )

    assert rendered.unit == "%"
    labels = rendered.data["labels"]
    assert all(label.endswith("%)") for label in labels)
    dataset = rendered.data["datasets"][0]
    values = dataset["data"]
    assert sum(v for v in values if v is not None) == pytest.approx(100.0)
