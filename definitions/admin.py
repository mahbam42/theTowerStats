"""Admin registrations for definitions models."""

from __future__ import annotations

from django.contrib import admin

from definitions.models import (
    BotDefinition,
    BotParameterDefinition,
    BotParameterLevel,
    CardDefinition,
    GuardianChipDefinition,
    GuardianChipParameterDefinition,
    GuardianChipParameterLevel,
    UltimateWeaponDefinition,
    UltimateWeaponParameterDefinition,
    UltimateWeaponParameterLevel,
    Unit,
    WikiData,
)


@admin.register(WikiData)
class WikiDataAdmin(admin.ModelAdmin):
    """Admin configuration for WikiData."""

    list_display = ("canonical_name", "entity_id", "parse_version", "source_section", "last_seen", "deprecated")
    list_filter = ("parse_version", "deprecated")
    search_fields = ("canonical_name", "entity_id", "page_url")


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    """Admin configuration for Unit."""

    list_display = ("name", "kind", "symbol")
    list_filter = ("kind",)
    search_fields = ("name",)


@admin.register(CardDefinition)
class CardDefinitionAdmin(admin.ModelAdmin):
    """Admin configuration for CardDefinition."""

    list_display = ("name", "slug", "rarity", "wiki_entity_id")
    search_fields = ("name", "slug", "wiki_entity_id")


@admin.register(BotDefinition)
class BotDefinitionAdmin(admin.ModelAdmin):
    """Admin configuration for BotDefinition."""

    list_display = ("name", "slug", "wiki_entity_id")
    search_fields = ("name", "slug", "wiki_entity_id")


@admin.register(UltimateWeaponDefinition)
class UltimateWeaponDefinitionAdmin(admin.ModelAdmin):
    """Admin configuration for UltimateWeaponDefinition."""

    list_display = ("name", "slug", "wiki_entity_id")
    search_fields = ("name", "slug", "wiki_entity_id")


@admin.register(GuardianChipDefinition)
class GuardianChipDefinitionAdmin(admin.ModelAdmin):
    """Admin configuration for GuardianChipDefinition."""

    list_display = ("name", "slug", "wiki_entity_id")
    search_fields = ("name", "slug", "wiki_entity_id")


@admin.register(BotParameterDefinition)
class BotParameterDefinitionAdmin(admin.ModelAdmin):
    """Admin configuration for BotParameterDefinition."""

    list_display = ("bot_definition", "key", "display_name", "unit_kind")
    list_filter = ("key", "unit_kind")


@admin.register(BotParameterLevel)
class BotParameterLevelAdmin(admin.ModelAdmin):
    """Admin configuration for BotParameterLevel."""

    list_display = ("parameter_definition", "level", "value_raw", "cost_raw", "currency")
    list_filter = ("currency",)


@admin.register(UltimateWeaponParameterDefinition)
class UltimateWeaponParameterDefinitionAdmin(admin.ModelAdmin):
    """Admin configuration for UltimateWeaponParameterDefinition."""

    list_display = ("ultimate_weapon_definition", "key", "display_name", "unit_kind")
    list_filter = ("key", "unit_kind")


@admin.register(UltimateWeaponParameterLevel)
class UltimateWeaponParameterLevelAdmin(admin.ModelAdmin):
    """Admin configuration for UltimateWeaponParameterLevel."""

    list_display = ("parameter_definition", "level", "value_raw", "cost_raw", "currency")
    list_filter = ("currency",)


@admin.register(GuardianChipParameterDefinition)
class GuardianChipParameterDefinitionAdmin(admin.ModelAdmin):
    """Admin configuration for GuardianChipParameterDefinition."""

    list_display = ("guardian_chip_definition", "key", "display_name", "unit_kind")
    list_filter = ("key", "unit_kind")


@admin.register(GuardianChipParameterLevel)
class GuardianChipParameterLevelAdmin(admin.ModelAdmin):
    """Admin configuration for GuardianChipParameterLevel."""

    list_display = ("parameter_definition", "level", "value_raw", "cost_raw", "currency")
    list_filter = ("currency",)

