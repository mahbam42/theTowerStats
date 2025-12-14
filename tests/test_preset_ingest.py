"""Integration tests for preset label ingestion."""

from __future__ import annotations

import pytest

from core.models import PresetTag, RunProgress
from core.services import ingest_battle_report


@pytest.mark.django_db
def test_ingest_battle_report_associates_preset_tag() -> None:
    """Create a preset tag when provided and associate it with the run."""

    _, created = ingest_battle_report(
        "Battle Report\nCoins: 1,200\nTier: 1\nWave: 10\nReal Time: 10m\n",
        preset_name="Farming",
    )
    assert created is True

    preset = PresetTag.objects.get(name="Farming")
    progress = RunProgress.objects.select_related("preset_tag").get()
    assert progress.preset_tag == preset

