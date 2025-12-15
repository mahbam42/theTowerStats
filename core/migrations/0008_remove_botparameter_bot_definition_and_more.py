"""Remove legacy core models after the Prompt12 app split.

This migration deletes the old `core` app models that were moved into the new
layered apps (`definitions`, `player_state`, `gamedata`).

It intentionally uses `DeleteModel` operations (instead of field-by-field
removals) to avoid SQLite table-remake issues with constraints during test DB
creation.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_gamedata_options_alter_runprogress_options_and_more'),
    ]

    operations = [
        # GameData (Phase 1 legacy)
        migrations.DeleteModel(name="RunProgress"),
        migrations.DeleteModel(name="GameData"),
        migrations.DeleteModel(name="PresetTag"),
        # Player State (Phase 3 legacy stubs)
        migrations.DeleteModel(name="PlayerCard"),
        migrations.DeleteModel(name="PlayerBot"),
        migrations.DeleteModel(name="PlayerGuardianChip"),
        migrations.DeleteModel(name="PlayerUltimateWeapon"),
        # Definitions (Phase 3 legacy)
        migrations.DeleteModel(name="CardParameter"),
        migrations.DeleteModel(name="CardLevel"),
        migrations.DeleteModel(name="CardSlot"),
        migrations.DeleteModel(name="CardDefinition"),
        migrations.DeleteModel(name="BotParameter"),
        migrations.DeleteModel(name="BotLevel"),
        migrations.DeleteModel(name="BotDefinition"),
        migrations.DeleteModel(name="GuardianChipParameter"),
        migrations.DeleteModel(name="GuardianChipLevel"),
        migrations.DeleteModel(name="GuardianChipDefinition"),
        migrations.DeleteModel(name="UltimateWeaponParameter"),
        migrations.DeleteModel(name="UltimateWeaponLevel"),
        migrations.DeleteModel(name="UltimateWeaponDefinition"),
        migrations.DeleteModel(name="WikiData"),
        migrations.DeleteModel(name="Unit"),
    ]
