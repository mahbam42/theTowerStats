"""Unit tests for v28 Battle Report metric extraction."""

from __future__ import annotations

import pytest

from analysis.raw_text_metrics import extract_raw_text_metrics

pytestmark = pytest.mark.unit


@pytest.mark.golden
def test_extract_raw_text_metrics_handles_v28_sections() -> None:
    """Extract v28 metrics using section-aware aliases."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tApr 10, 2026 18:12",
            "Game Time\t2d 13h 1m 2s",
            "Real Time\t13h 18m 35s",
            "Tier\t3",
            "Wave\t6402",
            "Killed By\tFast",
            "Coins Earned\t2.24B",
            "Coins Per Hour\t168.38M",
            "Cells Earned\t4.64K",
            "Cells Per Hour\t349",
            "Records",
            "Highest Coins / Minute\t26.45M",
            "Largest Wave Skip\t5",
            "Most Coins From Wave Skip\t0",
            "Most Cells From Wave Skip\t0",
            "Largest Smart Missile Stack\t0",
            "Largest Golden Combo\t0",
            "Most Coins From Golden Combo\t0",
            "Largest Inner Landmine Charge\t0",
            "Damage",
            "Black Hole\t57.15S",
            "Attack Chip\t12.00T",
            "Damage Taken",
            "Tower\t157.83T",
            "Wall\t37.24T",
            "Health Regenerated",
            "Lifesteal\t5.65T",
            "Tower Health Regen\t56.72B",
            "Wall Health Regen\t0",
            "Damage Blocked",
            "Defense %\t1.36q",
            "Defense Absolute\t6.94T",
            "Chrono Field\t0",
            "Chain Thunder\t0",
            "Flame Bot\t0",
            "Primordial Collapse\t69.25T",
            "Negative Mass Projector\t0",
            "Utility",
            "Enemy Attack Levels Skipped\t1643",
            "Enemy Health Levels Skipped\t1406",
            "Counts",
            "Projectiles Count\t18.36M",
            "Land Mines Spawned\t210909",
            "Death Defy\t0",
            "Hits Absorbed By Energy Shield\t189",
            "Nuke\t0",
            "Second Wind\t1",
            "Demon Mode\t0",
            "Coins",
            "Critical Coin\t0",
            "Bounty Coins\t32.49M",
            "Currencies",
            "Gems\t146",
            "Ad Gems\t120",
            "Medals\t7",
            "Fetch Gems\t28",
            "Enemies Destroyed By",
            "Projectiles\t20403",
            "Black Hole\t2048",
            "Other\t36",
            "",
        ]
    )

    extracted = extract_raw_text_metrics(raw_text)

    assert extracted["game_reported_coins_per_hour"].value == 168_380_000.0
    assert extracted["game_reported_cells_per_hour"].value == 349.0
    assert extracted["record_highest_coins_per_minute"].value == 26_450_000.0
    assert extracted["record_largest_wave_skip"].value == 5.0
    assert extracted["black_hole_damage"].raw_value == "57.15S"
    assert extracted["black_hole_damage"].value > 0
    assert extracted["guardian_damage"].value == 12_000_000_000_000.0
    assert extracted["tower_damage_taken"].value == 157_830_000_000_000.0
    assert extracted["wall_damage_taken"].value == 37_240_000_000_000.0
    assert extracted["lifesteal_healing"].value == 5_650_000_000_000.0
    assert extracted["tower_health_regen"].value == 56_720_000_000.0
    assert extracted["defense_percent_blocked_damage"].value == 1_360_000_000_000_000.0
    assert extracted["primordial_collapse_blocked_damage"].value == 69_250_000_000_000.0
    assert extracted["enemy_attack_levels_skipped"].value == 1643.0
    assert extracted["projectiles_count"].value == 18_360_000.0
    assert extracted["energy_shield_hits_absorbed"].value == 189.0
    assert extracted["guardian_coins_stolen"].value == 32_490_000.0
    assert extracted["gems_earned"].value == 146.0
    assert extracted["ad_gems_earned"].value == 120.0
    assert extracted["medals_earned"].value == 7.0
    assert extracted["guardian_gems_fetched"].value == 28.0
    assert extracted["enemies_destroyed_by_projectiles"].value == 20_403.0
    assert extracted["enemies_destroyed_by_black_hole"].value == 2048.0
    assert extracted["enemies_destroyed_by_other"].value == 36.0


@pytest.mark.regression
def test_extract_raw_text_metrics_keeps_legacy_black_hole_labels() -> None:
    """Extract older Black Hole labels, including the no-space bug variant."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Black Hole Damage\t16.46s",
            "Coins From Black Hole\t1.25M",
            "Blackhole Damage\t17.46s",
            "",
        ]
    )

    extracted = extract_raw_text_metrics(raw_text)

    assert extracted["black_hole_damage"].raw_value in {"16.46s", "17.46s"}
    assert extracted["black_hole_damage"].value > 0
    assert extracted["coins_from_black_hole"].value == 1_250_000.0
