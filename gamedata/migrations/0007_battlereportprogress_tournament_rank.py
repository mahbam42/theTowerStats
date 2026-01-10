"""Add tournament_rank to BattleReportProgress."""

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    """Schema migration adding BattleReportProgress.tournament_rank."""

    dependencies = [
        ("gamedata", "0006_battlereportderivedmetrics"),
    ]

    operations = [
        migrations.AddField(
            model_name="battlereportprogress",
            name="tournament_rank",
            field=models.CharField(
                blank=True,
                choices=[
                    ("copper", "Copper"),
                    ("silver", "Silver"),
                    ("gold", "Gold"),
                    ("platinum", "Platinum"),
                    ("champions", "Champions"),
                    ("legends", "Legends"),
                ],
                help_text="Optional tournament rank recorded during import.",
                max_length=20,
                null=True,
            ),
        ),
    ]
