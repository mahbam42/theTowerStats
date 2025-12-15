"""Purge structured wiki-derived Definitions (Definitions layer).

This command deletes only:
- definition rows (bots/UWs/guardians/cards),
- parameter definition rows,
- parameter level rows.

It does not delete `definitions.WikiData` and does not touch Player State or
GameData tables (though FK relationships may be nulled via `SET_NULL`).
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from definitions.models import (
    BotDefinition,
    BotParameterDefinition,
    BotParameterLevel,
    CardDefinition,
    GuardianChipDefinition,
    GuardianChipParameterDefinition,
    GuardianChipParameterLevel,
    UltimateWeaponDefinition,
    UltimateWeaponParameterDefinition,
    UltimateWeaponParameterLevel,
)


class Command(BaseCommand):
    """Purge structured wiki-derived definition tables."""

    help = "Delete definition + parameter tables (WikiData is retained)."

    def add_arguments(self, parser) -> None:
        """Add command arguments."""

        parser.add_argument(
            "--check",
            action="store_true",
            help="Dry-run: print what would be deleted.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Required to actually delete rows.",
        )

    def handle(self, *args, **options) -> str | None:
        """Run the command."""

        check: bool = options["check"]
        force: bool = options["force"]

        if check and force:
            raise CommandError("Use either --check or --force, not both.")
        if not check and not force:
            raise CommandError("Refusing to delete without explicit intent; pass --check or --force.")

        mode = "CHECK" if check else "DELETE"
        counts = {
            "bot_parameter_levels": BotParameterLevel.objects.count(),
            "bot_parameter_definitions": BotParameterDefinition.objects.count(),
            "bots": BotDefinition.objects.count(),
            "uw_parameter_levels": UltimateWeaponParameterLevel.objects.count(),
            "uw_parameter_definitions": UltimateWeaponParameterDefinition.objects.count(),
            "ultimate_weapons": UltimateWeaponDefinition.objects.count(),
            "guardian_parameter_levels": GuardianChipParameterLevel.objects.count(),
            "guardian_parameter_definitions": GuardianChipParameterDefinition.objects.count(),
            "guardians": GuardianChipDefinition.objects.count(),
            "cards": CardDefinition.objects.count(),
        }
        self.stdout.write(f"[{mode}] would_delete={counts}")
        if check:
            return None

        with transaction.atomic():
            BotParameterLevel.objects.all().delete()
            BotParameterDefinition.objects.all().delete()
            BotDefinition.objects.all().delete()

            UltimateWeaponParameterLevel.objects.all().delete()
            UltimateWeaponParameterDefinition.objects.all().delete()
            UltimateWeaponDefinition.objects.all().delete()

            GuardianChipParameterLevel.objects.all().delete()
            GuardianChipParameterDefinition.objects.all().delete()
            GuardianChipDefinition.objects.all().delete()

            CardDefinition.objects.all().delete()

        self.stdout.write("[DELETE] completed")
        return None

