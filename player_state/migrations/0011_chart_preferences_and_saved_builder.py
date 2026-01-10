"""Add chart dashboard preferences and saved Chart Builder configs."""

from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """Schema migration for chart preferences and saved builder configs."""

    dependencies = [
        ("player_state", "0010_battle_history_column_preference"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChartDashboardPreference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("favorite_chart_ids", models.JSONField(default=list, help_text="Ordered list of chart ids marked as favorites.")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "player",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chart_dashboard_preferences",
                        to="player_state.player",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ChartBuilderSavedConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("config", models.JSONField(default=dict, help_text="Versioned ChartConfigDTO payload for the saved chart.")),
                ("chart_builder", models.JSONField(default=dict, help_text="Chart Builder inputs used to recreate this saved chart.")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chart_builder_saved_configs",
                        to="player_state.player",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("player", "name"),
                        name="uniq_player_chart_builder_saved_config",
                    )
                ],
            },
        ),
    ]
