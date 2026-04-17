"""Database models for runtime battle reports and run* metrics."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.core.exceptions import ValidationError

from definitions.models import BotDefinition, GuardianChipDefinition, UltimateWeaponDefinition
from player_state.models import Player, Preset

TOURNAMENT_RANK_KEYS: tuple[str, ...] = (
    "copper",
    "silver",
    "gold",
    "platinum",
    "champions",
    "legends",
)
TOURNAMENT_RANK_CHOICES: tuple[tuple[str, str], ...] = tuple(
    (key, key.title()) for key in TOURNAMENT_RANK_KEYS
)

DISSONANCE_TYPE_KEYS: tuple[str, ...] = (
    "attack",
    "defense",
    "utility",
    "ultimate_weapon",
)
DISSONANCE_TYPE_CHOICES: tuple[tuple[str, str], ...] = (
    ("attack", "Attack"),
    ("defense", "Defense"),
    ("utility", "Utility"),
    ("ultimate_weapon", "Ultimate Weapon"),
)


class BattleReport(models.Model):
    """Raw, preserved battle report payload imported from the player."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="battle_reports")
    raw_text = models.TextField()
    parsed_at = models.DateTimeField(auto_now_add=True)
    checksum = models.CharField(max_length=64, db_index=True)
    is_hidden = models.BooleanField(
        default=False,
        help_text="Exclude this report from Charts and Explore unless explicitly included.",
    )

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
    game_time_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Parsed Game Time duration in seconds from the Battle Report.",
    )
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
    tournament_rank = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=TOURNAMENT_RANK_CHOICES,
        help_text="Optional tournament rank recorded during import.",
    )
    is_dissonance = models.BooleanField(
        default=False,
        help_text="Manual override: mark this run as a Dissonance run when the pasted text does not indicate it.",
    )
    dissonance_type = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=DISSONANCE_TYPE_CHOICES,
        help_text="Optional Dissonance type recorded during import.",
    )
    dissonance_levels_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Stored Dissonance level snapshot per type for this run's tier at import time.",
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
        if self.is_tournament and self.is_dissonance:
            raise ValidationError("BattleReportProgress cannot be both tournament and Dissonance.")
        if not self.is_tournament:
            self.tournament_rank = None
        if self.is_dissonance and not self.dissonance_type:
            raise ValidationError("Dissonance type is required when is_dissonance is enabled.")
        if not self.is_dissonance:
            self.dissonance_type = None
        if not isinstance(self.dissonance_levels_snapshot, dict):
            raise ValidationError("Dissonance level snapshot must be a mapping.")

    def save(self, *args, **kwargs) -> None:
        """Save while enforcing ownership invariants."""

        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def coins(self) -> int | None:
        """Return coins earned for analysis-engine compatibility."""

        return self.coins_earned


class PlayerDissonanceTierBoost(models.Model):
    """Persist Dissonance progression for a player, tier, and boost type.

    Attributes:
        player: Owning player.
        tier: Tier the Dissonance progression applies to.
        dissonance_type: One of the supported Dissonance categories.
        current_level: Current unlocked level for this player/tier/type.
        highest_effective_multiplier: Highest recorded effective multiplier.
        top_effective_multipliers: Descending top-three effective multiplier history.
    """

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="dissonance_tier_boosts",
    )
    tier = models.PositiveSmallIntegerField()
    dissonance_type = models.CharField(max_length=20, choices=DISSONANCE_TYPE_CHOICES)
    current_level = models.PositiveIntegerField(default=1)
    highest_effective_multiplier = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal("1.0000"),
    )
    top_effective_multipliers = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = "Player Dissonance Tier Boost"
        verbose_name_plural = "Player Dissonance Tier Boosts"
        constraints = [
            models.UniqueConstraint(
                fields=["player", "tier", "dissonance_type"],
                name="uniq_player_dissonance_tier_type",
            ),
        ]

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        return (
            "PlayerDissonanceTierBoost("
            f"player={self.player_id}, tier={self.tier}, type={self.dissonance_type}, level={self.current_level}"
            ")"
        )

    def clean(self) -> None:
        """Validate Dissonance progression invariants."""

        if self.current_level < 1:
            raise ValidationError("current_level must be at least 1.")
        if not isinstance(self.top_effective_multipliers, list):
            raise ValidationError("top_effective_multipliers must be a list.")

    def save(self, *args, **kwargs) -> None:
        """Persist Dissonance progression after validating invariants."""

        self.full_clean()
        super().save(*args, **kwargs)


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
