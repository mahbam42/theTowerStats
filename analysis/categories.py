"""Shared metric category definitions.

MetricCategory is a semantic classification (not purely visual) used to ensure
new metrics are registered consistently and scoped predictably.
"""

from __future__ import annotations

from enum import StrEnum


class MetricCategory(StrEnum):
    """Semantic category for a metric.

    Values are stable identifiers used across the analysis registry and UI.
    """

    economy = "economy"
    efficiency = "efficiency"
    damage = "damage"
    enemy_destruction = "enemy_destruction"
    combat = "combat"
    fetch = "fetch"
    utility = "utility"
