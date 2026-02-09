"""Helpers for aggregating Lifetime Stats modal metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

from analysis.battle_report_extract import extract_numeric_value
from analysis.metrics import MetricComputeConfig, compute_metric_value, get_metric_definition
from analysis.quantity import UnitType
from core.upgradeables import total_currency_invested_for_parameter, total_stones_invested_for_parameter
from gamedata.models import BattleReport
from player_state.models import Player, PlayerGuardianChipParameter, PlayerUltimateWeaponParameter


@dataclass(frozen=True, slots=True)
class LifetimeStatSpec:
    """Definition for a Lifetime Stats metric row.

    Attributes:
        key: Stable key used for metric lookup.
        label: Display label shown in the modal.
        group: Display group name (Economy, Combat, Utility).
        source: Source category for the metric value.
        unit: Optional display unit override.
        raw_label: Raw text label to extract when `source="raw_text"`.
        raw_unit: Unit type to use when extracting raw text metrics.
    """

    key: str
    label: str
    group: str
    source: Literal["analysis", "raw_text", "player_state"]
    unit: str | None = None
    raw_label: str | None = None
    raw_unit: UnitType | None = None


def build_lifetime_stat_groups(
    *,
    records: Iterable[BattleReport],
    player: Player,
) -> list[dict[str, object]]:
    """Build grouped Lifetime Stats rows for rendering.

    Args:
        records: BattleReport records to aggregate.
        player: Player owning the data for player-state metrics.

    Returns:
        List of group dictionaries containing ordered metric rows.
    """

    specs = (
        LifetimeStatSpec(
            key="coins_earned",
            label="Coins Earned",
            group="Economy",
            source="analysis",
        ),
        LifetimeStatSpec(
            key="cash_earned",
            label="Cash Earned",
            group="Economy",
            source="analysis",
        ),
        LifetimeStatSpec(
            key="cells_earned",
            label="Cells Earned",
            group="Economy",
            source="analysis",
        ),
        LifetimeStatSpec(
            key="reroll_shards_earned",
            label="Reroll Shards Earned",
            group="Economy",
            source="analysis",
        ),
        LifetimeStatSpec(
            key="stones_spent",
            label="Stones Spent",
            group="Economy",
            source="player_state",
            unit="stones",
        ),
        LifetimeStatSpec(
            key="bits_spent",
            label="Bits Spent",
            group="Economy",
            source="player_state",
            unit="bits",
        ),
        LifetimeStatSpec(
            key="damage_dealt",
            label="Damage Dealt",
            group="Combat",
            source="analysis",
        ),
        LifetimeStatSpec(
            key="thorn_damage",
            label="Thorn Damage",
            group="Combat",
            source="analysis",
        ),
        LifetimeStatSpec(
            key="enemies_destroyed_total",
            label="Enemies Destroyed",
            group="Combat",
            source="analysis",
        ),
        LifetimeStatSpec(
            key="enemies_destroyed_by_orbs",
            label="Orb Kills",
            group="Combat",
            source="analysis",
        ),
        LifetimeStatSpec(
            key="enemies_destroyed_by_death_ray",
            label="Death Ray Kills",
            group="Combat",
            source="analysis",
        ),
        LifetimeStatSpec(
            key="waves_reached",
            label="Waves Completed",
            group="Utility",
            source="analysis",
        ),
        LifetimeStatSpec(
            key="free_upgrades_total",
            label="Free Upgrades",
            group="Utility",
            source="analysis",
        ),
        LifetimeStatSpec(
            key="interest_earned",
            label="Interest Earned",
            group="Utility",
            source="analysis",
        ),
        LifetimeStatSpec(
            key="waves_skipped",
            label="Waves Skipped",
            group="Utility",
            source="raw_text",
            unit="waves",
            raw_label="Waves Skipped",
            raw_unit=UnitType.count,
        ),
    )

    totals = {
        "stones_spent": _total_stones_spent(player=player),
        "bits_spent": _total_bits_spent(player=player),
    }

    groups: dict[str, list[dict[str, object]]] = {"Economy": [], "Combat": [], "Utility": []}
    for spec in specs:
        if spec.source == "player_state":
            value = float(totals.get(spec.key, 0))
            groups[spec.group].append(
                {
                    "key": spec.key,
                    "label": spec.label,
                    "unit": spec.unit or "",
                    "numeric_value": value,
                }
            )
            continue

        if spec.source == "raw_text":
            count, total = _sum_raw_text_metric(
                records,
                metric_key=spec.key,
                raw_label=spec.raw_label,
                raw_unit=spec.raw_unit,
            )
            unit = spec.unit or ""
            groups[spec.group].append(
                {
                    "key": spec.key,
                    "label": spec.label,
                    "unit": unit,
                    "numeric_value": total if count else None,
                }
            )
            continue

        count, total = _sum_analysis_metric(records, metric_key=spec.key)
        metric_unit = spec.unit or get_metric_definition(spec.key).unit
        groups[spec.group].append(
            {
                "key": spec.key,
                "label": spec.label,
                "unit": metric_unit,
                "numeric_value": total if count else None,
            }
        )

    ordered_groups: list[dict[str, object]] = []
    for group_name in ("Economy", "Combat", "Utility"):
        rows = groups.get(group_name, [])
        ordered_groups.append(
            {
                "id": group_name.casefold().replace(" ", "-"),
                "label": group_name,
                "metrics": rows,
            }
        )
    return ordered_groups


def _sum_analysis_metric(records: Iterable[BattleReport], *, metric_key: str) -> tuple[int, float | None]:
    """Return the summed metric value and contributing count for a metric key."""

    total = 0.0
    count = 0
    for record in records:
        value = _metric_value(record, metric_key=metric_key)
        if value is None:
            continue
        total += float(value)
        count += 1
    if not count:
        return 0, None
    return count, total


def _metric_value(record: BattleReport, *, metric_key: str) -> float | None:
    """Compute a metric value using the analysis engine helpers."""

    progress = getattr(record, "run_progress", record)
    coins = getattr(progress, "coins_earned", None)
    cash = getattr(progress, "cash_earned", None)
    interest_earned = getattr(progress, "interest_earned", None)
    cells = getattr(progress, "cells_earned", None)
    reroll_shards = getattr(progress, "reroll_shards_earned", None)
    wave = getattr(progress, "wave", None)
    real_time_seconds = getattr(progress, "real_time_seconds", None)

    value, _used, _assumptions = compute_metric_value(
        metric_key,
        record=record,
        coins=coins,
        cash=cash,
        interest_earned=interest_earned,
        cells=cells,
        reroll_shards=reroll_shards,
        wave=wave,
        real_time_seconds=real_time_seconds,
        context=None,
        entity_type=None,
        entity_name=None,
        config=MetricComputeConfig(monte_carlo=None),
    )
    return value


def _sum_raw_text_metric(
    records: Iterable[BattleReport],
    *,
    metric_key: str,
    raw_label: str | None,
    raw_unit: UnitType | None,
) -> tuple[int, float | None]:
    """Return the summed raw-text metric value and contributing count."""

    if not raw_label or raw_unit is None:
        return 0, None
    total = 0.0
    count = 0
    for record in records:
        derived = getattr(record, "derived_metrics", None)
        values = getattr(derived, "values", None) if derived is not None else None
        if isinstance(values, dict) and metric_key in values:
            value = values.get(metric_key)
        else:
            raw_text = getattr(record, "raw_text", None)
            if not isinstance(raw_text, str):
                continue
            parsed = extract_numeric_value(raw_text, label=raw_label, unit_type=raw_unit)
            if parsed is None:
                continue
            value = parsed.value
        if value is None:
            continue
        total += float(value)
        count += 1
    if not count:
        return 0, None
    return count, total


def _total_stones_spent(*, player: Player) -> int:
    """Return total stones spent using Ultimate Weapon upgrade data."""

    total = 0
    params = PlayerUltimateWeaponParameter.objects.filter(player=player).select_related("parameter_definition")
    for param in params:
        param_def = param.parameter_definition
        if param_def is None:
            continue
        total += total_stones_invested_for_parameter(
            parameter_definition=param_def,
            level=param.level,
        )
    return total


def _total_bits_spent(*, player: Player) -> int:
    """Return total bits spent using Guardian Chip upgrade data."""

    total = 0
    params = PlayerGuardianChipParameter.objects.filter(player=player).select_related("parameter_definition")
    for param in params:
        param_def = param.parameter_definition
        if param_def is None:
            continue
        total += total_currency_invested_for_parameter(
            parameter_definition=param_def,
            level=param.level,
        )
    return total
