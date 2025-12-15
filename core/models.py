"""Database models for the core app.

Phase 1 introduces the minimal persistence required to prove the end-to-end
pipeline:

- store raw Battle Report text without destructive transforms,
- deduplicate imports by checksum,
- store only the minimal run metadata needed for a first time-series chart.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone


class PresetTag(models.Model):
    """Player-defined preset label for contextual grouping.

    Presets are intentionally limited to a name-only tag in Phase 2. They
    represent user-provided context without implying strategy or recommendations.

    Attributes:
        name: Human-readable label.
    """

    name = models.CharField(max_length=80, unique=True)

    def __str__(self) -> str:
        """Return the preset tag name for display contexts."""

        return self.name


class GameData(models.Model):
    """Raw, preserved game data payload imported from the player.

    Attributes:
        raw_text: Unmodified Battle Report text as pasted by the user.
        parsed_at: Timestamp when this payload was ingested.
        checksum: Deterministic checksum of normalized raw text used for dedupe.
    """

    raw_text = models.TextField()
    parsed_at = models.DateTimeField(auto_now_add=True)
    checksum = models.CharField(max_length=64, unique=True)

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        return f"GameData({self.checksum[:10]}…, parsed_at={self.parsed_at.isoformat()})"
    
    class Meta:
        verbose_name = "Game Data"
        verbose_name_plural = "Wiki Datum"


class RunProgress(models.Model):
    """Minimal run metadata extracted from a Battle Report.

    Phase 1 scope is intentionally limited to a small set of fields needed for a
    single rate metric chart.

    Attributes:
        game_data: The raw payload this metadata was extracted from.
        battle_date: Battle timestamp from the report, if present.
        tier: Tier value from the report, if present.
        preset_tag: Optional player-defined preset label.
        wave: Final wave reached, if present.
        real_time_seconds: Real time duration in seconds, if present.
    """

    game_data = models.OneToOneField(
        GameData, on_delete=models.CASCADE, related_name="run_progress"
    )
    battle_date = models.DateTimeField(null=True, blank=True)
    tier = models.PositiveSmallIntegerField(null=True, blank=True)
    preset_tag = models.ForeignKey(
        PresetTag,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="runs",
    )
    wave = models.PositiveIntegerField(null=True, blank=True)
    real_time_seconds = models.PositiveIntegerField(null=True, blank=True)

    class Meta: 
        verbose_name = "Game Progress"
        verbose_name_plural = "Game Progress"

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        return f"RunProgress(tier={self.tier}, wave={self.wave}, battle_date={self.battle_date})"


class WikiData(models.Model):
    """Versioned, non-destructive store for wiki-derived table data.

    Wiki-derived data is ingested as raw strings to provide stable inputs for
    later analysis phases. Content fields (name, raw_row, hashes, metadata) are
    treated as immutable once written. Lifecycle fields (`last_seen`,
    `deprecated`) may be updated to support change detection and safe diffing.

    Attributes:
        page_url: Source page URL on the wiki.
        canonical_name: Human-readable entity name (e.g., card name).
        entity_id: Stable, internal identifier derived from the entity name.
        content_hash: Deterministic hash of the raw scraped row content.
        raw_row: Mapping of column header -> raw cell text (whitespace-normalized).
        source_section: Identifier for the source table/section within the page.
        first_seen: When this exact content revision was first observed.
        last_seen: When this content revision was last observed.
        parse_version: Parser version string used to produce `raw_row`.
        deprecated: True when the entity is missing from the latest scrape.
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
                fields=["page_url", "source_section", "parse_version", "entity_id", "content_hash"],
                name="uniq_wikidata_revision",
            )
        ]
        indexes = [
            models.Index(fields=["page_url", "source_section", "parse_version", "entity_id"]),
        ]
        verbose_name = "Wiki Data"
        verbose_name_plural = "Wiki Datum"

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
    """A lightweight unit/metadata model for labeling raw parameter values.

    This model is intentionally small and permissive. It exists to support
    traceable, non-destructive storage of wiki-derived or user-entered values
    without committing to any specific gameplay math in Phase 3.

    Attributes:
        name: Human-friendly unit name (e.g. "seconds", "percent").
        symbol: Optional display symbol (e.g. "s", "%").
        kind: Broad category for display/grouping purposes.
    """

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


