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
    cells_earned: int | None = None
    reroll_shards_earned: int | None = None


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


def test_resource_per_hour_metrics_use_real_time() -> None:
    """Derive cells/hour and reroll shards/hour from real time."""

    record = Record(
        raw_text="Battle Report\nReal Time\t30m 0s\n",
        parsed_at=datetime(2025, 12, 21, 13, 20, tzinfo=timezone.utc),
        run_progress=Progress(
            battle_date=datetime(2025, 12, 21, 13, 18, tzinfo=timezone.utc),
            wave=100,
            real_time_seconds=1800,
            cells_earned=600,
            reroll_shards_earned=1200,
        ),
        derived_metrics=None,
    )

    cells = analyze_metric_series([record], metric_key="cells_per_hour")
    shards = analyze_metric_series([record], metric_key="reroll_shards_per_hour")

    assert cells.points[0].value == 1200.0
    assert shards.points[0].value == 2400.0


@pytest.mark.golden
def test_bot_metrics_extract_from_raw_text() -> None:
    """Extract bot metrics used for run usage inference."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 14, 2025 01:39",
            "Flame Bot Damage\t402.59T",
            "Thunder Bot Stuns\t1.79K",
            "Golden Bot Coins Earned\t57.74K",
            "",
        ]
    )

    extracted = extract_raw_text_metrics(raw_text)

    assert extracted["flame_bot_damage"].raw_value == "402.59T"
    assert extracted["flame_bot_damage"].value == 402_590_000_000_000.0
    assert extracted["thunder_bot_stuns"].raw_value == "1.79K"
    assert extracted["thunder_bot_stuns"].value == 1790.0
    assert extracted["golden_bot_coins_earned"].raw_value == "57.74K"
    assert extracted["golden_bot_coins_earned"].value == 57_740.0


@pytest.mark.golden
def test_free_upgrades_metrics_extract_and_total() -> None:
    """Extract free upgrade metrics and derive the total."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 14, 2025 01:39",
            "Real Time\t17m 35s",
            "Utility",
            "Free Attack Upgrade\t55",
            "Free Defense Upgrade\t68",
            "Free Utility Upgrade\t68",
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

    attack = analyze_metric_series([record], metric_key="free_attack_upgrades")
    defense = analyze_metric_series([record], metric_key="free_defense_upgrades")
    utility = analyze_metric_series([record], metric_key="free_utility_upgrades")
    total = analyze_metric_series([record], metric_key="free_upgrades_total")

    assert attack.points[0].value == 55.0
    assert defense.points[0].value == 68.0
    assert utility.points[0].value == 68.0
    assert total.points[0].value == 191.0


@pytest.mark.golden
def test_recovery_packages_extract_from_raw_text() -> None:
    """Extract recovery packages from raw Battle Report text."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 14, 2025 01:39",
            "Recovery Packages\t573",
            "",
        ]
    )

    extracted = extract_raw_text_metrics(raw_text)

    assert extracted["recovery_packages"].raw_value == "573"
    assert extracted["recovery_packages"].value == 573.0


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


@pytest.mark.golden
def test_enemies_destroyed_group_totals() -> None:
    """Derive grouped enemy totals for common, elite, and fleet types."""

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

    common = analyze_metric_series([record], metric_key="enemies_destroyed_common")
    elite = analyze_metric_series([record], metric_key="enemies_destroyed_elite")
    fleet = analyze_metric_series([record], metric_key="enemies_destroyed_fleet")

    assert common.points[0].value == 78_711.0
    assert elite.points[0].value == 51.0
    assert fleet.points[0].value == 0.0


@pytest.mark.regression
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
    assert sum(v for v in values if isinstance(v, (int, float))) == pytest.approx(100.0)
