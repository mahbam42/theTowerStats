"""Observed Ultimate Weapon usage detection from Battle Report text.

This module provides a deterministic, best-effort mapping from Ultimate Weapon
names to Battle Report metrics that can be used as evidence that a weapon was
active during a run.

It intentionally stays in the analysis layer:
- pure (no Django imports, no DB writes),
- defensive on missing labels (missing -> inactive),
- testable (stable inputs/outputs).
"""

from __future__ import annotations

from dataclasses import dataclass

from .battle_report_extract import extract_numeric_value
from .quantity import UnitType


@dataclass(frozen=True, slots=True)
class UWUsageRule:
    """Rule describing how to infer UW activity from a Battle Report.

    Args:
        label: Exact Battle Report label to read.
        unit_type: Unit category to validate when parsing the value.
    """

    label: str
    unit_type: UnitType


_UW_RULES_BY_NAME: dict[str, UWUsageRule] = {
    "black hole": UWUsageRule(label="Black Hole Damage", unit_type=UnitType.damage),
    "chain lightning": UWUsageRule(label="Chain Lightning Damage", unit_type=UnitType.damage),
    "death wave": UWUsageRule(label="Death Wave Damage", unit_type=UnitType.damage),
    "golden tower": UWUsageRule(label="Coins From Golden Tower", unit_type=UnitType.coins),
    "inner land mines": UWUsageRule(label="Inner Land Mine Damage", unit_type=UnitType.damage),
    "poison swamp": UWUsageRule(label="Swamp Damage", unit_type=UnitType.damage),
    "smart missiles": UWUsageRule(label="Smart Missile Damage", unit_type=UnitType.damage),
    "spotlight": UWUsageRule(label="Destroyed in Spotlight", unit_type=UnitType.count),
}


def is_ultimate_weapon_observed_active(raw_text: str, *, ultimate_weapon_name: str) -> bool:
    """Return True when a Battle Report shows evidence of an Ultimate Weapon being active.

    Args:
        raw_text: Raw Battle Report text as imported/stored.
        ultimate_weapon_name: Display name for the Ultimate Weapon (e.g. "Black Hole").

    Returns:
        True when the mapped Battle Report metric parses and is > 0; otherwise False.
    """

    rule = _UW_RULES_BY_NAME.get((ultimate_weapon_name or "").strip().casefold())
    if rule is None:
        return False

    extracted = extract_numeric_value(raw_text or "", label=rule.label, unit_type=rule.unit_type)
    if extracted is None:
        return False

    return extracted.value > 0


def observed_active_ultimate_weapons(raw_text: str) -> frozenset[str]:
    """Return a set of Ultimate Weapon names observed as active in a Battle Report.

    Args:
        raw_text: Raw Battle Report text as imported/stored.

    Returns:
        Frozen set of Ultimate Weapon display names that appear active in the run.
    """

    active: set[str] = set()
    for name, rule in _UW_RULES_BY_NAME.items():
        extracted = extract_numeric_value(raw_text or "", label=rule.label, unit_type=rule.unit_type)
        if extracted is None:
            continue
        if extracted.value > 0:
            active.add(_title_case_uw_name(name))
    return frozenset(active)


def _title_case_uw_name(name_casefold: str) -> str:
    """Return the canonical display casing for known Ultimate Weapon names.

    Args:
        name_casefold: Casefolded Ultimate Weapon name.

    Returns:
        Display name matching the known title case stored in definitions.
    """

    # Keep this mapping explicit so user-facing labels remain deterministic.
    return {
        "black hole": "Black Hole",
        "chain lightning": "Chain Lightning",
        "death wave": "Death Wave",
        "golden tower": "Golden Tower",
        "inner land mines": "Inner Land Mines",
        "poison swamp": "Poison Swamp",
        "smart missiles": "Smart Missiles",
        "spotlight": "Spotlight",
    }.get(name_casefold, name_casefold)

