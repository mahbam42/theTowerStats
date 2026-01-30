"""Add guardian chip slot unlock tracking to Player."""

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    """Add guardian chip slots unlocked field."""

    dependencies = [
        ("player_state", "0012_explore_query"),
    ]

    operations = [
        migrations.AddField(
            model_name="player",
            name="guardian_chip_slots_unlocked",
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
