"""Database models for player progress and configuration."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from definitions.models import (
    BotDefinition,
    BotParameterDefinition,
    CardDefinition,
    GuardianChipDefinition,
    GuardianChipParameterDefinition,
    UltimateWeaponDefinition,
    UltimateWeaponParameterDefinition,
)

PRESET_COLOR_KEYS: tuple[str, ...] = (
    "blue",
    "teal",
    "green",
    "orange",
    "red",
    "purple",
)
PRESET_COLOR_CHOICES: tuple[tuple[str, str], ...] = tuple(
    (key, key.title()) for key in PRESET_COLOR_KEYS
)

MAX_ACTIVE_GUARDIAN_CHIPS = 2


def preset_color_for_id(*, preset_id: int) -> str:
    """Select a stable preset color key for a database id.

    Args:
        preset_id: Database primary key for a Preset.

    Returns:
        A stable color key chosen from the supported palette.
    """

    return PRESET_COLOR_KEYS[preset_id % len(PRESET_COLOR_KEYS)]


class Player(models.Model):
    """A single-player (by default) root entity for progress ownership."""

    name = models.CharField(max_length=80, unique=True, default="default")
    card_slots_unlocked = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Return the player name for display contexts."""

        return self.name


class Preset(models.Model):
    """A configuration snapshot label (no metrics)."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="presets")
    name = models.CharField(max_length=80)
    color = models.CharField(max_length=20, blank=True, choices=PRESET_COLOR_CHOICES, default="")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["player", "name"], name="uniq_player_preset_name")
        ]

    def __str__(self) -> str:
        """Return preset display name."""

        return self.name

    def save(self, *args, **kwargs) -> None:
        """Save while ensuring the preset has a stable badge color."""

        super().save(*args, **kwargs)
        if self.color or self.pk is None:
            return
        self.color = preset_color_for_id(preset_id=self.pk)
        super().save(update_fields=["color"])

    def badge_color(self) -> str:
        """Return the effective color key for UI badges.

        Returns:
            A palette key for use in CSS class names.
        """

        if self.color:
            return self.color
        if self.pk is None:
            return PRESET_COLOR_KEYS[0]
        return preset_color_for_id(preset_id=self.pk)


class ChartSnapshot(models.Model):
    """An immutable snapshot used as a reusable comparison anchor.

    A snapshot stores:
    - a constrained Chart Builder configuration (schema-driven),
    - the context filters used when it was created.

    Snapshots are labels over existing metrics and are not a source of new math.
    """

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="chart_snapshots")
    name = models.CharField(max_length=120)
    target = models.CharField(
        max_length=40,
        default="charts",
        help_text="Dashboard target for applying this snapshot (e.g. charts, ultimate_weapons).",
    )
    config = models.JSONField(
        default=dict,
        help_text="Versioned ChartConfigDTO payload used for deterministic chart execution.",
    )
    chart_builder = models.JSONField(default=dict)
    chart_context = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["player", "name"], name="uniq_player_chart_snapshot_name")
        ]

    def __str__(self) -> str:
        """Return a concise display string."""

        return f"ChartSnapshot({self.name})"

    def save(self, *args, **kwargs) -> None:
        """Save a snapshot, enforcing immutability after creation.

        Raises:
            ValidationError: When attempting to update an existing snapshot.
        """

        if self.pk is not None and not kwargs.get("force_insert", False):
            raise ValidationError("Chart snapshots are immutable once created.")
        super().save(*args, **kwargs)


class PlayerCard(models.Model):
    """Player card unlock state.

    Cards are descriptive modifiers and do not use ParameterKey or upgrade tables.
    """

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="cards")
    card_definition = models.ForeignKey(
        CardDefinition,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="player_cards",
    )
    card_slug = models.CharField(max_length=200, db_index=True)
    inventory_count = models.PositiveIntegerField(default=0)
    stars_unlocked = models.PositiveSmallIntegerField(default=0)
    presets = models.ManyToManyField("Preset", through="PlayerCardPreset", blank=True, related_name="player_cards")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["player", "card_slug"], name="uniq_player_card_slug")
        ]

    def clean(self) -> None:
        """Validate invariants for card state."""

        if self.card_definition is not None and self.card_definition.slug != self.card_slug:
            raise ValidationError("card_slug must match card_definition.slug when definition is set.")

    def save(self, *args, **kwargs) -> None:
        """Save while enforcing invariants."""

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return a concise display string."""

        return (
            "PlayerCard("
            f"{self.card_slug}, inventory={self.inventory_count}, stars={self.stars_unlocked}"
            ")"
        )


