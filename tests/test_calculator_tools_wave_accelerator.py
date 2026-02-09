"""Integration tests for Wave Accelerator calculator values."""

from __future__ import annotations

import pytest

from core.calculators import wave_accelerator_reduction_percent
from definitions.models import CardDefinition
from player_state.models import PlayerCard

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_wave_accelerator_reduction_percent_uses_card_level(player) -> None:
    """Wave Accelerator reduction is selected from the card effect per level."""

    card_def = CardDefinition.objects.create(
        name="Wave Accelerator",
        slug="wave-accelerator",
        effect_raw="30% / 35% / 40%",
    )
    PlayerCard.objects.create(
        player=player,
        card_definition=card_def,
        card_slug=card_def.slug,
        stars_unlocked=2,
        inventory_count=0,
    )

    assert wave_accelerator_reduction_percent(player=player) == 35.0
