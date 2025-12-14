"""Database models for the core app.

Phase 1 introduces the minimal persistence required to prove the end-to-end
pipeline:

- store raw Battle Report text without destructive transforms,
- deduplicate imports by checksum,
- store only the minimal run metadata needed for a first time-series chart.
"""

from __future__ import annotations

from django.db import models


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
        wave: Final wave reached, if present.
        real_time_seconds: Real time duration in seconds, if present.
    """

    game_data = models.OneToOneField(
        GameData, on_delete=models.CASCADE, related_name="run_progress"
    )
    battle_date = models.DateTimeField(null=True, blank=True)
    tier = models.PositiveSmallIntegerField(null=True, blank=True)
    wave = models.PositiveIntegerField(null=True, blank=True)
    real_time_seconds = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self) -> str:
        """Return a concise display string for admin/debug usage."""

        return f"RunProgress(tier={self.tier}, wave={self.wave}, battle_date={self.battle_date})"
