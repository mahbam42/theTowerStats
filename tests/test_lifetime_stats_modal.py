"""Integration tests for the Lifetime Stats modal payload."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from django.urls import reverse

from analysis.raw_text_metrics import extract_raw_text_metrics
from gamedata.models import BattleReport, BattleReportDerivedMetrics, BattleReportProgress

pytestmark = pytest.mark.integration


def _create_report(
    *,
    player,
    raw_text: str,
    battle_date: datetime,
    coins: int,
    cash: int,
    interest: int,
    cells: int,
    reroll_shards: int,
    wave: int,
    real_time_seconds: int,
) -> BattleReport:
    """Create a BattleReport with progress + derived metrics."""

    report = BattleReport.objects.create(
        player=player,
        raw_text=raw_text,
        checksum=f"checksum-{battle_date.isoformat()}".ljust(64, "x"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=battle_date,
        tier=1,
        wave=wave,
        real_time_seconds=real_time_seconds,
        coins_earned=coins,
        coins_earned_raw=str(coins),
        cash_earned=cash,
        cash_earned_raw=str(cash),
        interest_earned=interest,
        interest_earned_raw=str(interest),
        cells_earned=cells,
        reroll_shards_earned=reroll_shards,
    )
    extracted = extract_raw_text_metrics(raw_text)
    BattleReportDerivedMetrics.objects.create(
        battle_report=report,
        player=player,
        values={key: parsed.value for key, parsed in extracted.items()},
        raw_values={key: parsed.raw_value for key, parsed in extracted.items()},
    )
    return report


def _metric_value(payload: dict[str, object], key: str) -> float | None:
    """Return a numeric metric value from the Lifetime Stats payload."""

    groups = payload.get("groups")
    if not isinstance(groups, list):
        return None
    for group in groups:
        if not isinstance(group, dict):
            continue
        metrics = group.get("metrics")
        if not isinstance(metrics, list):
            continue
        for metric in metrics:
            if not isinstance(metric, dict):
                continue
            if metric.get("key") == key:
                return metric.get("numeric_value")
    return None


def _group_metric_keys(payload: dict[str, object], group_name: str) -> list[str]:
    """Return metric keys for a named Lifetime Stats group."""

    groups = payload.get("groups")
    if not isinstance(groups, list):
        return []
    for group in groups:
        if not isinstance(group, dict) or group.get("label") != group_name:
            continue
        metrics = group.get("metrics")
        if not isinstance(metrics, list):
            return []
        return [str(metric.get("key")) for metric in metrics if isinstance(metric, dict)]
    return []


@pytest.mark.django_db
@pytest.mark.golden
def test_lifetime_stats_modal_returns_totals(auth_client, player) -> None:
    """Lifetime Stats totals sum across all runs."""

    raw_text_a = "\n".join(
        [
            "Battle Report",
            "Records",
            "Highest Coins / Minute\t25",
            "Largest Wave Skip\t2",
            "Most Coins From Wave Skip\t100",
            "Most Cells From Wave Skip\t5",
            "Largest Smart Missile Stack\t3",
            "Largest Golden Combo\t4",
            "Most Coins From Golden Combo\t250",
            "Largest Inner Landmine Charge\t6",
            "Damage dealt\t100",
            "Thorn damage\t20",
            "Waves Skipped\t3",
            "Free Attack Upgrade\t10",
            "Free Defense Upgrade\t15",
            "Free Utility Upgrade\t5",
            "Enemies Destroyed",
            "Basic\t10",
            "Fast\t5",
            "Ranged\t2",
            "Tank\t1",
            "Protector\t0",
            "Destroyed By Orbs\t3",
            "Destroyed by Death Ray\t1",
            "",
        ]
    )
    raw_text_b = "\n".join(
        [
            "Battle Report",
            "Records",
            "Highest Coins / Minute\t40",
            "Largest Wave Skip\t5",
            "Most Coins From Wave Skip\t150",
            "Most Cells From Wave Skip\t7",
            "Largest Smart Missile Stack\t8",
            "Largest Golden Combo\t9",
            "Most Coins From Golden Combo\t300",
            "Largest Inner Landmine Charge\t10",
            "Damage dealt\t200",
            "Thorn damage\t40",
            "Waves Skipped\t4",
            "Free Attack Upgrade\t12",
            "Free Defense Upgrade\t14",
            "Free Utility Upgrade\t9",
            "Enemies Destroyed",
            "Basic\t20",
            "Fast\t10",
            "Ranged\t4",
            "Tank\t2",
            "Protector\t1",
            "Destroyed By Orbs\t4",
            "Destroyed by Death Ray\t2",
            "",
        ]
    )
    _create_report(
        player=player,
        raw_text=raw_text_a,
        battle_date=datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc),
        coins=1000,
        cash=500,
        interest=50,
        cells=10,
        reroll_shards=5,
        wave=100,
        real_time_seconds=3600,
    )
    _create_report(
        player=player,
        raw_text=raw_text_b,
        battle_date=datetime(2026, 2, 1, 12, 0, tzinfo=timezone.utc),
        coins=2400,
        cash=700,
        interest=70,
        cells=20,
        reroll_shards=15,
        wave=200,
        real_time_seconds=3600,
    )

    response = auth_client.get(reverse("core:lifetime_stats_modal"))
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True

    assert _metric_value(payload, "coins_earned") == 3400.0
    assert _metric_value(payload, "cash_earned") == 1200.0
    assert _metric_value(payload, "cells_earned") == 30.0
    assert _metric_value(payload, "reroll_shards_earned") == 20.0
    assert _metric_value(payload, "damage_dealt") == 300.0
    assert _metric_value(payload, "thorn_damage") == 60.0
    assert _metric_value(payload, "enemies_destroyed_total") == 55.0
    assert _metric_value(payload, "enemies_destroyed_by_orbs") == 7.0
    assert _metric_value(payload, "enemies_destroyed_by_death_ray") == 3.0
    assert _metric_value(payload, "waves_reached") == 300.0
    assert _metric_value(payload, "free_upgrades_total") == 65.0
    assert _metric_value(payload, "interest_earned") == 120.0
    assert _metric_value(payload, "waves_skipped") == 7.0
    assert _metric_value(payload, "recent_coins_per_hour") == 2400.0
    assert _metric_value(payload, "record_highest_coins_per_minute") == 40.0
    assert _metric_value(payload, "record_largest_wave_skip") == 5.0
    assert _metric_value(payload, "record_most_coins_from_wave_skip") == 150.0
    assert _metric_value(payload, "record_most_cells_from_wave_skip") == 7.0
    assert _metric_value(payload, "record_largest_smart_missile_stack") == 8.0
    assert _metric_value(payload, "record_largest_golden_combo") == 9.0
    assert _metric_value(payload, "record_most_coins_from_golden_combo") == 300.0
    assert _metric_value(payload, "record_largest_inner_landmine_charge") == 10.0

    assert [group["label"] for group in payload["groups"]] == ["Economy", "Combat", "Utility"]
    assert "record_highest_coins_per_minute" in _group_metric_keys(payload, "Economy")
    assert "record_largest_golden_combo" in _group_metric_keys(payload, "Combat")
    assert "record_largest_wave_skip" in _group_metric_keys(payload, "Utility")


@pytest.mark.django_db
def test_lifetime_stats_modal_applies_custom_date_range(auth_client, player) -> None:
    """Custom date ranges scope Lifetime Stats results."""

    _create_report(
        player=player,
        raw_text="Battle Report\nDamage dealt\t100\n",
        battle_date=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        coins=1000,
        cash=500,
        interest=50,
        cells=10,
        reroll_shards=5,
        wave=100,
        real_time_seconds=3600,
    )
    _create_report(
        player=player,
        raw_text="Battle Report\nDamage dealt\t200\n",
        battle_date=datetime(2026, 2, 1, 12, 0, tzinfo=timezone.utc),
        coins=2400,
        cash=700,
        interest=70,
        cells=20,
        reroll_shards=15,
        wave=200,
        real_time_seconds=3600,
    )

    response = auth_client.get(
        reverse("core:lifetime_stats_modal"),
        {
            "range_mode": "custom",
            "start_date": "2026-02-01",
            "end_date": "2026-02-02",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["run_count"] == 1
    assert _metric_value(payload, "coins_earned") == 2400.0
    assert _metric_value(payload, "recent_coins_per_hour") == 2400.0
