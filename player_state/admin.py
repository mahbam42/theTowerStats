"""Admin registrations for player state models."""

from __future__ import annotations

from django.contrib import admin
from django.db.models import QuerySet

from player_state.models import (
    ChartSnapshot,
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

class PlayerScopedAdmin(admin.ModelAdmin):
    """ModelAdmin that enforces per-player queryset filtering and ownership on create."""

    player_field_name = "player"

    def get_queryset(self, request) -> QuerySet:
        """Return a queryset scoped to the authenticated user's Player."""

        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(**{f"{self.player_field_name}__user": request.user})

    def get_readonly_fields(self, request, obj=None):  # type: ignore[override]
        """Prevent non-superusers from reassigning ownership fields."""

        readonly = list(super().get_readonly_fields(request, obj=obj))
        if not request.user.is_superuser and self.player_field_name not in readonly:
            readonly.append(self.player_field_name)
        return tuple(readonly)

    def save_model(self, request, obj, form, change) -> None:  # type: ignore[override]
        """Assign player ownership automatically for non-superusers."""

        if not request.user.is_superuser and not change:
            setattr(obj, self.player_field_name, request.user.player)
        super().save_model(request, obj, form, change)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """Admin configuration for Player."""

    list_display = ("display_name", "user", "created_at")
    search_fields = ("display_name", "user__username")

    def get_queryset(self, request) -> QuerySet:
        """Return a queryset scoped to the authenticated user's Player."""

        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def get_readonly_fields(self, request, obj=None):  # type: ignore[override]
        """Prevent non-superusers from editing identity fields."""

        readonly = list(super().get_readonly_fields(request, obj=obj))
        if not request.user.is_superuser:
            readonly.extend(["user"])
        return tuple(dict.fromkeys(readonly))

    def save_model(self, request, obj, form, change) -> None:  # type: ignore[override]
        """Assign user ownership automatically for non-superusers."""

        if not request.user.is_superuser and not change:
            obj.user = request.user
            if not obj.display_name:
                obj.display_name = request.user.username
        super().save_model(request, obj, form, change)


@admin.register(Preset)
class PresetAdmin(PlayerScopedAdmin):
    """Admin configuration for Preset."""

    list_display = ("player", "name", "color", "created_at")
    search_fields = ("name",)
    list_filter = ("player",)


@admin.register(ChartSnapshot)
class ChartSnapshotAdmin(PlayerScopedAdmin):
    """Admin configuration for ChartSnapshot."""

    list_display = ("player", "name", "target", "created_at")
    list_filter = ("player",)
    search_fields = ("name",)


@admin.register(PlayerCard)
class PlayerCardAdmin(PlayerScopedAdmin):
    """Admin configuration for PlayerCard."""

    list_display = ("player", "card_slug", "stars_unlocked", "updated_at")
    list_filter = ("player",)


@admin.register(PlayerBot)
class PlayerBotAdmin(PlayerScopedAdmin):
    """Admin configuration for PlayerBot."""

    list_display = ("player", "bot_slug", "unlocked", "updated_at")
    list_filter = ("player", "unlocked")


@admin.register(PlayerUltimateWeapon)
class PlayerUltimateWeaponAdmin(PlayerScopedAdmin):
    """Admin configuration for PlayerUltimateWeapon."""

    list_display = ("player", "ultimate_weapon_slug", "unlocked", "updated_at")
    list_filter = ("player", "unlocked")


@admin.register(PlayerGuardianChip)
class PlayerGuardianChipAdmin(PlayerScopedAdmin):
    """Admin configuration for PlayerGuardianChip."""

    list_display = ("player", "guardian_chip_slug", "unlocked", "updated_at")
    list_filter = ("player", "unlocked")


@admin.register(PlayerBotParameter)
class PlayerBotParameterAdmin(PlayerScopedAdmin):
    """Admin configuration for PlayerBotParameter."""

    list_display = ("player_bot", "parameter_definition", "level", "updated_at")


@admin.register(PlayerUltimateWeaponParameter)
class PlayerUltimateWeaponParameterAdmin(PlayerScopedAdmin):
    """Admin configuration for PlayerUltimateWeaponParameter."""

    list_display = ("player_ultimate_weapon", "parameter_definition", "level", "updated_at")


@admin.register(PlayerGuardianChipParameter)
class PlayerGuardianChipParameterAdmin(PlayerScopedAdmin):
    """Admin configuration for PlayerGuardianChipParameter."""

    list_display = ("player_guardian_chip", "parameter_definition", "level", "updated_at")
