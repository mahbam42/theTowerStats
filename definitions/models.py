"""Database models for the Definitions layer.

Definitions are wiki-derived and rebuildable. They must not reference Player
State or GameData models.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone
from enum import StrEnum


class WikiData(models.Model):
    """Versioned, non-destructive store for wiki-derived table data.

    Wiki-derived data is ingested as raw strings to provide stable inputs for
    later analysis phases. Content fields (name, raw_row, hashes, metadata) are
    treated as immutable once written. Lifecycle fields (`last_seen`,
    `deprecated`) may be updated to support change detection and safe diffing.
    """

    page_url = models.URLField()
    canonical_name = models.CharField(max_length=200)
    entity_id = models.CharField(max_length=200, db_index=True)
    content_hash = models.CharField(max_length=64, db_index=True)
    raw_row = models.JSONField()
    source_section = models.CharField(max_length=200)
    first_seen = models.DateTimeField(default=timezone.now, editable=False)
    last_seen = models.DateTimeField(default=timezone.now)
    parse_version = models.CharField(max_length=40)
    deprecated = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "page_url",
                    "source_section",
                    "parse_version",
                    "entity_id",
                    "content_hash",
                ],
                name="uniq_wikidata_revision",
            )
        ]
        indexes = [
            models.Index(fields=["page_url", "source_section", "parse_version", "entity_id"]),
        ]
        verbose_name = "Wiki Data"
        verbose_name_plural = "Wiki Data"

    def save(self, *args, **kwargs) -> None:
        """Save the record, enforcing immutability for content fields."""

        if self.pk is not None:
            original = WikiData.objects.get(pk=self.pk)
            immutable_fields = (
                "page_url",
                "canonical_name",
                "entity_id",
                "content_hash",
                "raw_row",
                "source_section",
                "first_seen",
                "parse_version",
            )
            for field_name in immutable_fields:
                if getattr(original, field_name) != getattr(self, field_name):
                    raise ValueError(
                        f"WikiData is immutable; attempted to change {field_name!r} for pk={self.pk}."
                    )
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        return f"WikiData(entity_id={self.entity_id}, hash={self.content_hash[:10]}…, deprecated={self.deprecated})"


class Unit(models.Model):
    """A lightweight unit/metadata model for labeling raw parameter values."""

    class Kind(models.TextChoices):
        """Broad unit categories for UI display."""

        UNKNOWN = "unknown", "Unknown"
        COUNT = "count", "Count"
        PERCENT = "percent", "Percent"
        SECONDS = "seconds", "Seconds"
        MULTIPLIER = "multiplier", "Multiplier"
        CURRENCY = "currency", "Currency"

    name = models.CharField(max_length=80, unique=True)
    symbol = models.CharField(max_length=12, blank=True)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.UNKNOWN)

    def __str__(self) -> str:
        """Return the unit name for display contexts."""

        return self.name


class ParameterKey(StrEnum):
    """Global registry of parameter labels.

    This registry contains labels only (no gameplay/scaling logic). The same key
    may represent different semantics per entity; the entity-scoped meaning is
    provided by `display_name` on the parameter definition.
    """

    ANGLE = "angle"
    CASH_BONUS = "cash_bonus"
    CHANCE = "chance"
    COINS_BONUS = "coins_bonus"
    COINS_MULTIPLIER = "coins_multiplier"
    COOLDOWN = "cooldown"
    DAMAGE = "damage"
    DAMAGE_MULTIPLIER = "damage_multiplier"
    DAMAGE_PERCENT = "damage_percent"
    DAMAGE_REDUCTION = "damage_reduction"
    DOUBLE_FIND_CHANCE = "double_find_chance"
    DURATION = "duration"
    EFFECT_WAVE = "effect_wave"
    FIND_CHANCE = "find_chance"
    LINGER = "linger"
    MAX_RECOVERY = "max_recovery"
    MULTIPLIER = "multiplier"
    PERCENTAGE = "percentage"
    QUANTITY = "quantity"
    RANGE = "range"
    RECOVERY_AMOUNT = "recovery_amount"
    SIZE = "size"
    SLOW = "slow"
    TARGETS = "targets"


PARAMETER_KEY_CHOICES: tuple[tuple[str, str], ...] = tuple(
    (key.value, key.value.replace("_", " ").title()) for key in ParameterKey
)


class Currency(models.TextChoices):
    """Currency for wiki upgrade tables."""

    MEDALS = "medals", "Medals"
    STONES = "stones", "Stones"
    BITS = "bits", "Bits"


class CardDefinition(models.Model):
    """Definition record for a card as shown in the in-app library."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.CharField(max_length=200, unique=True)
    wiki_page_url = models.URLField(blank=True)
    wiki_entity_id = models.CharField(max_length=200, blank=True, db_index=True)
    description = models.TextField(blank=True)
    rarity = models.CharField(max_length=80, blank=True)
    unlock_text = models.TextField(blank=True)
    source_wikidata = models.ForeignKey(
        WikiData, null=True, blank=True, on_delete=models.SET_NULL, related_name="card_definitions"
    )

    def __str__(self) -> str:
        """Return the card name for display contexts."""

        return self.name


