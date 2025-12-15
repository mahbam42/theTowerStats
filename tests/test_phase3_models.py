"""Model smoke tests for Phase 3 structural completeness."""

from __future__ import annotations

import pytest

from core.models import (
    BotParameter,
    CardDefinition,
    CardLevel,
    CardParameter,
    CardSlot,
    GuardianChipParameter,
    PlayerBot,
    PlayerCard,
    PlayerGuardianChip,
    PlayerUltimateWeapon,
    PresetTag,
    UltimateWeaponParameter,
    Unit,
)


@pytest.mark.django_db
def test_phase3_models_create_minimal_rows() -> None:
    """Create minimal rows for Phase 3 models to ensure migrations apply cleanly."""

    percent = Unit.objects.create(name="percent", symbol="%", kind=Unit.Kind.PERCENT)
    farming = PresetTag.objects.create(name="Farming")

    card = CardDefinition.objects.create(name="Damage")
    card.preset_tags.add(farming)

    CardParameter.objects.create(
        card_definition=card,
        key="Bonus",
        raw_value="10",
        unit=percent,
    )
    CardLevel.objects.create(card_definition=card, level=1, star=1, raw_row={"Bonus": "10%"})
    CardSlot.objects.create(slot_number=1, unlock_cost_raw="Free")

    UltimateWeaponParameter.objects.create(weapon_name="Golden Tower", key="Cooldown", raw_value="120", unit=None)
    GuardianChipParameter.objects.create(chip_name="Core", key="Effect", raw_value="?", unit=None)
    BotParameter.objects.create(bot_name="Amplify Bot", key="Bonus", raw_value="?", unit=None)

    PlayerCard.objects.create(card_definition=card, owned=True, level=1, star=1)
    PlayerGuardianChip.objects.create(chip_name="Core", owned=False)
    PlayerUltimateWeapon.objects.create(weapon_name="Golden Tower", unlocked=False)
    PlayerBot.objects.create(bot_name="Amplify Bot", unlocked=False)

