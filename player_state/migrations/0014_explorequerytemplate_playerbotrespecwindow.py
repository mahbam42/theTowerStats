"""Add Explore query templates and Bot Respec Event-window tracking."""

from __future__ import annotations

import django.db.models.deletion
from django.db import migrations, models


def seed_explore_query_templates(apps, schema_editor) -> None:
    """Create the initial admin-managed Explore template records."""

    ExploreQueryTemplate = apps.get_model("player_state", "ExploreQueryTemplate")
    ExploreQueryTemplate.objects.update_or_create(
        name="Farming Efficiency by Tier",
        defaults={
            "description": (
                "Starting point for comparing observed farming efficiency by tier "
                "without auto-running the query."
            ),
            "dsl_text": "\n".join(
                [
                    'name "Farming Efficiency by Tier"',
                    "scope date [date:YYYY-MM-DD]..[date:YYYY-MM-DD]",
                    "scope tier all not tournament",
                    "scope preset [preset:—]",
                    "scope snapshot [snapshot:—]",
                    "scope past_n_runs [runs:—]",
                    "breakdown by tier",
                    "metric coins_per_hour avg",
                    "# Optional secondary metrics (avg):",
                    "# metric coins_earned avg",
                    "# metric real_time_hours avg",
                    "# metric cells_earned avg",
                    "# metric reroll_shards_earned avg",
                    "# metric waves_reached avg",
                    "output table",
                ]
            ),
            "tags": "economy, farming, starter",
            "is_active": True,
        },
    )


def unseed_explore_query_templates(apps, schema_editor) -> None:
    """Remove the initial Explore template records added by this migration."""

    ExploreQueryTemplate = apps.get_model("player_state", "ExploreQueryTemplate")
    ExploreQueryTemplate.objects.filter(name="Farming Efficiency by Tier").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('player_state', '0013_player_guardian_chip_slots_unlocked'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExploreQueryTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
                ('description', models.TextField(blank=True)),
                ('dsl_text', models.TextField(help_text='Explore DSL copied into the editor when a player uses the template.')),
                ('tags', models.CharField(blank=True, help_text='Optional comma-separated tags for lightweight Explore categorization.', max_length=255)),
                ('is_active', models.BooleanField(default=True, help_text='Hide inactive templates from Explore without deleting them.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('name', 'id'),
            },
        ),
        migrations.CreateModel(
            name='PlayerBotRespecWindow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('window_start', models.DateField()),
                ('window_end', models.DateField()),
                ('used_at', models.DateTimeField(auto_now_add=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bot_respec_windows', to='player_state.player')),
            ],
            options={
                'ordering': ('-window_start', '-used_at'),
                'constraints': [models.UniqueConstraint(fields=('player', 'window_start', 'window_end'), name='uniq_player_bot_respec_window')],
            },
        ),
        migrations.RunPython(seed_explore_query_templates, unseed_explore_query_templates),
    ]
