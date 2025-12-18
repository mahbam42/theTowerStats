"""Add effective value fields to player parameter rows."""

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    """Add optional effective value + notes fields for player parameters."""

    dependencies = [
        ("player_state", "0004_playerguardianchip_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="playerbotparameter",
            name="effective_value_raw",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Optional authoritative effective value (do not compute; explanatory only).",
                max_length=64,
            ),
        ),
        migrations.AddField(
            model_name="playerbotparameter",
            name="effective_notes",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Optional explanation lines for effective value (no calculations).",
            ),
        ),
        migrations.AddField(
            model_name="playerultimateweaponparameter",
            name="effective_value_raw",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Optional authoritative effective value (do not compute; explanatory only).",
                max_length=64,
            ),
        ),
        migrations.AddField(
            model_name="playerultimateweaponparameter",
            name="effective_notes",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Optional explanation lines for effective value (no calculations).",
            ),
        ),
        migrations.AddField(
            model_name="playerguardianchipparameter",
            name="effective_value_raw",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Optional authoritative effective value (do not compute; explanatory only).",
                max_length=64,
            ),
        ),
        migrations.AddField(
            model_name="playerguardianchipparameter",
            name="effective_notes",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Optional explanation lines for effective value (no calculations).",
            ),
        ),
    ]

