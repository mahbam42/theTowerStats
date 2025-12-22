"""Add manual tournament flag to BattleReportProgress.

Tournament runs are normally inferred from the Tier label, but the game UI can
mark tournament rounds without reflecting it in copied text. This migration
adds a boolean field so players can explicitly tag runs at import time.
"""

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    """Schema migration adding BattleReportProgress.is_tournament."""

    dependencies = [
        ("gamedata", "0004_player_scoping"),
    ]

    operations = [
        migrations.AddField(
            model_name="battlereportprogress",
            name="is_tournament",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Manual override: mark this run as a tournament when the report text does not indicate it."
                ),
            ),
        ),
    ]

