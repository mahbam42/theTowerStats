"""Add guardian chip activation state."""

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    """Add the PlayerGuardianChip.active boolean flag."""

    dependencies = [
        ("player_state", "0003_preset_color"),
    ]

    operations = [
        migrations.AddField(
            model_name="playerguardianchip",
            name="active",
            field=models.BooleanField(default=False),
        ),
    ]

