"""Golden tests for Phase 1 Battle Report parsing."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from core.parsers.battle_report import parse_battle_report

pytestmark = [pytest.mark.unit, pytest.mark.golden]


def test_parse_battle_report_extracts_phase1_fields() -> None:
    """Parse a Battle Report and extract the Phase 1 field subset."""

    raw_text = (
        "Battle Report\n"
        "Battle Date: 2025-12-01 13:45:00\n"
        "Tier: 6\n"
        "Wave: 1234\n"
        "Real Time: 1h 2m 3s\n"
        "Coins: 999999\n"
        "Some New Label: ignored\n"
    )

    parsed = parse_battle_report(raw_text)

    assert parsed.checksum == "4c9e9a56f3285c18778c9a41457dae385bd90d05ab34b0d95429ae6afeea3ce3"
    assert parsed.battle_date == datetime(2025, 12, 1, 13, 45, 0, tzinfo=timezone.utc)
    assert parsed.tier == 6
    assert parsed.wave == 1234
    assert parsed.real_time_seconds == 3723
    assert parsed.killed_by is None
    assert parsed.coins_earned_raw == "999999"
    assert parsed.coins_earned == 999_999
    assert parsed.cash_earned is None
    assert parsed.interest_earned is None
    assert parsed.gem_blocks_tapped is None
    assert parsed.cells_earned is None
    assert parsed.reroll_shards_earned is None


def test_parse_battle_report_handles_tab_separated_labels() -> None:
    """Parse tab-separated Battle Reports with month-name dates."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 07, 2025 21:59",
            "Game Time\t10h 24m 52s",
            "Real Time\t2h 17m 23s",
            "Tier\t7",
            "Wave\t1301",
            "Killed By\tBoss",
            "Coins earned\t17.55M",
            "Coins per hour\t7.67M",
            "Cash earned\t$55.90M",
            "Interest earned\t$2.13M",
            "Gem Blocks Tapped\t3",
            "Cells Earned\t346",
            "Reroll Shards Earned\t373",
            "",
        ]
    )

    parsed = parse_battle_report(raw_text)

    assert parsed.checksum == "3b022c38f8187f076fb643de672a503d4c264c844b71f363fdddb796b96db44b"
    assert parsed.battle_date == datetime(2025, 12, 7, 21, 59, tzinfo=timezone.utc)
    assert parsed.tier == 7
    assert parsed.wave == 1301
    assert parsed.real_time_seconds == 8243
    assert parsed.killed_by == "Boss"
    assert parsed.coins_earned_raw == "17.55M"
    assert parsed.coins_earned == 17_550_000
    assert parsed.cash_earned_raw == "$55.90M"
    assert parsed.cash_earned == 55_900_000
    assert parsed.interest_earned_raw == "$2.13M"
    assert parsed.interest_earned == 2_130_000
    assert parsed.gem_blocks_tapped == 3
    assert parsed.cells_earned == 346
    assert parsed.reroll_shards_earned == 373


