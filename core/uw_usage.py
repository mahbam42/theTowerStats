"""Django-facing helpers for observed Ultimate Weapon usage in Battle Reports."""

from __future__ import annotations

from collections import Counter

from analysis.uw_usage import observed_active_ultimate_weapons
from definitions.models import UltimateWeaponDefinition
from gamedata.models import BattleReport
from player_state.models import Player


def count_observed_uw_runs(*, player: Player) -> dict[int, int]:
    """Count how many Battle Reports show each Ultimate Weapon as active.

    Args:
        player: Owning player whose Battle Reports should be scanned.

    Returns:
        Dict mapping `UltimateWeaponDefinition.id` to the number of Battle Reports
        where that Ultimate Weapon has evidence of being active (value > 0 for a
        mapped Battle Report metric).
    """

    definitions_by_name = {
        definition.name: definition.id for definition in UltimateWeaponDefinition.objects.order_by("id")
    }
    counts: Counter[int] = Counter()
    for report in BattleReport.objects.filter(player=player).only("raw_text"):
        for uw_name in observed_active_ultimate_weapons(report.raw_text or ""):
            definition_id = definitions_by_name.get(uw_name)
            if definition_id is not None:
                counts[definition_id] += 1
    return dict(counts)

