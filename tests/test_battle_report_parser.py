"""Golden tests for Phase 1 Battle Report parsing."""

from __future__ import annotations

from datetime import datetime, timezone

from core.parsers.battle_report import parse_battle_report


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
