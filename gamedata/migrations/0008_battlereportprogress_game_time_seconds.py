"""Add game_time_seconds to BattleReportProgress."""

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    """Add BattleReportProgress.game_time_seconds."""

    dependencies = [
        ("gamedata", "0007_battlereportprogress_tournament_rank"),
    ]

    operations = [
        migrations.AddField(
            model_name="battlereportprogress",
            name="game_time_seconds",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Parsed Game Time duration in seconds from the Battle Report.",
                null=True,
            ),
        ),
    ]
