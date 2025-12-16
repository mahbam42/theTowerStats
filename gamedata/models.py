"""Database models for runtime battle reports and run* metrics."""

from __future__ import annotations

from django.db import models

from definitions.models import BotDefinition, GuardianChipDefinition, UltimateWeaponDefinition
from player_state.models import Preset


class BattleReport(models.Model):
    """Raw, preserved battle report payload imported from the player."""

    raw_text = models.TextField()
    parsed_at = models.DateTimeField(auto_now_add=True)
    checksum = models.CharField(max_length=64, unique=True)

    class Meta:
        verbose_name = "Battle Report"
        verbose_name_plural = "Battle Reports"

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        return f"BattleReport({self.checksum[:10]}…, parsed_at={self.parsed_at.isoformat()})"


class BattleReportProgress(models.Model):
    """Minimal run metadata extracted from a Battle Report.

    This replaces the prior Phase 1 `RunProgress` but keeps the relationship
    name `run_progress` for compatibility with analysis/visualization code.
    """

    battle_report = models.OneToOneField(
        BattleReport, on_delete=models.CASCADE, related_name="run_progress"
    )
    battle_date = models.DateTimeField(null=True, blank=True)
    tier = models.PositiveSmallIntegerField(null=True, blank=True)
    preset = models.ForeignKey(
        Preset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="battle_reports",
    )
    wave = models.PositiveIntegerField(null=True, blank=True)
    real_time_seconds = models.PositiveIntegerField(null=True, blank=True)
    killed_by = models.CharField(max_length=255, null=True, blank=True)
    coins_earned = models.BigIntegerField(null=True, blank=True)
    coins_earned_raw = models.CharField(max_length=64, null=True, blank=True)
    cash_earned = models.BigIntegerField(null=True, blank=True)
    cash_earned_raw = models.CharField(max_length=64, null=True, blank=True)
    interest_earned = models.BigIntegerField(null=True, blank=True)
    interest_earned_raw = models.CharField(max_length=64, null=True, blank=True)
    gem_blocks_tapped = models.PositiveIntegerField(null=True, blank=True)
    cells_earned = models.PositiveIntegerField(null=True, blank=True)
    reroll_shards_earned = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Battle Report Progress"
        verbose_name_plural = "Battle Report Progress"

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        return f"BattleReportProgress(tier={self.tier}, wave={self.wave}, battle_date={self.battle_date})"

    @property
    def coins(self) -> int | None:
        """Return coins earned for analysis-engine compatibility."""

        return self.coins_earned


class RunBot(models.Model):
    """Observed bot usage/performance row for a battle report."""

    battle_report = models.ForeignKey(BattleReport, on_delete=models.CASCADE, related_name="run_bots")
    bot_definition = models.ForeignKey(BotDefinition, on_delete=models.CASCADE, related_name="run_bots")
    notes = models.TextField(blank=True)


class RunGuardian(models.Model):
    """Observed guardian chip usage/performance row for a battle report."""

    battle_report = models.ForeignKey(
        BattleReport, on_delete=models.CASCADE, related_name="run_guardians"
    )
    guardian_chip_definition = models.ForeignKey(
        GuardianChipDefinition, on_delete=models.CASCADE, related_name="run_guardians"
    )
    notes = models.TextField(blank=True)


class RunCombatUltimateWeapon(models.Model):
    """Observed combat-utility ultimate weapon usage row for a battle report."""

    battle_report = models.ForeignKey(
        BattleReport, on_delete=models.CASCADE, related_name="run_combat_uws"
    )
    ultimate_weapon_definition = models.ForeignKey(
        UltimateWeaponDefinition, on_delete=models.CASCADE, related_name="run_combat_uws"
    )
    notes = models.TextField(blank=True)


class RunUtilityUltimateWeapon(models.Model):
    """Observed non-combat ultimate weapon usage row for a battle report."""

    battle_report = models.ForeignKey(
        BattleReport, on_delete=models.CASCADE, related_name="run_utility_uws"
    )
    ultimate_weapon_definition = models.ForeignKey(
        UltimateWeaponDefinition, on_delete=models.CASCADE, related_name="run_utility_uws"
    )
    notes = models.TextField(blank=True)
