"""Unit tests for Calculator Tools helpers."""

from __future__ import annotations

import pytest

from core.calculators import (
    LabSpeedupOption,
    build_game_speed_result,
    lab_speedup_rows,
    progress_seconds_from_parts,
)

pytestmark = pytest.mark.unit


def test_build_game_speed_result_baseline() -> None:
    """Derived game speed equals 1.0 at baseline wave timing."""

    waves = 100
    real_time_seconds = int(35 * waves)
    result = build_game_speed_result(
        waves=waves,
        real_time_seconds=real_time_seconds,
        game_speed=1.0,
        wave_accelerator_active=False,
        reduction_pct=0.0,
    )

    assert result.waves_per_hour == pytest.approx(3600 / 35, rel=1e-6)
    assert result.derived_speed == pytest.approx(1.0, rel=1e-6)


def test_lab_speedup_rows_compute_boosts_and_costs() -> None:
    """Lab speedup rows compute boosts and total cell costs."""

    option = LabSpeedupOption(boost=2.0, duration_hours=1, cost_per_lab=100, cost_all_labs=500)
    rows = lab_speedup_rows(remaining_seconds=10 * 3600, labs_unlocked=2, options=[option])

    assert len(rows) == 1
    row = rows[0]
    assert row.boosts_needed == 5
    assert row.total_cells == 1000
    assert row.research_hours == pytest.approx(10.0)
    assert row.research_seconds == 36000
    assert row.max_boosts is None
    assert row.possible_by_deadline is None


def test_progress_seconds_from_parts() -> None:
    """Progress parts sum into total seconds."""

    assert progress_seconds_from_parts(days=1, hours=2, minutes=3, seconds=4) == 93784


def test_lab_speedup_rows_deadline_flags() -> None:
    """Deadline flags reflect remaining time constraints."""

    option = LabSpeedupOption(boost=2.0, duration_hours=1, cost_per_lab=10, cost_all_labs=10)
    rows = lab_speedup_rows(
        remaining_seconds=10 * 3600,
        labs_unlocked=1,
        options=[option],
        available_seconds=4 * 3600,
    )

    row = rows[0]
    assert row.max_boosts == 4
    assert row.possible_by_deadline is False
