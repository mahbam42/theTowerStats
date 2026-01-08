"""Integration tests for unknown unit suffix capture."""

from __future__ import annotations

import pytest

from core.parsers.battle_report import record_unrecognized_unit_suffixes
from definitions.models import Unit

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_record_unrecognized_unit_suffixes_creates_unit_row() -> None:
    """Record unknown compact suffixes in the Unit table."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Coins earned\t1.25Z",
            "Cash earned\t$2.00Q",
            "Real Time\t1h 2m 3s",
            "",
        ]
    )

    recorded = record_unrecognized_unit_suffixes(raw_text)

    assert recorded == {"z"}
    unit = Unit.objects.get(name="magnitude suffix z")
    assert unit.symbol == "z"
    assert unit.kind == Unit.Kind.UNKNOWN
    assert not Unit.objects.filter(name="magnitude suffix Q").exists()