class PlayerCardPreset(models.Model):
    """Many-to-many join table connecting player cards to preset labels."""

    player_card = models.ForeignKey(PlayerCard, on_delete=models.CASCADE, related_name="preset_links")
    preset = models.ForeignKey(Preset, on_delete=models.CASCADE, related_name="card_links")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["player_card", "preset"], name="uniq_player_card_preset")
        ]

    def __str__(self) -> str:
        """Return a concise display string."""

        return f"PlayerCardPreset(card={self.player_card_id}, preset={self.preset_id})"


class PlayerBot(models.Model):
    """Player bot unlock state (per-parameter progression lives separately)."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="bots")
    bot_definition = models.ForeignKey(
        BotDefinition,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="player_bots",
    )
    bot_slug = models.CharField(max_length=200, db_index=True)
    unlocked = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["player", "bot_slug"], name="uniq_player_bot_slug")
        ]

    def clean(self) -> None:
        """Validate invariants for bot state."""

        if self.bot_definition is not None and self.bot_definition.slug != self.bot_slug:
            raise ValidationError("bot_slug must match bot_definition.slug when definition is set.")

    def save(self, *args, **kwargs) -> None:
        """Save while enforcing invariants."""

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return a concise display string."""

        return f"PlayerBot({self.bot_slug}, unlocked={self.unlocked})"


class PlayerUltimateWeapon(models.Model):
    """Player ultimate weapon unlock state (per-parameter progression lives separately)."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="ultimate_weapons")
    ultimate_weapon_definition = models.ForeignKey(
        UltimateWeaponDefinition,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="player_ultimate_weapons",
    )
    ultimate_weapon_slug = models.CharField(max_length=200, db_index=True)
    unlocked = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player", "ultimate_weapon_slug"],
                name="uniq_player_uw_slug",
            )
        ]

    def clean(self) -> None:
        """Validate invariants for ultimate weapon state."""

        if (
            self.ultimate_weapon_definition is not None
            and self.ultimate_weapon_definition.slug != self.ultimate_weapon_slug
        ):
            raise ValidationError(
                "ultimate_weapon_slug must match ultimate_weapon_definition.slug when definition is set."
            )

    def save(self, *args, **kwargs) -> None:
        """Save while enforcing invariants."""

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return a concise display string."""

        return f"PlayerUltimateWeapon({self.ultimate_weapon_slug}, unlocked={self.unlocked})"


class PlayerGuardianChip(models.Model):
    """Player guardian chip unlock state (per-parameter progression lives separately)."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="guardian_chips")
    guardian_chip_definition = models.ForeignKey(
        GuardianChipDefinition,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="player_guardian_chips",
    )
    guardian_chip_slug = models.CharField(max_length=200, db_index=True)
    unlocked = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player", "guardian_chip_slug"],
                name="uniq_player_guardian_slug",
            )
        ]

    def clean(self) -> None:
        """Validate invariants for guardian chip state."""

        if (
            self.guardian_chip_definition is not None
            and self.guardian_chip_definition.slug != self.guardian_chip_slug
        ):
            raise ValidationError(
                "guardian_chip_slug must match guardian_chip_definition.slug when definition is set."
            )
        if self.active and not self.unlocked:
            raise ValidationError("Cannot activate a locked guardian chip.")
        if self.active and self.player_id:
            other_active = (
                PlayerGuardianChip.objects.filter(player_id=self.player_id, active=True)
                .exclude(pk=self.pk)
                .count()
            )
            if other_active >= MAX_ACTIVE_GUARDIAN_CHIPS:
                raise ValidationError(f"At most {MAX_ACTIVE_GUARDIAN_CHIPS} guardian chips may be active at once.")

    def save(self, *args, **kwargs) -> None:
        """Save while enforcing invariants."""

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return a concise display string."""

        return f"PlayerGuardianChip({self.guardian_chip_slug}, unlocked={self.unlocked})"


