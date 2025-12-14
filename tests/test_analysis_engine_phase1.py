"""Golden tests for Phase 1 Analysis Engine behavior."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import cast

from analysis.engine import analyze_runs
from analysis.dto import RunProgressInput
from core.parsers.battle_report import parse_battle_report
from pytest import approx


def test_analyze_runs_computes_coins_per_hour() -> None:
    """Compute coins/hour for a set of run-progress inputs."""

    inputs = [
        RunProgressInput(
            battle_date=datetime(2025, 12, 1, 0, 0, tzinfo=timezone.utc),
            coins=900_000,
            wave=900,
            real_time_seconds=1800,
        ),
        RunProgressInput(
            battle_date=datetime(2025, 12, 2, 0, 0, tzinfo=timezone.utc),
            coins=1_800_000,
            wave=1800,
            real_time_seconds=3600,
        ),
    ]

    result = analyze_runs(inputs)

    assert len(result.runs) == 2
    assert result.runs[0].coins_per_hour == 1_800_000.0
    assert result.runs[1].coins_per_hour == 1_800_000.0


def test_analyze_runs_parses_compact_coins_from_raw_text() -> None:
    """Parse `Coins: 4.24M` from raw text and compute coins/hour."""

    @dataclass(frozen=True)
    class Progress:
        battle_date: datetime | None
        wave: int | None
        real_time_seconds: int | None
        coins: int | None = None

    @dataclass(frozen=True)
    class Record:
        raw_text: str
        parsed_at: datetime
        run_progress: Progress

    record = Record(
        raw_text="Battle Report\nCoins: 4.24M\n",
        parsed_at=datetime(2025, 12, 1, 0, 0, tzinfo=timezone.utc),
        run_progress=Progress(battle_date=None, wave=1, real_time_seconds=3600),
    )

    result = analyze_runs([record])
    assert len(result.runs) == 1
    assert result.runs[0].coins_per_hour == 4_240_000.0


def test_analyze_runs_handles_tabbed_battle_report_raw_text() -> None:
    """Parse coins and metadata from a tab-separated Battle Report."""

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

    parsed_report = parse_battle_report(raw_text)
    battle_date = cast(datetime, parsed_report.battle_date)
    wave = cast(int, parsed_report.wave)
    real_time_seconds = cast(int, parsed_report.real_time_seconds)

    @dataclass(frozen=True)
    class Record:
        raw_text: str
        parsed_at: datetime
        run_progress: RunProgressInput

    assert parsed_report.battle_date is not None
    assert parsed_report.wave is not None
    assert parsed_report.real_time_seconds is not None

    record = Record(
        raw_text=raw_text,
        parsed_at=datetime(2025, 12, 7, 22, 0, tzinfo=timezone.utc),
        run_progress=RunProgressInput(
            battle_date=parsed_report.battle_date,
            coins=None,
            wave=parsed_report.wave,
            real_time_seconds=parsed_report.real_time_seconds,
        ),
    )

    result = analyze_runs([record])

    assert len(result.runs) == 1
    assert result.runs[0].battle_date == datetime(2025, 12, 7, 21, 59, tzinfo=timezone.utc)
    assert result.runs[0].coins_per_hour == approx(7_664_685.18743176, rel=1e-6)


def test_analyze_runs_handles_real_game_sample() -> None:
    """Compute rate metrics from the real-game Battle Report sample."""

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

    parsed_report = parse_battle_report(raw_text)
    battle_date = cast(datetime, parsed_report.battle_date)
    wave = cast(int, parsed_report.wave)
    real_time_seconds = cast(int, parsed_report.real_time_seconds)

    @dataclass(frozen=True)
    class Record:
        raw_text: str
        parsed_at: datetime
        run_progress: RunProgressInput

    record = Record(
        raw_text=raw_text,
        parsed_at=datetime(2025, 12, 14, 1, 40, tzinfo=timezone.utc),
        run_progress=RunProgressInput(
            battle_date=battle_date,
            coins=None,
            wave=wave,
            real_time_seconds=real_time_seconds,
        ),
    )

    result = analyze_runs([record])

    assert len(result.runs) == 1
    assert result.runs[0].battle_date == datetime(2025, 12, 14, 1, 39, tzinfo=timezone.utc)
    assert result.runs[0].coins_per_hour == approx(4_231_279.62085308, rel=1e-6)


def test_analyze_runs_ignores_incomplete_records() -> None:
    """Skip records missing required fields instead of raising errors."""

    @dataclass(frozen=True)
    class Progress:
        battle_date: datetime | None
        wave: int | None
        real_time_seconds: int | None
        coins: int | None = None

    incomplete = Progress(
        battle_date=None,
        wave=10,
        real_time_seconds=None,
        coins=100,
    )

    result = analyze_runs([incomplete])

    assert isinstance(result.runs, tuple)
    assert len(result.runs) == 0
