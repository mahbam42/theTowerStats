"""Database models for runtime battle reports and run* metrics."""

from __future__ import annotations

from django.db import models
from django.core.exceptions import ValidationError

from definitions.models import BotDefinition, GuardianChipDefinition, UltimateWeaponDefinition
from player_state.models import Player, Preset


class BattleReport(models.Model):
    """Raw, preserved battle report payload imported from the player."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="battle_reports")
    raw_text = models.TextField()
    parsed_at = models.DateTimeField(auto_now_add=True)
    checksum = models.CharField(max_length=64, db_index=True)

    class Meta:
        verbose_name = "Battle Report"
        verbose_name_plural = "Battle Reports"
        constraints = [
            models.UniqueConstraint(fields=["player", "checksum"], name="uniq_player_battle_report_checksum"),
        ]

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        return (
            "BattleReport("
            f"player={self.player_id}, checksum={self.checksum[:10]}…, parsed_at={self.parsed_at.isoformat()}"
            ")"
        )


class BattleReportDerivedMetrics(models.Model):
    """Persisted derived metrics parsed from Battle Report raw text."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="battle_report_derived_metrics")
    battle_report = models.OneToOneField(
        BattleReport, on_delete=models.CASCADE, related_name="derived_metrics"
    )
    values = models.JSONField(default=dict, blank=True)
    raw_values = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Battle Report Derived Metrics"
        verbose_name_plural = "Battle Report Derived Metrics"

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        return f"BattleReportDerivedMetrics(battle_report_id={self.battle_report_id})"

    def clean(self) -> None:
        """Enforce that derived metrics remain scoped to a single player."""

        if self.battle_report_id and self.battle_report.player_id != self.player_id:
            raise ValidationError("BattleReportDerivedMetrics.player must match battle_report.player.")

    def save(self, *args, **kwargs) -> None:
        """Persist derived metrics after validating ownership."""

        self.full_clean()
        super().save(*args, **kwargs)


class BattleReportProgress(models.Model):
    """Minimal run metadata extracted from a Battle Report.

    This replaces the prior Phase 1 `RunProgress` but keeps the relationship
    name `run_progress` for compatibility with analysis/visualization code.
    """

    battle_report = models.OneToOneField(
        BattleReport, on_delete=models.CASCADE, related_name="run_progress"
    )
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="battle_report_progress")
    battle_date = models.DateTimeField(null=True, blank=True)
    tier = models.PositiveSmallIntegerField(null=True, blank=True)
    preset = models.ForeignKey(
        Preset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="battle_reports",
    )
    preset_name_snapshot = models.CharField(
        max_length=80,
        blank=True,
        default="",
        help_text="Preset label captured at assignment time for historical display.",
    )
    preset_color_snapshot = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Preset color key captured at assignment time for historical badge rendering.",
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
    is_tournament = models.BooleanField(
        default=False,
        help_text="Manual override: mark this run as a tournament when the report text does not indicate it.",
    )

    class Meta:
        verbose_name = "Battle Report Progress"
        verbose_name_plural = "Battle Report Progress"

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        return f"BattleReportProgress(tier={self.tier}, wave={self.wave}, battle_date={self.battle_date})"

    def clean(self) -> None:
        """Validate that progress metadata stays within a single owning player."""

        if self.battle_report_id and self.battle_report.player_id != self.player_id:
            raise ValidationError("BattleReportProgress.player must match battle_report.player.")
        if self.preset_id and self.preset.player_id != self.player_id:
            raise ValidationError("BattleReportProgress.player must match preset.player.")

    def save(self, *args, **kwargs) -> None:
        """Save while enforcing ownership invariants."""

        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def coins(self) -> int | None:
        """Return coins earned for analysis-engine compatibility."""

        return self.coins_earned


class RunBot(models.Model):
    """Observed bot usage/performance row for a battle report."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="run_bots")
    battle_report = models.ForeignKey(BattleReport, on_delete=models.CASCADE, related_name="run_bots")
    bot_definition = models.ForeignKey(BotDefinition, on_delete=models.CASCADE, related_name="run_bots")
    notes = models.TextField(blank=True)

    def clean(self) -> None:
        """Validate that the run row stays within a single owning player."""

        if self.battle_report_id and self.battle_report.player_id != self.player_id:
            raise ValidationError("RunBot.player must match battle_report.player.")

    def save(self, *args, **kwargs) -> None:
        """Save while enforcing ownership invariants."""

        self.full_clean()
        super().save(*args, **kwargs)


class RunGuardian(models.Model):
    """Observed guardian chip usage/performance row for a battle report."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="run_guardians")
    battle_report = models.ForeignKey(
        BattleReport, on_delete=models.CASCADE, related_name="run_guardians"
    )
    guardian_chip_definition = models.ForeignKey(
        GuardianChipDefinition, on_delete=models.CASCADE, related_name="run_guardians"
    )
    notes = models.TextField(blank=True)

    def clean(self) -> None:
        """Validate that the run row stays within a single owning player."""

        if self.battle_report_id and self.battle_report.player_id != self.player_id:
            raise ValidationError("RunGuardian.player must match battle_report.player.")

    def save(self, *args, **kwargs) -> None:
        """Save while enforcing ownership invariants."""

        self.full_clean()
        super().save(*args, **kwargs)


class RunCombatUltimateWeapon(models.Model):
    """Observed combat-utility ultimate weapon usage row for a battle report."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="run_combat_uws")
    battle_report = models.ForeignKey(
        BattleReport, on_delete=models.CASCADE, related_name="run_combat_uws"
    )
    ultimate_weapon_definition = models.ForeignKey(
        UltimateWeaponDefinition, on_delete=models.CASCADE, related_name="run_combat_uws"
    )
    notes = models.TextField(blank=True)

    def clean(self) -> None:
        """Validate that the run row stays within a single owning player."""

        if self.battle_report_id and self.battle_report.player_id != self.player_id:
            raise ValidationError("RunCombatUltimateWeapon.player must match battle_report.player.")

    def save(self, *args, **kwargs) -> None:
        """Save while enforcing ownership invariants."""

        self.full_clean()
        super().save(*args, **kwargs)


class RunUtilityUltimateWeapon(models.Model):
    """Observed non-combat ultimate weapon usage row for a battle report."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="run_utility_uws")
    battle_report = models.ForeignKey(
        BattleReport, on_delete=models.CASCADE, related_name="run_utility_uws"
    )
    ultimate_weapon_definition = models.ForeignKey(
        UltimateWeaponDefinition, on_delete=models.CASCADE, related_name="run_utility_uws"
    )
    notes = models.TextField(blank=True)

    def clean(self) -> None:
        """Validate that the run row stays within a single owning player."""

        if self.battle_report_id and self.battle_report.player_id != self.player_id:
            raise ValidationError("RunUtilityUltimateWeapon.player must match battle_report.player.")

    def save(self, *args, **kwargs) -> None:
        """Save while enforcing ownership invariants."""

        self.full_clean()
        super().save(*args, **kwargs)
