"""Add Battle History column preference storage."""

from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """Add Battle History column preference storage."""

    dependencies = [
        ("player_state", "0009_goaltarget"),
    ]

    operations = [
        migrations.CreateModel(
            name="BattleHistoryColumnPreference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "player",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="battle_history_column_preferences",
                        to="player_state.player",
                    ),
                ),
                (
                    "columns",
                    models.JSONField(
                        default=list,
                        help_text="Ordered list of visible Battle History column keys.",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
