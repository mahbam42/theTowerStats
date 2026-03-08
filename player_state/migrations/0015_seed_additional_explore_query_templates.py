"""Seed additional admin-managed Explore query templates."""

from __future__ import annotations

from django.db import migrations


def seed_additional_explore_query_templates(apps, schema_editor) -> None:
    """Create additional built-in Explore templates for common workflows."""

    ExploreQueryTemplate = apps.get_model("player_state", "ExploreQueryTemplate")
    templates = (
        {
            "name": "Guardian Chip Performance",
            "description": (
                "Starting point for reviewing Guardian chip contribution across "
                "recent runs without auto-running the query."
            ),
            "dsl_text": "\n".join(
                [
                    'name "Guardian Chip Performance"',
                    "scope date [date:YYYY-MM-DD]..[date:YYYY-MM-DD]",
                    "scope tier [tier:—]",
                    "scope preset [preset:—]",
                    "scope snapshot [snapshot:—]",
                    "scope past_n_runs 5",
                    "breakdown by date",
                    (
                        "metric guardian_damage sum and guardian_coins_stolen sum "
                        "and guardian_gems_fetched sum and guardian_medals_fetched sum "
                        "and guardian_reroll_shards_fetched sum "
                        "and guardian_summoned_enemies sum"
                    ),
                ]
            ),
            "tags": "guardian, performance, starter",
            "is_active": True,
        },
        {
            "name": "Reroll Shards Earned",
            "description": (
                "Starting point for comparing observed reroll shard income by tier "
                "without auto-running the query."
            ),
            "dsl_text": "\n".join(
                [
                    'name "Reroll Shards Earned"',
                    "scope date [date:YYYY-MM-DD]..[date:YYYY-MM-DD]",
                    "scope tier [tier:—] not tournament",
                    "scope preset [preset:—]",
                    "scope snapshot [snapshot:—]",
                    "scope past_n_runs [runs:—]",
                    "scope hidden exclude",
                    "breakdown by tier",
                    "metric reroll_shards_earned avg",
                    "output bar",
                ]
            ),
            "tags": "economy, reroll shards, starter",
            "is_active": True,
        },
    )

    for template in templates:
        ExploreQueryTemplate.objects.get_or_create(
            name=template["name"],
            defaults=template,
        )


def unseed_additional_explore_query_templates(apps, schema_editor) -> None:
    """Remove the additional Explore templates added by this migration."""

    ExploreQueryTemplate = apps.get_model("player_state", "ExploreQueryTemplate")
    ExploreQueryTemplate.objects.filter(
        name__in=("Guardian Chip Performance", "Reroll Shards Earned")
    ).delete()


class Migration(migrations.Migration):
    """Add more built-in Explore templates."""

    dependencies = [
        ("player_state", "0014_explorequerytemplate_playerbotrespecwindow"),
    ]

    operations = [
        migrations.RunPython(
            seed_additional_explore_query_templates,
            unseed_additional_explore_query_templates,
        ),
    ]
