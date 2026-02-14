"""Add is_hidden flag to BattleReport."""

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    """Add is_hidden flag to BattleReport."""

    dependencies = [
        ("gamedata", "0008_battlereportprogress_game_time_seconds"),
    ]

    operations = [
        migrations.AddField(
            model_name="battlereport",
            name="is_hidden",
            field=models.BooleanField(
                default=False,
                help_text="Exclude this report from Charts and Explore unless explicitly included.",
            ),
        ),
    ]
