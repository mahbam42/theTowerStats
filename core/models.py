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
