"""Helpers for Calculator Tools dashboard computations."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Iterable

SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 86400

WAVE_DURATION_SECONDS = 26.0
BASE_WAVE_COOLDOWN_SECONDS = 9.0
WAVE_ACCELERATOR_REDUCTION = 0.30


@dataclass(frozen=True, slots=True)
class GameSpeedResult:
    """Computed values for the Game Speed calculator."""

    waves_per_hour: float | None
    expected_waves_per_hour: float | None
    expected_real_time_seconds: float | None
    derived_speed: float | None
    seconds_per_wave: float
    cooldown_seconds: float


@dataclass(frozen=True, slots=True)
class LabSpeedupOption:
    """Configuration for a lab speedup boost option."""

    boost: float
    duration_hours: int
    cost_per_lab: int
    cost_all_labs: int


@dataclass(frozen=True, slots=True)
class LabSpeedupRow:
    """Computed output row for a lab speedup option."""

    boost: float
    duration_hours: int
    boosts_needed: int
    total_cells: int
    research_hours: float


@dataclass(frozen=True, slots=True)
class LabGoal:
    """Mission goal target for lab research time."""

    key: str
    label: str
    total_seconds: int


LAB_GOALS: tuple[LabGoal, ...] = (
    LabGoal(key="goal_12d", label="12 days", total_seconds=12 * SECONDS_PER_DAY),
    LabGoal(key="goal_30d", label="30 days", total_seconds=30 * SECONDS_PER_DAY),
    LabGoal(
        key="goal_89d",
        label="89d 19h 33m 20s",
        total_seconds=(89 * SECONDS_PER_DAY) + (19 * SECONDS_PER_HOUR) + (33 * 60) + 20,
    ),
)

LAB_UNLOCK_COSTS: tuple[tuple[int, str], ...] = (
    (1, "Free"),
    (2, "100"),
    (3, "400"),
    (4, "1,400"),
    (5, "3,000"),
)

LAB_SPEEDUP_OPTIONS: tuple[LabSpeedupOption, ...] = (
    LabSpeedupOption(boost=1.5, duration_hours=1, cost_per_lab=15, cost_all_labs=75),
    LabSpeedupOption(boost=1.5, duration_hours=8, cost_per_lab=120, cost_all_labs=600),
    LabSpeedupOption(boost=1.5, duration_hours=24, cost_per_lab=360, cost_all_labs=1800),
    LabSpeedupOption(boost=2.0, duration_hours=1, cost_per_lab=100, cost_all_labs=500),
    LabSpeedupOption(boost=2.0, duration_hours=8, cost_per_lab=800, cost_all_labs=4000),
    LabSpeedupOption(boost=2.0, duration_hours=24, cost_per_lab=2400, cost_all_labs=12000),
    LabSpeedupOption(boost=3.0, duration_hours=1, cost_per_lab=840, cost_all_labs=4200),
    LabSpeedupOption(boost=3.0, duration_hours=8, cost_per_lab=6720, cost_all_labs=33600),
    LabSpeedupOption(boost=3.0, duration_hours=24, cost_per_lab=20160, cost_all_labs=100800),
    LabSpeedupOption(boost=4.0, duration_hours=1, cost_per_lab=3360, cost_all_labs=16800),
    LabSpeedupOption(boost=4.0, duration_hours=8, cost_per_lab=26880, cost_all_labs=134400),
    LabSpeedupOption(boost=4.0, duration_hours=24, cost_per_lab=80640, cost_all_labs=403200),
    LabSpeedupOption(boost=5.0, duration_hours=1, cost_per_lab=11900, cost_all_labs=59500),
    LabSpeedupOption(boost=5.0, duration_hours=8, cost_per_lab=95200, cost_all_labs=476000),
    LabSpeedupOption(boost=5.0, duration_hours=24, cost_per_lab=285600, cost_all_labs=1428000),
    LabSpeedupOption(boost=6.0, duration_hours=1, cost_per_lab=60000, cost_all_labs=300000),
    LabSpeedupOption(boost=6.0, duration_hours=8, cost_per_lab=480000, cost_all_labs=2400000),
    LabSpeedupOption(boost=6.0, duration_hours=24, cost_per_lab=1440000, cost_all_labs=7200000),
    LabSpeedupOption(boost=7.0, duration_hours=1, cost_per_lab=250000, cost_all_labs=1250000),
    LabSpeedupOption(boost=7.0, duration_hours=8, cost_per_lab=2000000, cost_all_labs=10000000),
    LabSpeedupOption(boost=7.0, duration_hours=24, cost_per_lab=6000000, cost_all_labs=30000000),
    LabSpeedupOption(boost=8.0, duration_hours=1, cost_per_lab=1000000, cost_all_labs=5000000),
    LabSpeedupOption(boost=8.0, duration_hours=8, cost_per_lab=8000000, cost_all_labs=40000000),
    LabSpeedupOption(boost=8.0, duration_hours=24, cost_per_lab=24000000, cost_all_labs=120000000),
)


def cooldown_seconds(*, wave_accelerator_active: bool) -> float:
    """Return the wave cooldown seconds given Wave Accelerator state."""

    if not wave_accelerator_active:
        return BASE_WAVE_COOLDOWN_SECONDS
    return BASE_WAVE_COOLDOWN_SECONDS * (1.0 - WAVE_ACCELERATOR_REDUCTION)


def seconds_per_wave(*, wave_accelerator_active: bool) -> float:
    """Return total seconds per wave using the baseline wave + cooldown."""

    return WAVE_DURATION_SECONDS + cooldown_seconds(wave_accelerator_active=wave_accelerator_active)


def expected_waves_per_hour(*, game_speed: float, wave_accelerator_active: bool) -> float:
    """Return expected waves/hour for the selected game speed."""

    base_seconds = seconds_per_wave(wave_accelerator_active=wave_accelerator_active)
    return (game_speed * SECONDS_PER_HOUR) / base_seconds


def derive_game_speed(*, waves: int | None, real_time_seconds: int | None, wave_accelerator_active: bool) -> float | None:
    """Derive game speed from observed real time and waves reached."""

    if not waves or not real_time_seconds:
        return None
    if real_time_seconds <= 0:
        return None
    base_seconds = seconds_per_wave(wave_accelerator_active=wave_accelerator_active)
    waves_per_hour = (float(waves) * SECONDS_PER_HOUR) / float(real_time_seconds)
    return (waves_per_hour * base_seconds) / SECONDS_PER_HOUR


def expected_real_time_seconds(
    *, waves: int | None, game_speed: float, wave_accelerator_active: bool
) -> float | None:
    """Return expected real-time seconds for a wave count and game speed."""

    if not waves:
        return None
    base_seconds = seconds_per_wave(wave_accelerator_active=wave_accelerator_active)
    return float(waves) * base_seconds / float(game_speed)


def build_game_speed_result(
    *, waves: int | None, real_time_seconds: int | None, game_speed: float, wave_accelerator_active: bool
) -> GameSpeedResult:
    """Build a GameSpeedResult from run data and calculator inputs."""

    base_seconds = seconds_per_wave(wave_accelerator_active=wave_accelerator_active)
    if not waves or not real_time_seconds or real_time_seconds <= 0:
        return GameSpeedResult(
            waves_per_hour=None,
            expected_waves_per_hour=expected_waves_per_hour(
                game_speed=game_speed, wave_accelerator_active=wave_accelerator_active
            ),
            expected_real_time_seconds=expected_real_time_seconds(
                waves=waves, game_speed=game_speed, wave_accelerator_active=wave_accelerator_active
            ),
            derived_speed=None,
            seconds_per_wave=base_seconds,
            cooldown_seconds=cooldown_seconds(wave_accelerator_active=wave_accelerator_active),
        )
    waves_per_hour = (float(waves) * SECONDS_PER_HOUR) / float(real_time_seconds)
    derived_speed = (waves_per_hour * base_seconds) / SECONDS_PER_HOUR
    return GameSpeedResult(
        waves_per_hour=waves_per_hour,
        expected_waves_per_hour=expected_waves_per_hour(
            game_speed=game_speed, wave_accelerator_active=wave_accelerator_active
        ),
        expected_real_time_seconds=expected_real_time_seconds(
            waves=waves, game_speed=game_speed, wave_accelerator_active=wave_accelerator_active
        ),
        derived_speed=derived_speed,
        seconds_per_wave=base_seconds,
        cooldown_seconds=cooldown_seconds(wave_accelerator_active=wave_accelerator_active),
    )


def progress_seconds_from_parts(
    *, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0
) -> int:
    """Convert day/hour/minute/second inputs into total seconds."""

    return (days * SECONDS_PER_DAY) + (hours * SECONDS_PER_HOUR) + (minutes * 60) + seconds


def lab_speedup_rows(
    *, remaining_seconds: int, labs_unlocked: int, options: Iterable[LabSpeedupOption] = LAB_SPEEDUP_OPTIONS
) -> list[LabSpeedupRow]:
    """Compute speedup requirements and totals for lab boosts."""

    rows: list[LabSpeedupRow] = []
    remaining_hours = max(remaining_seconds, 0) / float(SECONDS_PER_HOUR)
    labs = max(1, labs_unlocked)
    for option in options:
        research_hours = float(labs) * option.boost * float(option.duration_hours)
        boosts_needed = 0 if remaining_hours <= 0 else int(ceil(remaining_hours / research_hours))
        total_cells = boosts_needed * option.cost_per_lab * labs
        rows.append(
            LabSpeedupRow(
                boost=option.boost,
                duration_hours=option.duration_hours,
                boosts_needed=boosts_needed,
                total_cells=total_cells,
                research_hours=research_hours * boosts_needed,
            )
        )
    return rows


def format_duration(*, total_seconds: int) -> str:
    """Format seconds into a compact duration label."""

    seconds = max(total_seconds, 0)
    days = seconds // SECONDS_PER_DAY
    seconds -= days * SECONDS_PER_DAY
    hours = seconds // SECONDS_PER_HOUR
    seconds -= hours * SECONDS_PER_HOUR
    minutes = seconds // 60
    seconds -= minutes * 60
    parts: list[str] = []
    if days:
        parts.append(f"{days}d")
    if hours or days:
        parts.append(f"{hours}h")
    if minutes or hours or days:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)
