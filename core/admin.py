"""Admin registrations for the core app."""

from __future__ import annotations

from django.contrib import admin

from core.models import GameData, PresetTag, RunProgress


@admin.register(GameData)
class GameDataAdmin(admin.ModelAdmin):
    """Admin configuration for GameData."""

    list_display = ("parsed_at", "checksum")
    search_fields = ("checksum",)


@admin.register(RunProgress)
class RunProgressAdmin(admin.ModelAdmin):
    """Admin configuration for RunProgress."""

    list_display = ("battle_date", "tier", "preset_tag", "wave", "real_time_seconds")
    list_filter = ("tier", "preset_tag")


@admin.register(PresetTag)
class PresetTagAdmin(admin.ModelAdmin):
    """Admin configuration for PresetTag."""

    list_display = ("name",)
    search_fields = ("name",)
