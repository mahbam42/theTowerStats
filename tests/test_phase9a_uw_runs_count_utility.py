"""Phase 9A regression tests for UW usage metrics."""

from __future__ import annotations

from dataclasses import dataclass

from analysis.metrics import MetricComputeConfig, compute_metric_value
from core.parsers.battle_report import extract_ultimate_weapon_usage


@dataclass(frozen=True, slots=True)
class _UWDef:
    name: str


@dataclass(frozen=True, slots=True)
class _UWRow:
    ultimate_weapon_definition: _UWDef


@dataclass(frozen=True, slots=True)
class _Record:
    run_utility_uws: tuple[_UWRow, ...]


def test_uw_runs_count_includes_utility_uw_rows() -> None:
    """uw_runs_count treats run_utility_uws as a valid usage source."""

    record = _Record(run_utility_uws=(_UWRow(ultimate_weapon_definition=_UWDef(name="Chain Lightning")),))
    value, _used, _assumptions = compute_metric_value(
        "uw_runs_count",
        record=record,
        coins=None,
        cash=None,
        cells=None,
        reroll_shards=None,
        wave=None,
        real_time_seconds=None,
        context=None,
        entity_type=None,
        entity_name="Chain Lightning",
        config=MetricComputeConfig(),
    )
    assert value == 1.0


def test_extract_ultimate_weapon_usage_parses_combat_and_utility_lists() -> None:
    """Parse comma-delimited UW usage lists from Battle Report-style lines."""

    combat, utility = extract_ultimate_weapon_usage(
        "\n".join(
            [
                "Battle Report",
                "Combat Ultimate Weapons: Chain Lightning, Golden Tower",
                "Utility Ultimate Weapons: Chrono Field",
            ]
        )
    )
    assert combat == ("Chain Lightning", "Golden Tower")
    assert utility == ("Chrono Field",)


@dataclass(frozen=True, slots=True)
class _TextRecord:
    raw_text: str


def test_uw_runs_count_uses_observed_battle_report_metrics_when_available() -> None:
    """uw_runs_count prefers observed Battle Report metrics over UW name lists."""

    record = _TextRecord(raw_text="Battle Report\nBlack Hole Damage\t12.5K\n")
    value, _used, _assumptions = compute_metric_value(
        "uw_runs_count",
        record=record,
        coins=None,
        cash=None,
        cells=None,
        reroll_shards=None,
        wave=None,
        real_time_seconds=None,
        context=None,
        entity_type=None,
        entity_name="Black Hole",
        config=MetricComputeConfig(),
    )
    assert value == 1.0


def test_uw_runs_count_observed_metric_requires_positive_value() -> None:
    """Zero-valued metrics do not count as observed UW usage."""

    record = _TextRecord(raw_text="Battle Report\nChain Lightning Damage\t0\n")
    value, _used, _assumptions = compute_metric_value(
        "uw_runs_count",
        record=record,
        coins=None,
        cash=None,
        cells=None,
        reroll_shards=None,
        wave=None,
        real_time_seconds=None,
        context=None,
        entity_type=None,
        entity_name="Chain Lightning",
        config=MetricComputeConfig(),
    )
    assert value == 0.0