def test_parse_battle_report_handles_real_game_sample() -> None:
    """Parse a real-game Battle Report sample with tabbed labels."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 14, 2025 01:39",
            "Game Time\t1h 10m 22s",
            "Real Time\t17m 35s",
            "Tier\t11",
            "Wave\t121",
            "Killed By\tBoss",
            "Coins earned\t1.24M",
            "Coins per hour\t4.24M",
            "Cash earned\t$1.00M",
            "Interest earned\t$220.24K",
            "Gem Blocks Tapped\t1",
            "Cells Earned\t0",
            "Reroll Shards Earned\t94",
            "Combat",
            "Damage dealt\t39.01T",
            "Damage Taken\t138.06M",
            "Damage Taken Wall\t78.73M",
            "Damage Taken While Berserked\t306.37M",
            "Damage Gain From Berserk\tx8.00",
            "Death Defy\t0",
            "Lifesteal\t0",
            "Projectiles Damage\t6.25T",
            "Projectiles Count\t15.18K",
            "Thorn damage\t24.65B",
            "Orb Damage\t108.40B",
            "Enemies Hit by Orbs\t8",
            "Land Mine Damage\t313.35B",
            "Land Mines Spawned\t1448",
            "Rend Armor Damage\t0",
            "Death Ray Damage\t0",
            "Smart Missile Damage\t349.94B",
            "Inner Land Mine Damage\t0",
            "Chain Lightning Damage\t31.81T",
            "Death Wave Damage\t21.50B",
            "Tagged by Deathwave\t120",
            "Swamp Damage\t0",
            "Black Hole Damage\t0",
            "Electrons Damage\t0",
            "Utility",
            "Waves Skipped\t0",
            "Recovery Packages\t68",
            "Free Attack Upgrade\t55",
            "Free Defense Upgrade\t68",
            "Free Utility Upgrade\t68",
            "HP From Death Wave\t0.00",
            "Coins From Death Wave\t2.35K",
            "Cash From Golden Tower\t$140.15K",
            "Coins From Golden Tower\t62.30K",
            "Coins From Black Hole\t0",
            "Coins From Spotlight\t1.76K",
            "Coins From Orb\t0",
            "Coins from Coin Upgrade\t832.21K",
            "Coins from Coin Bonuses\t335.53K",
            "Enemies Destroyed",
            "Total Enemies\t4606",
            "Basic\t3701",
            "Fast\t401",
            "Tank\t311",
            "Ranged\t181",
            "Boss\t12",
            "Protector\t0",
            "Total Elites\t0",
            "Vampires\t0",
            "Rays\t0",
            "Scatters\t0",
            "Saboteur\t0",
            "Commander\t0",
            "Overcharge\t0",
            "Destroyed By Orbs\t8",
            "Destroyed by Thorns\t1",
            "Destroyed by Death Ray\t0",
            "Destroyed by Land Mine\t49",
            "Destroyed in Spotlight\t474",
            "Bots",
            "Flame Bot Damage\t111.15B",
            "Thunder Bot Stuns\t32",
            "Golden Bot Coins Earned\t578",
            "Destroyed in Golden Bot\t34",
            "Guardian",
            "Damage\t21.34B",
            "Summoned enemies\t0",
            "Guardian coins stolen\t0",
            "Coins Fetched\t805",
            "Gems\t0",
            "Medals\t0",
            "Reroll Shards\t0",
            "Cannon Shards\t0",
            "Armor Shards\t0",
            "Generator Shards\t0",
            "Core Shards\t0",
            "Common Modules\t1",
            "Rare Modules\t0",
            "",
        ]
    )

    parsed = parse_battle_report(raw_text)

    assert (
        parsed.checksum
        == "e84c298d16c5a5f5b0863026959efbe6e93873cf57614609bcd961ed7981036d"
    )
    assert parsed.battle_date == datetime(2025, 12, 14, 1, 39, tzinfo=timezone.utc)
    assert parsed.tier == 11
    assert parsed.wave == 121
    assert parsed.real_time_seconds == 1055
    assert parsed.killed_by == "Boss"
    assert parsed.coins_earned_raw == "1.24M"
    assert parsed.coins_earned == 1_240_000
    assert parsed.cash_earned_raw == "$1.00M"
    assert parsed.cash_earned == 1_000_000
    assert parsed.interest_earned_raw == "$220.24K"
    assert parsed.interest_earned == 220_240
    assert parsed.gem_blocks_tapped == 1
    assert parsed.cells_earned == 0
    assert parsed.reroll_shards_earned == 94


def test_parse_battle_report_tolerates_missing_sections() -> None:
    """Return partial results when known fields are missing."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Wave\t250",
            "",
        ]
    )

    parsed = parse_battle_report(raw_text)

    assert parsed.wave == 250
    assert parsed.battle_date is None
    assert parsed.tier is None
    assert parsed.real_time_seconds is None


def test_parse_battle_report_tolerates_reordered_and_messy_input() -> None:
    """Handle reordered labels, extra whitespace, and malformed known fields."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "  Wave      3210  ",
            "Tier:\t  not-a-number",
            "Real Time  \t  00:12:34",
            "Battle Date    2025-12-08 01:02",
            "Some New Label Without Value",
            "Another New Label:    ",
            "",
        ]
    )

    parsed = parse_battle_report(raw_text)

    assert parsed.wave == 3210
    assert parsed.tier is None
    assert parsed.real_time_seconds == 754
    assert parsed.battle_date == datetime(2025, 12, 8, 1, 2, tzinfo=timezone.utc)