class CardDefinition(models.Model):
    """Definition record for a card as shown in the in-app library.

    Attributes:
        name: Card name as presented in the UI.
        wiki_page_url: Optional URL to the wiki source page.
        wiki_entity_id: Optional stable identifier used for wiki ingestion.
        preset_tags: Optional many-to-many labels for grouping cards.
        description: Optional wiki-provided summary text.
        rarity: Optional rarity label.
        unlock_text: Optional unlock-condition text.
    """

    name = models.CharField(max_length=120, unique=True)
    wiki_page_url = models.URLField(blank=True)
    wiki_entity_id = models.CharField(max_length=200, blank=True, db_index=True)
    preset_tags = models.ManyToManyField(
        PresetTag,
        blank=True,
        related_name="card_definitions",
    )
    description = models.TextField(blank=True)
    rarity = models.CharField(max_length=80, blank=True)
    unlock_text = models.TextField(blank=True)

    def __str__(self) -> str:
        """Return the card name for display contexts."""

        return self.name


class CardParameter(models.Model):
    """Raw parameter/value row for a card definition.

    This model is intentionally schema-light in Phase 3. Raw values are stored
    as strings to preserve their original representation.

    Attributes:
        card_definition: Parent card definition.
        key: Parameter name (e.g. "Cooldown reduction").
        raw_value: Raw cell text or user-entered value.
        unit: Optional unit label.
        source_wikidata: Optional pointer to the exact wiki revision used.
    """

    card_definition = models.ForeignKey(
        CardDefinition, on_delete=models.CASCADE, related_name="parameters", editable=False
    )
    card_level = models.ForeignKey(
        "CardLevel", on_delete=models.CASCADE, related_name="parameters", null=True, blank=True
    )
    key = models.CharField(max_length=120)
    raw_value = models.CharField(max_length=200)
    unit = models.ForeignKey(Unit, null=True, blank=True, on_delete=models.SET_NULL)
    source_wikidata = models.ForeignKey(
        WikiData,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="card_parameters",
    )

    class Meta:
        indexes = [
            models.Index(fields=["card_definition", "key"]),
            models.Index(fields=["card_level", "key"]),
        ]

    def save(self, *args, **kwargs):
        """Ensure parameters are scoped to a card level and definition."""

        if self.card_level_id is None:
            raise ValueError("CardParameter requires a card_level reference")
        self.card_definition = self.card_level.card_definition
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        return f"{self.card_definition.name} L{self.card_level.level}: {self.key}={self.raw_value}"


class CardLevel(models.Model):
    """Structural card level/star record for later upgrade tables.

    Attributes:
        card_definition: Parent card definition.
        level: Card level (best-effort integer).
        star: Optional star/tier indicator (best-effort integer).
        raw_row: Optional raw mapping for traceability.
        source_wikidata: Optional pointer to the exact wiki revision used.
    """

    card_definition = models.ForeignKey(
        CardDefinition, on_delete=models.CASCADE, related_name="levels"
    )
    level = models.PositiveSmallIntegerField()
    star = models.PositiveSmallIntegerField(null=True, blank=True)
    raw_row = models.JSONField(default=dict, blank=True)
    source_wikidata = models.ForeignKey(
        WikiData,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="card_levels",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["card_definition", "level", "star"],
                name="uniq_card_level_star",
            )
        ]
        indexes = [
            models.Index(fields=["card_definition", "level"]),
        ]

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        star = f"★{self.star}" if self.star is not None else "★?"
        return f"{self.card_definition.name} L{self.level} {star}"


class CardSlot(models.Model):
    """Structural definition of a card slot unlock milestone.

    Attributes:
        slot_number: Slot index (1-based).
        unlock_cost_raw: Raw unlock cost representation (e.g. "50M coins").
        source_wikidata: Optional pointer to the exact wiki revision used.
        notes: Optional freeform notes for later UX.
    """

    slot_number = models.PositiveSmallIntegerField(unique=True)
    unlock_cost_raw = models.CharField(max_length=80, blank=True)
    source_wikidata = models.ForeignKey(
        WikiData,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="card_slots",
    )
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        return f"CardSlot({self.slot_number})"


class BotDefinition(models.Model):
    """Definition record for a bot as shown in the in-app library."""

    name = models.CharField(max_length=120, unique=True)
    wiki_page_url = models.URLField(blank=True)
    wiki_entity_id = models.CharField(max_length=200, blank=True, db_index=True)
    description = models.TextField(blank=True)
    rarity = models.CharField(max_length=80, blank=True)
    unlock_text = models.TextField(blank=True)

    def __str__(self) -> str:
        """Return the bot name for display contexts."""

        return self.name


