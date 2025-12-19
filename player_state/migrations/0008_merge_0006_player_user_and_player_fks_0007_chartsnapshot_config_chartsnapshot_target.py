"""Merge divergent migration branches for the `player_state` app.

This migration resolves the split created by:
- 0006_player_user_and_player_fks
- 0007_chartsnapshot_config_chartsnapshot_target
"""

from __future__ import annotations

from django.db import migrations


class Migration(migrations.Migration):
    """Merge migration for `player_state`."""

    dependencies = [
        ("player_state", "0006_player_user_and_player_fks"),
        ("player_state", "0007_chartsnapshot_config_chartsnapshot_target"),
    ]

    operations = []