class PlayerBotParameter(models.Model):
    """Player-selected level for a bot parameter definition."""

    player_bot = models.ForeignKey(PlayerBot, on_delete=models.CASCADE, related_name="parameters")
    parameter_definition = models.ForeignKey(
        BotParameterDefinition,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="player_levels",
    )
    level = models.PositiveSmallIntegerField(default=0)
    effective_value_raw = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="Optional authoritative effective value (do not compute; explanatory only).",
    )
    effective_notes = models.TextField(
        blank=True,
        default="",
        help_text="Optional explanation lines for effective value (no calculations).",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player_bot", "parameter_definition"],
                name="uniq_player_bot_param",
            )
        ]

    def clean(self) -> None:
        """Validate locked-state and definition alignment."""

        if self.level and not self.player_bot.unlocked:
            raise ValidationError("Cannot set bot parameter level when the bot is locked.")
        if (
            self.parameter_definition is not None
            and self.player_bot.bot_definition is not None
            and self.parameter_definition.bot_definition_id != self.player_bot.bot_definition_id
        ):
            raise ValidationError("Bot parameter definition must belong to the same bot definition.")

    def save(self, *args, **kwargs) -> None:
        """Save while enforcing invariants."""

        self.full_clean()
        super().save(*args, **kwargs)


class PlayerUltimateWeaponParameter(models.Model):
    """Player-selected level for an ultimate weapon parameter definition."""

    player_ultimate_weapon = models.ForeignKey(
        PlayerUltimateWeapon, on_delete=models.CASCADE, related_name="parameters"
    )
    parameter_definition = models.ForeignKey(
        UltimateWeaponParameterDefinition,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="player_levels",
    )
    level = models.PositiveSmallIntegerField(default=0)
    effective_value_raw = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="Optional authoritative effective value (do not compute; explanatory only).",
    )
    effective_notes = models.TextField(
        blank=True,
        default="",
        help_text="Optional explanation lines for effective value (no calculations).",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player_ultimate_weapon", "parameter_definition"],
                name="uniq_player_uw_param",
            )
        ]

    def clean(self) -> None:
        """Validate locked-state and definition alignment."""

        if self.level and not self.player_ultimate_weapon.unlocked:
            raise ValidationError("Cannot set ultimate weapon parameter level when the weapon is locked.")
        if (
            self.parameter_definition is not None
            and self.player_ultimate_weapon.ultimate_weapon_definition is not None
            and self.parameter_definition.ultimate_weapon_definition_id
            != self.player_ultimate_weapon.ultimate_weapon_definition_id
        ):
            raise ValidationError(
                "Ultimate weapon parameter definition must belong to the same ultimate weapon definition."
            )

    def save(self, *args, **kwargs) -> None:
        """Save while enforcing invariants."""

        self.full_clean()
        super().save(*args, **kwargs)


class PlayerGuardianChipParameter(models.Model):
    """Player-selected level for a guardian chip parameter definition."""

    player_guardian_chip = models.ForeignKey(
        PlayerGuardianChip, on_delete=models.CASCADE, related_name="parameters"
    )
    parameter_definition = models.ForeignKey(
        GuardianChipParameterDefinition,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="player_levels",
    )
    level = models.PositiveSmallIntegerField(default=0)
    effective_value_raw = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="Optional authoritative effective value (do not compute; explanatory only).",
    )
    effective_notes = models.TextField(
        blank=True,
        default="",
        help_text="Optional explanation lines for effective value (no calculations).",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player_guardian_chip", "parameter_definition"],
                name="uniq_player_guardian_param",
            )
        ]

    def clean(self) -> None:
        """Validate locked-state and definition alignment."""

        if self.level and not self.player_guardian_chip.unlocked:
            raise ValidationError("Cannot set guardian chip parameter level when the chip is locked.")
        if (
            self.parameter_definition is not None
            and self.player_guardian_chip.guardian_chip_definition is not None
            and self.parameter_definition.guardian_chip_definition_id
            != self.player_guardian_chip.guardian_chip_definition_id
        ):
            raise ValidationError(
                "Guardian chip parameter definition must belong to the same guardian chip definition."
            )

    def save(self, *args, **kwargs) -> None:
        """Save while enforcing invariants."""

        self.full_clean()
        super().save(*args, **kwargs)
