"""Admin registrations for player state models."""

from __future__ import annotations

from django.contrib import admin

from player_state.models import (
    Player,
    PlayerBot,
    PlayerBotParameter,
    PlayerCard,
    PlayerGuardianChip,
    PlayerGuardianChipParameter,
    PlayerUltimateWeapon,
    PlayerUltimateWeaponParameter,
    Preset,
)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """Admin configuration for Player."""

    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Preset)
class PresetAdmin(admin.ModelAdmin):
    """Admin configuration for Preset."""

    list_display = ("player", "name", "created_at")
    search_fields = ("name",)
    list_filter = ("player",)


@admin.register(PlayerCard)
class PlayerCardAdmin(admin.ModelAdmin):
    """Admin configuration for PlayerCard."""

    list_display = ("player", "card_slug", "stars_unlocked", "updated_at")
    list_filter = ("player",)


@admin.register(PlayerBot)
class PlayerBotAdmin(admin.ModelAdmin):
    """Admin configuration for PlayerBot."""

    list_display = ("player", "bot_slug", "unlocked", "updated_at")
    list_filter = ("player", "unlocked")


@admin.register(PlayerUltimateWeapon)
class PlayerUltimateWeaponAdmin(admin.ModelAdmin):
    """Admin configuration for PlayerUltimateWeapon."""

    list_display = ("player", "ultimate_weapon_slug", "unlocked", "updated_at")
    list_filter = ("player", "unlocked")


@admin.register(PlayerGuardianChip)
class PlayerGuardianChipAdmin(admin.ModelAdmin):
    """Admin configuration for PlayerGuardianChip."""

    list_display = ("player", "guardian_chip_slug", "unlocked", "updated_at")
    list_filter = ("player", "unlocked")


@admin.register(PlayerBotParameter)
class PlayerBotParameterAdmin(admin.ModelAdmin):
    """Admin configuration for PlayerBotParameter."""

    list_display = ("player_bot", "parameter_definition", "level", "updated_at")


@admin.register(PlayerUltimateWeaponParameter)
class PlayerUltimateWeaponParameterAdmin(admin.ModelAdmin):
    """Admin configuration for PlayerUltimateWeaponParameter."""

    list_display = ("player_ultimate_weapon", "parameter_definition", "level", "updated_at")


@admin.register(PlayerGuardianChipParameter)
class PlayerGuardianChipParameterAdmin(admin.ModelAdmin):
    """Admin configuration for PlayerGuardianChipParameter."""

    list_display = ("player_guardian_chip", "parameter_definition", "level", "updated_at")

