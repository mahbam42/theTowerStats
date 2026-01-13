"""Add Explore query persistence."""

from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """Create ExploreQuery for player-authored Explore queries."""

    dependencies = [
        ("player_state", "0011_chart_preferences_and_saved_builder"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExploreQuery",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("schema_version", models.CharField(default="1.0", max_length=20)),
                ("query", models.JSONField(default=dict, help_text="Versioned Explore query payload (schema-driven).")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="explore_queries",
                        to="player_state.player",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("player", "name"),
                        name="uniq_player_explore_query_name",
                    )
                ],
            },
        ),
    ]

