"""Admin registrations for the core app."""

from __future__ import annotations

from django.contrib import admin

from core.models import (
    BotParameter,
    CardDefinition,
    CardLevel,
    CardParameter,
    CardSlot,
    GameData,
    GuardianChipParameter,
    PlayerBot,
    PlayerCard,
    PlayerGuardianChip,
    PlayerUltimateWeapon,
    PresetTag,
    RunProgress,
    UltimateWeaponParameter,
    Unit,
    WikiData,
)


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


@admin.register(WikiData)
class WikiDataAdmin(admin.ModelAdmin):
    """Admin configuration for WikiData."""

    list_display = ("canonical_name", "entity_id", "source_section", "parse_version", "last_seen", "deprecated")
    list_filter = ("source_section", "parse_version", "deprecated")
    search_fields = ("canonical_name", "entity_id", "page_url")


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    """Admin configuration for Unit."""

    list_display = ("name", "kind", "symbol")
    list_filter = ("kind",)
    search_fields = ("name", "symbol")


@admin.register(CardDefinition)
class CardDefinitionAdmin(admin.ModelAdmin):
    """Admin configuration for CardDefinition."""

    list_display = ("name", "wiki_entity_id")
    search_fields = ("name", "wiki_entity_id", "wiki_page_url")
    filter_horizontal = ("preset_tags",)


@admin.register(CardParameter)
class CardParameterAdmin(admin.ModelAdmin):
    """Admin configuration for CardParameter."""

    list_display = ("card_definition", "key", "raw_value", "unit", "source_wikidata")
    list_filter = ("unit",)
    search_fields = ("card_definition__name", "key", "raw_value")


@admin.register(CardLevel)
class CardLevelAdmin(admin.ModelAdmin):
    """Admin configuration for CardLevel."""

    list_display = ("card_definition", "level", "star", "source_wikidata")
    list_filter = ("star",)
    search_fields = ("card_definition__name",)


@admin.register(CardSlot)
class CardSlotAdmin(admin.ModelAdmin):
    """Admin configuration for CardSlot."""

    list_display = ("slot_number", "unlock_cost_raw")
    search_fields = ("unlock_cost_raw",)


@admin.register(BotParameter)
class BotParameterAdmin(admin.ModelAdmin):
    """Admin configuration for BotParameter."""

    list_display = ("bot_name", "key", "raw_value", "unit", "source_wikidata")
    list_filter = ("unit",)
    search_fields = ("bot_name", "key", "raw_value")


@admin.register(GuardianChipParameter)
class GuardianChipParameterAdmin(admin.ModelAdmin):
    """Admin configuration for GuardianChipParameter."""

    list_display = ("chip_name", "key", "raw_value", "unit", "source_wikidata")
    list_filter = ("unit",)
    search_fields = ("chip_name", "key", "raw_value")


@admin.register(UltimateWeaponParameter)
class UltimateWeaponParameterAdmin(admin.ModelAdmin):
    """Admin configuration for UltimateWeaponParameter."""

    list_display = ("weapon_name", "key", "raw_value", "unit", "source_wikidata")
    list_filter = ("unit",)
    search_fields = ("weapon_name", "key", "raw_value")


@admin.register(PlayerCard)
class PlayerCardAdmin(admin.ModelAdmin):
    """Admin configuration for PlayerCard."""

    list_display = ("card_definition", "owned", "level", "star", "updated_at")
    list_filter = ("owned",)
    search_fields = ("card_definition__name",)


@admin.register(PlayerGuardianChip)
class PlayerGuardianChipAdmin(admin.ModelAdmin):
    """Admin configuration for PlayerGuardianChip."""

    list_display = ("chip_name", "owned", "level", "star", "updated_at")
    list_filter = ("owned",)
    search_fields = ("chip_name",)


@admin.register(PlayerUltimateWeapon)
class PlayerUltimateWeaponAdmin(admin.ModelAdmin):
    """Admin configuration for PlayerUltimateWeapon."""

    list_display = ("weapon_name", "unlocked", "level", "star", "updated_at")
    list_filter = ("unlocked",)
    search_fields = ("weapon_name",)


@admin.register(PlayerBot)
class PlayerBotAdmin(admin.ModelAdmin):
    """Admin configuration for PlayerBot."""

    list_display = ("bot_name", "unlocked", "level", "updated_at")
    list_filter = ("unlocked",)
    search_fields = ("bot_name",)
