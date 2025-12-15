"""Admin registrations for GameData models."""

from __future__ import annotations

from django.contrib import admin

from gamedata.models import (
    BattleReport,
    BattleReportProgress,
    RunBot,
    RunCombatUltimateWeapon,
    RunGuardian,
    RunUtilityUltimateWeapon,
)


@admin.register(BattleReport)
class BattleReportAdmin(admin.ModelAdmin):
    """Admin configuration for BattleReport."""

    list_display = ("checksum", "parsed_at")
    search_fields = ("checksum",)


@admin.register(BattleReportProgress)
class BattleReportProgressAdmin(admin.ModelAdmin):
    """Admin configuration for BattleReportProgress."""

    list_display = ("battle_report", "battle_date", "tier", "wave", "real_time_seconds", "preset")
    list_filter = ("tier", "preset")


@admin.register(RunBot)
class RunBotAdmin(admin.ModelAdmin):
    """Admin configuration for RunBot."""

    list_display = ("battle_report", "bot_definition")


@admin.register(RunGuardian)
class RunGuardianAdmin(admin.ModelAdmin):
    """Admin configuration for RunGuardian."""

    list_display = ("battle_report", "guardian_chip_definition")


@admin.register(RunCombatUltimateWeapon)
class RunCombatUltimateWeaponAdmin(admin.ModelAdmin):
    """Admin configuration for RunCombatUltimateWeapon."""

    list_display = ("battle_report", "ultimate_weapon_definition")


@admin.register(RunUtilityUltimateWeapon)
class RunUtilityUltimateWeaponAdmin(admin.ModelAdmin):
    """Admin configuration for RunUtilityUltimateWeapon."""

    list_display = ("battle_report", "ultimate_weapon_definition")