class BotDefinition(models.Model):
    """Definition record for a bot as shown in the in-app library."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.CharField(max_length=200, unique=True)
    wiki_page_url = models.URLField(blank=True)
    wiki_entity_id = models.CharField(max_length=200, blank=True, db_index=True)
    description = models.TextField(blank=True)
    source_wikidata = models.ForeignKey(
        WikiData, null=True, blank=True, on_delete=models.SET_NULL, related_name="bot_definitions"
    )

    def __str__(self) -> str:
        """Return the bot name for display contexts."""

        return self.name


class UltimateWeaponDefinition(models.Model):
    """Definition record for ultimate weapons."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.CharField(max_length=200, unique=True)
    wiki_page_url = models.URLField(blank=True)
    wiki_entity_id = models.CharField(max_length=200, blank=True, db_index=True)
    description = models.TextField(blank=True)
    source_wikidata = models.ForeignKey(
        WikiData,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ultimate_weapon_definitions",
    )

    def __str__(self) -> str:
        """Return the weapon name for display contexts."""

        return self.name


class GuardianChipDefinition(models.Model):
    """Definition record for guardian chips."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.CharField(max_length=200, unique=True)
    wiki_page_url = models.URLField(blank=True)
    wiki_entity_id = models.CharField(max_length=200, blank=True, db_index=True)
    description = models.TextField(blank=True)
    source_wikidata = models.ForeignKey(
        WikiData,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="guardian_chip_definitions",
    )

    def __str__(self) -> str:
        """Return the chip name for display contexts."""

        return self.name


class BotParameterDefinition(models.Model):
    """Parameter definition for a bot upgrade parameter."""

    bot_definition = models.ForeignKey(
        BotDefinition, on_delete=models.CASCADE, related_name="parameter_definitions"
    )
    key = models.CharField(max_length=40, choices=PARAMETER_KEY_CHOICES)
    display_name = models.CharField(max_length=120)
    unit_kind = models.CharField(
        max_length=20, choices=Unit.Kind.choices, default=Unit.Kind.UNKNOWN
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["bot_definition", "key"],
                name="uniq_bot_param_definition_key",
            )
        ]

    def __str__(self) -> str:
        """Return a concise string for admin/debug usage."""

        return f"{self.bot_definition.slug}:{self.key}"


class BotParameterLevel(models.Model):
    """Wiki-derived level row for a bot parameter."""

    parameter_definition = models.ForeignKey(
        BotParameterDefinition, on_delete=models.CASCADE, related_name="levels"
    )
    level = models.PositiveSmallIntegerField()
    value_raw = models.CharField(max_length=200)
    cost_raw = models.CharField(max_length=200)
    currency = models.CharField(max_length=20, choices=Currency.choices, default=Currency.MEDALS)
    source_wikidata = models.ForeignKey(
        WikiData, null=True, blank=True, on_delete=models.SET_NULL, related_name="bot_parameter_levels"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["parameter_definition", "level"],
                name="uniq_bot_param_level",
            ),
            models.CheckConstraint(
                condition=models.Q(currency=Currency.MEDALS),
                name="bot_param_currency_medals",
            ),
        ]

    def __str__(self) -> str:
        """Return a concise string for admin/debug usage."""

        return f"{self.parameter_definition} L{self.level}"


class UltimateWeaponParameterDefinition(models.Model):
    """Parameter definition for an ultimate weapon upgrade parameter."""

    ultimate_weapon_definition = models.ForeignKey(
        UltimateWeaponDefinition,
        on_delete=models.CASCADE,
        related_name="parameter_definitions",
    )
    key = models.CharField(max_length=40, choices=PARAMETER_KEY_CHOICES)
    display_name = models.CharField(max_length=120)
    unit_kind = models.CharField(
        max_length=20, choices=Unit.Kind.choices, default=Unit.Kind.UNKNOWN
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ultimate_weapon_definition", "key"],
                name="uniq_uw_param_definition_key",
            )
        ]

    def __str__(self) -> str:
        """Return a concise string for admin/debug usage."""

        return f"{self.ultimate_weapon_definition.slug}:{self.key}"


class UltimateWeaponParameterLevel(models.Model):
    """Wiki-derived level row for an ultimate weapon parameter."""

    parameter_definition = models.ForeignKey(
        UltimateWeaponParameterDefinition, on_delete=models.CASCADE, related_name="levels"
    )
    level = models.PositiveSmallIntegerField()
    value_raw = models.CharField(max_length=200)
    cost_raw = models.CharField(max_length=200)
    currency = models.CharField(max_length=20, choices=Currency.choices, default=Currency.STONES)
    source_wikidata = models.ForeignKey(
        WikiData,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="uw_parameter_levels",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["parameter_definition", "level"],
                name="uniq_uw_param_level",
            ),
            models.CheckConstraint(
                condition=models.Q(currency=Currency.STONES),
                name="uw_param_currency_stones",
            ),
        ]

    def __str__(self) -> str:
        """Return a concise string for admin/debug usage."""

        return f"{self.parameter_definition} L{self.level}"


class GuardianChipParameterDefinition(models.Model):
    """Parameter definition for a guardian chip upgrade parameter."""

    guardian_chip_definition = models.ForeignKey(
        GuardianChipDefinition,
        on_delete=models.CASCADE,
        related_name="parameter_definitions",
    )
    key = models.CharField(max_length=40, choices=PARAMETER_KEY_CHOICES)
    display_name = models.CharField(max_length=120)
    unit_kind = models.CharField(
        max_length=20, choices=Unit.Kind.choices, default=Unit.Kind.UNKNOWN
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["guardian_chip_definition", "key"],
                name="uniq_guardian_param_definition_key",
            )
        ]

    def __str__(self) -> str:
        """Return a concise string for admin/debug usage."""

        return f"{self.guardian_chip_definition.slug}:{self.key}"


class GuardianChipParameterLevel(models.Model):
    """Wiki-derived level row for a guardian chip parameter."""

    parameter_definition = models.ForeignKey(
        GuardianChipParameterDefinition, on_delete=models.CASCADE, related_name="levels"
    )
    level = models.PositiveSmallIntegerField()
    value_raw = models.CharField(max_length=200)
    cost_raw = models.CharField(max_length=200)
    currency = models.CharField(max_length=20, choices=Currency.choices, default=Currency.BITS)
    source_wikidata = models.ForeignKey(
        WikiData,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="guardian_parameter_levels",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["parameter_definition", "level"],
                name="uniq_guardian_param_level",
            ),
            models.CheckConstraint(
                condition=models.Q(currency=Currency.BITS),
                name="guardian_param_currency_bits",
            ),
        ]

    def __str__(self) -> str:
        """Return a concise string for admin/debug usage."""

        return f"{self.parameter_definition} L{self.level}"
