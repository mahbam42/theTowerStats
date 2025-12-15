"""Model smoke tests for Phase 3 structural completeness."""

from __future__ import annotations

import pytest

from core.models import (
    BotDefinition,
    BotLevel,
    BotParameter,
    CardDefinition,
    CardLevel,
    CardParameter,
    CardSlot,
    GuardianChipDefinition,
    GuardianChipLevel,
    GuardianChipParameter,
    PlayerBot,
    PlayerCard,
    PlayerGuardianChip,
    PlayerUltimateWeapon,
    PresetTag,
    UltimateWeaponDefinition,
    UltimateWeaponLevel,
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

    level = CardLevel.objects.create(card_definition=card, level=1, star=1, raw_row={"Bonus": "10%"})
    CardParameter.objects.create(
        card_definition=card,
        card_level=level,
        key="Bonus",
        raw_value="10",
        unit=percent,
    )
    CardSlot.objects.create(slot_number=1, unlock_cost_raw="Free")

    bot_def = BotDefinition.objects.create(name="Amplify Bot")
    bot_level = BotLevel.objects.create(bot_definition=bot_def, level=1, raw_row={})
    BotParameter.objects.create(bot_definition=bot_def, bot_level=bot_level, key="Bonus", raw_value="?", unit=None)

    chip_def = GuardianChipDefinition.objects.create(name="Core")
    chip_level = GuardianChipLevel.objects.create(guardian_chip_definition=chip_def, level=1, raw_row={})
    GuardianChipParameter.objects.create(
        guardian_chip_definition=chip_def, guardian_chip_level=chip_level, key="Effect", raw_value="?", unit=None
    )

    uw_def = UltimateWeaponDefinition.objects.create(name="Golden Tower")
    uw_level = UltimateWeaponLevel.objects.create(ultimate_weapon_definition=uw_def, level=1, raw_row={})
    UltimateWeaponParameter.objects.create(
        ultimate_weapon_definition=uw_def,
        ultimate_weapon_level=uw_level,
        key="Cooldown",
        raw_value="120",
        unit=None,
    )

    PlayerCard.objects.create(card_definition=card, owned=True, level=1, star=1)
    PlayerGuardianChip.objects.create(chip_name="Core", owned=False)
    PlayerUltimateWeapon.objects.create(weapon_name="Golden Tower", unlocked=False)
    PlayerBot.objects.create(bot_name="Amplify Bot", unlocked=False)

