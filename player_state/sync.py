"""Idempotent utilities for aligning Player State with Definitions.

These helpers ensure player progress rows exist for every known definition and
re-link existing player rows by slug when definitions are rebuilt.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.db import transaction

from definitions.models import (
    BotDefinition,
    BotParameterDefinition,
    CardDefinition,
    GuardianChipDefinition,
    GuardianChipParameterDefinition,
    UltimateWeaponDefinition,
    UltimateWeaponParameterDefinition,
)
from player_state.models import (
    Player,
    PlayerBot,
    PlayerBotParameter,
    PlayerCard,
    PlayerGuardianChip,
    PlayerGuardianChipParameter,
    PlayerUltimateWeapon,
    PlayerUltimateWeaponParameter,
)


@dataclass(frozen=True, slots=True)
class SyncSummary:
    """Counts for a sync run."""

    created_player_rows: int = 0
    updated_player_rows: int = 0
    created_parameter_rows: int = 0


def sync_player_state_from_definitions(*, player_name: str = "default", write: bool) -> SyncSummary:
    """Ensure Player State rows exist and link to Definitions by slug.

    Args:
        player_name: Player.name to sync (single-player default is "default").
        write: When True, persist changes. When False, compute counts only.

    Returns:
        SyncSummary containing created/updated counts.
    """

    if not write:
        return SyncSummary()

    with transaction.atomic():
        player, _ = Player.objects.get_or_create(name=player_name)
        summary = SyncSummary()
        summary = _sync_cards(player, summary=summary)
        summary = _sync_bots(player, summary=summary)
        summary = _sync_ultimate_weapons(player, summary=summary)
        summary = _sync_guardians(player, summary=summary)
        return summary


def _sync_cards(player: Player, *, summary: SyncSummary) -> SyncSummary:
    """Create PlayerCard rows and link them to CardDefinition by slug."""

    for definition in CardDefinition.objects.all():
        obj, created = PlayerCard.objects.get_or_create(
            player=player,
            card_slug=definition.slug,
            defaults={"card_definition": definition, "stars_unlocked": 0},
        )
        if created:
            summary = SyncSummary(
                created_player_rows=summary.created_player_rows + 1,
                updated_player_rows=summary.updated_player_rows,
                created_parameter_rows=summary.created_parameter_rows,
            )
        elif obj.card_definition_id != definition.id:
            obj.card_definition = definition
            obj.save(update_fields=["card_definition", "updated_at"])
            summary = SyncSummary(
                created_player_rows=summary.created_player_rows,
                updated_player_rows=summary.updated_player_rows + 1,
                created_parameter_rows=summary.created_parameter_rows,
            )
    return summary


def _sync_bots(player: Player, *, summary: SyncSummary) -> SyncSummary:
    """Create PlayerBot rows and link them to BotDefinition by slug."""

    for definition in BotDefinition.objects.all():
        bot, created = PlayerBot.objects.get_or_create(
            player=player,
            bot_slug=definition.slug,
            defaults={"bot_definition": definition, "unlocked": False},
        )
        if created:
            summary = SyncSummary(
                created_player_rows=summary.created_player_rows + 1,
                updated_player_rows=summary.updated_player_rows,
                created_parameter_rows=summary.created_parameter_rows,
            )
        elif bot.bot_definition_id != definition.id:
            bot.bot_definition = definition
            bot.save(update_fields=["bot_definition", "updated_at"])
            summary = SyncSummary(
                created_player_rows=summary.created_player_rows,
                updated_player_rows=summary.updated_player_rows + 1,
                created_parameter_rows=summary.created_parameter_rows,
            )

        for param_def in BotParameterDefinition.objects.filter(bot_definition=definition):
            _, created_param = PlayerBotParameter.objects.get_or_create(
                player_bot=bot, parameter_definition=param_def, defaults={"level": 0}
            )
            if created_param:
                summary = SyncSummary(
                    created_player_rows=summary.created_player_rows,
                    updated_player_rows=summary.updated_player_rows,
                    created_parameter_rows=summary.created_parameter_rows + 1,
                )
    return summary


def _sync_ultimate_weapons(player: Player, *, summary: SyncSummary) -> SyncSummary:
    """Create PlayerUltimateWeapon rows and link them to UltimateWeaponDefinition by slug."""

    for definition in UltimateWeaponDefinition.objects.all():
        uw, created = PlayerUltimateWeapon.objects.get_or_create(
            player=player,
            ultimate_weapon_slug=definition.slug,
            defaults={"ultimate_weapon_definition": definition, "unlocked": False},
        )
        if created:
            summary = SyncSummary(
                created_player_rows=summary.created_player_rows + 1,
                updated_player_rows=summary.updated_player_rows,
                created_parameter_rows=summary.created_parameter_rows,
            )
        elif uw.ultimate_weapon_definition_id != definition.id:
            uw.ultimate_weapon_definition = definition
            uw.save(update_fields=["ultimate_weapon_definition", "updated_at"])
            summary = SyncSummary(
                created_player_rows=summary.created_player_rows,
                updated_player_rows=summary.updated_player_rows + 1,
                created_parameter_rows=summary.created_parameter_rows,
            )

        for param_def in UltimateWeaponParameterDefinition.objects.filter(
            ultimate_weapon_definition=definition
        ):
            _, created_param = PlayerUltimateWeaponParameter.objects.get_or_create(
                player_ultimate_weapon=uw, parameter_definition=param_def, defaults={"level": 0}
            )
            if created_param:
                summary = SyncSummary(
                    created_player_rows=summary.created_player_rows,
                    updated_player_rows=summary.updated_player_rows,
                    created_parameter_rows=summary.created_parameter_rows + 1,
                )
    return summary


def _sync_guardians(player: Player, *, summary: SyncSummary) -> SyncSummary:
    """Create PlayerGuardianChip rows and link them to GuardianChipDefinition by slug."""

    for definition in GuardianChipDefinition.objects.all():
        chip, created = PlayerGuardianChip.objects.get_or_create(
            player=player,
            guardian_chip_slug=definition.slug,
            defaults={"guardian_chip_definition": definition, "unlocked": False},
        )
        if created:
            summary = SyncSummary(
                created_player_rows=summary.created_player_rows + 1,
                updated_player_rows=summary.updated_player_rows,
                created_parameter_rows=summary.created_parameter_rows,
            )
        elif chip.guardian_chip_definition_id != definition.id:
            chip.guardian_chip_definition = definition
            chip.save(update_fields=["guardian_chip_definition", "updated_at"])
            summary = SyncSummary(
                created_player_rows=summary.created_player_rows,
                updated_player_rows=summary.updated_player_rows + 1,
                created_parameter_rows=summary.created_parameter_rows,
            )

        for param_def in GuardianChipParameterDefinition.objects.filter(
            guardian_chip_definition=definition
        ):
            _, created_param = PlayerGuardianChipParameter.objects.get_or_create(
                player_guardian_chip=chip, parameter_definition=param_def, defaults={"level": 0}
            )
            if created_param:
                summary = SyncSummary(
                    created_player_rows=summary.created_player_rows,
                    updated_player_rows=summary.updated_player_rows,
                    created_parameter_rows=summary.created_parameter_rows + 1,
                )
    return summary