class BotLevel(models.Model):
    """Structural bot level record linking parameters to revisions."""

    bot_definition = models.ForeignKey(
        BotDefinition, on_delete=models.CASCADE, related_name="levels"
    )
    level = models.PositiveSmallIntegerField()
    star = models.PositiveSmallIntegerField(null=True, blank=True)
    raw_row = models.JSONField(default=dict, blank=True)
    source_wikidata = models.ForeignKey(
        WikiData,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bot_levels",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["bot_definition", "level", "star"],
                name="uniq_bot_level_star",
            )
        ]
        indexes = [
            models.Index(fields=["bot_definition", "level"]),
        ]

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        star = f"★{self.star}" if self.star is not None else "★?"
        return f"{self.bot_definition.name} L{self.level} {star}"


class BotParameter(models.Model):
    """Raw parameter/value row for bot upgrades."""

    bot_definition = models.ForeignKey(
        BotDefinition, on_delete=models.CASCADE, related_name="parameters", editable=False
    )
    bot_level = models.ForeignKey(
        BotLevel, on_delete=models.CASCADE, related_name="parameters"
    )
    key = models.CharField(max_length=120)
    raw_value = models.CharField(max_length=200)
    unit = models.ForeignKey(Unit, null=True, blank=True, on_delete=models.SET_NULL)
    source_wikidata = models.ForeignKey(
        WikiData,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bot_parameters",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["bot_level", "key"], name="uniq_bot_level_parameter_key"
            )
        ]
        indexes = [
            models.Index(fields=["bot_definition", "key"]),
            models.Index(fields=["bot_level", "key"]),
        ]

    def save(self, *args, **kwargs):
        """Ensure parameters are scoped to a bot level and definition."""

        if self.bot_level_id is None:
            raise ValueError("BotParameter requires a bot_level reference")
        self.bot_definition = self.bot_level.bot_definition
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        return f"{self.bot_definition.name} L{self.bot_level.level}: {self.key}={self.raw_value}"


class GuardianChipDefinition(models.Model):
    """Definition record for guardian chips."""

    name = models.CharField(max_length=120, unique=True)
    wiki_page_url = models.URLField(blank=True)
    wiki_entity_id = models.CharField(max_length=200, blank=True, db_index=True)
    description = models.TextField(blank=True)
    rarity = models.CharField(max_length=80, blank=True)
    unlock_text = models.TextField(blank=True)

    def __str__(self) -> str:
        """Return the chip name for display contexts."""

        return self.name


class GuardianChipLevel(models.Model):
    """Structural guardian chip level record for parameter scoping."""

    guardian_chip_definition = models.ForeignKey(
        GuardianChipDefinition, on_delete=models.CASCADE, related_name="levels"
    )
    level = models.PositiveSmallIntegerField()
    star = models.PositiveSmallIntegerField(null=True, blank=True)
    raw_row = models.JSONField(default=dict, blank=True)
    source_wikidata = models.ForeignKey(
        WikiData,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="guardian_chip_levels",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["guardian_chip_definition", "level", "star"],
                name="uniq_guardian_chip_level_star",
            )
        ]
        indexes = [
            models.Index(fields=["guardian_chip_definition", "level"]),
        ]

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        star = f"★{self.star}" if self.star is not None else "★?"
        return f"{self.guardian_chip_definition.name} L{self.level} {star}"


class GuardianChipParameter(models.Model):
    """Raw parameter/value row for guardian chip upgrade tables."""

    guardian_chip_definition = models.ForeignKey(
        GuardianChipDefinition,
        on_delete=models.CASCADE,
        related_name="parameters",
        editable=False,
    )
    guardian_chip_level = models.ForeignKey(
        GuardianChipLevel, on_delete=models.CASCADE, related_name="parameters"
    )
    key = models.CharField(max_length=120)
    raw_value = models.CharField(max_length=200)
    unit = models.ForeignKey(Unit, null=True, blank=True, on_delete=models.SET_NULL)
    source_wikidata = models.ForeignKey(
        WikiData,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="guardian_chip_parameters",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["guardian_chip_level", "key"],
                name="uniq_guardian_chip_level_parameter_key",
            )
        ]
        indexes = [
            models.Index(fields=["guardian_chip_definition", "key"]),
            models.Index(fields=["guardian_chip_level", "key"]),
        ]

    def save(self, *args, **kwargs):
        """Ensure parameters are scoped to a guardian chip level and definition."""

        if self.guardian_chip_level_id is None:
            raise ValueError("GuardianChipParameter requires a guardian_chip_level reference")
        self.guardian_chip_definition = self.guardian_chip_level.guardian_chip_definition
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        return (
            f"{self.guardian_chip_definition.name} L{self.guardian_chip_level.level}: "
            f"{self.key}={self.raw_value}"
        )


