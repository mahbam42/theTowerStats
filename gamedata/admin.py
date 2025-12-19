"""Admin registrations for GameData models."""

from __future__ import annotations

from django.contrib import admin
from django.db.models import QuerySet

from gamedata.models import (
    BattleReport,
    BattleReportProgress,
    RunBot,
    RunCombatUltimateWeapon,
    RunGuardian,
    RunUtilityUltimateWeapon,
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


@admin.register(BattleReport)
class BattleReportAdmin(PlayerScopedAdmin):
    """Admin configuration for BattleReport."""

    list_display = ("player", "checksum", "parsed_at")
    search_fields = ("checksum",)


@admin.register(BattleReportProgress)
class BattleReportProgressAdmin(PlayerScopedAdmin):
    """Admin configuration for BattleReportProgress."""

    list_display = ("player", "battle_report", "battle_date", "tier", "wave", "real_time_seconds", "preset")
    list_filter = ("player", "tier", "preset")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):  # type: ignore[override]
        """Scope preset choices to the authenticated user's Player."""

        if (
            not request.user.is_superuser
            and db_field.name == "preset"
            and hasattr(request.user, "player")
        ):
            base_qs = kwargs.get("queryset") or db_field.remote_field.model._default_manager.all()
            kwargs["queryset"] = base_qs.filter(player=request.user.player)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(RunBot)
class RunBotAdmin(PlayerScopedAdmin):
    """Admin configuration for RunBot."""

    list_display = ("player", "battle_report", "bot_definition")


@admin.register(RunGuardian)
class RunGuardianAdmin(PlayerScopedAdmin):
    """Admin configuration for RunGuardian."""

    list_display = ("player", "battle_report", "guardian_chip_definition")


@admin.register(RunCombatUltimateWeapon)
class RunCombatUltimateWeaponAdmin(PlayerScopedAdmin):
    """Admin configuration for RunCombatUltimateWeapon."""

    list_display = ("player", "battle_report", "ultimate_weapon_definition")


@admin.register(RunUtilityUltimateWeapon)
class RunUtilityUltimateWeaponAdmin(PlayerScopedAdmin):
    """Admin configuration for RunUtilityUltimateWeapon."""

    list_display = ("player", "battle_report", "ultimate_weapon_definition")