class UltimateWeaponDefinition(models.Model):
    """Definition record for ultimate weapons."""

    name = models.CharField(max_length=120, unique=True)
    wiki_page_url = models.URLField(blank=True)
    wiki_entity_id = models.CharField(max_length=200, blank=True, db_index=True)
    description = models.TextField(blank=True)
    rarity = models.CharField(max_length=80, blank=True)
    unlock_text = models.TextField(blank=True)

    def __str__(self) -> str:
        """Return the weapon name for display contexts."""

        return self.name


class UltimateWeaponLevel(models.Model):
    """Structural ultimate weapon level record."""

    ultimate_weapon_definition = models.ForeignKey(
        UltimateWeaponDefinition, on_delete=models.CASCADE, related_name="levels"
    )
    level = models.PositiveSmallIntegerField()
    star = models.PositiveSmallIntegerField(null=True, blank=True)
    raw_row = models.JSONField(default=dict, blank=True)
    source_wikidata = models.ForeignKey(
        WikiData,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ultimate_weapon_levels",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ultimate_weapon_definition", "level", "star"],
                name="uniq_ultimate_weapon_level_star",
            )
        ]
        indexes = [
            models.Index(fields=["ultimate_weapon_definition", "level"]),
        ]

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        star = f"★{self.star}" if self.star is not None else "★?"
        return f"{self.ultimate_weapon_definition.name} L{self.level} {star}"


class UltimateWeaponParameter(models.Model):
    """Raw parameter/value row for ultimate weapon upgrade tables."""

    ultimate_weapon_definition = models.ForeignKey(
        UltimateWeaponDefinition,
        on_delete=models.CASCADE,
        related_name="parameters",
        editable=False,
    )
    ultimate_weapon_level = models.ForeignKey(
        UltimateWeaponLevel, on_delete=models.CASCADE, related_name="parameters"
    )
    key = models.CharField(max_length=120)
    raw_value = models.CharField(max_length=200)
    unit = models.ForeignKey(Unit, null=True, blank=True, on_delete=models.SET_NULL)
    source_wikidata = models.ForeignKey(
        WikiData,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ultimate_weapon_parameters",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ultimate_weapon_level", "key"],
                name="uniq_uw_level_parameter_key",
            )
        ]
        indexes = [
            models.Index(fields=["ultimate_weapon_definition", "key"]),
            models.Index(fields=["ultimate_weapon_level", "key"]),
        ]

    def save(self, *args, **kwargs):
        """Ensure parameters are scoped to an ultimate weapon level and definition."""

        if self.ultimate_weapon_level_id is None:
            raise ValueError("UltimateWeaponParameter requires an ultimate_weapon_level reference")
        self.ultimate_weapon_definition = self.ultimate_weapon_level.ultimate_weapon_definition
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        return (
            f"{self.ultimate_weapon_definition.name} L{self.ultimate_weapon_level.level}: "
            f"{self.key}={self.raw_value}"
        )


class PlayerCard(models.Model):
    """Player-owned card progress record (single-player by default).

    Attributes:
        card_definition: The card being tracked.
        owned: Whether the player owns the card.
        level: Player's current card level (best-effort).
        star: Player's current star level (best-effort).
        updated_at: Timestamp when this record was last updated.
        notes: Optional freeform notes.
    """

    card_definition = models.OneToOneField(
        CardDefinition, on_delete=models.CASCADE, related_name="player_state"
    )
    owned = models.BooleanField(default=False)
    level = models.PositiveSmallIntegerField(null=True, blank=True)
    star = models.PositiveSmallIntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        owned = "owned" if self.owned else "unowned"
        return f"PlayerCard({self.card_definition.name}, {owned})"


class PlayerGuardianChip(models.Model):
    """Player-owned guardian chip progress record (structural stub)."""

    chip_name = models.CharField(max_length=120, unique=True)
    owned = models.BooleanField(default=False)
    level = models.PositiveSmallIntegerField(null=True, blank=True)
    star = models.PositiveSmallIntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        """Return the chip name for display contexts."""

        return self.chip_name


class PlayerUltimateWeapon(models.Model):
    """Player-owned ultimate weapon progress record (structural stub)."""

    weapon_name = models.CharField(max_length=120, unique=True)
    unlocked = models.BooleanField(default=False)
    level = models.PositiveSmallIntegerField(null=True, blank=True)
    star = models.PositiveSmallIntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        """Return the weapon name for display contexts."""

        return self.weapon_name


class PlayerBot(models.Model):
    """Player-owned bot progress record (structural stub)."""

    bot_name = models.CharField(max_length=120, unique=True)
    unlocked = models.BooleanField(default=False)
    level = models.PositiveSmallIntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        """Return the bot name for display contexts."""

        return self.bot_name
