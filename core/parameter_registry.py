"""Registry of allowed parameter keys for wiki ingestion.

The registry enforces a closed set of parameter names per entity to prevent
metadata or unknown headers from being treated as numeric parameters. Each
entry captures the owning system, a stable entity slug, the parameter key as it
appears in wiki tables, and the expected :class:`core.models.Unit.Kind`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Tuple

from core.models import Unit


@dataclass(frozen=True, slots=True)
class ParameterKey:
    """Single allowed parameter key scoped to a system + entity.

    Attributes:
        system: One of ``bot``, ``uw``, or ``guardian``.
        entity_slug: Stable slug for the entity (e.g., ``flame`` bot).
        parameter: Canonical parameter header from the wiki table.
        unit_kind: Expected :class:`core.models.Unit.Kind` for the parameter.
    """

    system: str
    entity_slug: str
    parameter: str
    unit_kind: Unit.Kind


def _index_registry(entries: Iterable[ParameterKey]) -> Dict[Tuple[str, str, str], ParameterKey]:
    """Build a keyed index and guard against duplicate registrations."""

    index: Dict[Tuple[str, str, str], ParameterKey] = {}
    for entry in entries:
        key = (entry.system, entry.entity_slug, entry.parameter)
        if key in index:
            raise ValueError(f"Duplicate parameter registry entry for {key}")
        index[key] = entry
    return index


PARAMETER_KEY_REGISTRY: tuple[ParameterKey, ...] = (
    # Bots
    ParameterKey("bot", "amplify", "Damage", Unit.Kind.COUNT),
    ParameterKey("bot", "amplify", "Duration", Unit.Kind.SECONDS),
    ParameterKey("bot", "amplify", "Cooldown", Unit.Kind.SECONDS),
    ParameterKey("bot", "flame", "Damage", Unit.Kind.COUNT),
    ParameterKey("bot", "flame", "Duration", Unit.Kind.SECONDS),
    ParameterKey("bot", "flame", "Cooldown", Unit.Kind.SECONDS),
    ParameterKey("bot", "thunder", "Damage", Unit.Kind.COUNT),
    ParameterKey("bot", "thunder", "Duration", Unit.Kind.SECONDS),
    ParameterKey("bot", "thunder", "Cooldown", Unit.Kind.SECONDS),
    ParameterKey("bot", "golden", "Damage", Unit.Kind.COUNT),
    ParameterKey("bot", "golden", "Duration", Unit.Kind.SECONDS),
    ParameterKey("bot", "golden", "Cooldown", Unit.Kind.SECONDS),
    # Guardian Chips
    ParameterKey("guardian", "ally", "Damage", Unit.Kind.COUNT),
    ParameterKey("guardian", "ally", "Duration", Unit.Kind.SECONDS),
    ParameterKey("guardian", "ally", "Cooldown", Unit.Kind.SECONDS),
    ParameterKey("guardian", "core", "Damage", Unit.Kind.COUNT),
    ParameterKey("guardian", "core", "Duration", Unit.Kind.SECONDS),
    ParameterKey("guardian", "core", "Cooldown", Unit.Kind.SECONDS),
    ParameterKey("guardian", "fortress", "Damage", Unit.Kind.COUNT),
    ParameterKey("guardian", "fortress", "Duration", Unit.Kind.SECONDS),
    ParameterKey("guardian", "fortress", "Cooldown", Unit.Kind.SECONDS),
    ParameterKey("guardian", "recovery", "Damage", Unit.Kind.COUNT),
    ParameterKey("guardian", "recovery", "Duration", Unit.Kind.SECONDS),
    ParameterKey("guardian", "recovery", "Cooldown", Unit.Kind.SECONDS),
    ParameterKey("guardian", "overclock", "Damage", Unit.Kind.COUNT),
    ParameterKey("guardian", "overclock", "Duration", Unit.Kind.SECONDS),
    ParameterKey("guardian", "overclock", "Cooldown", Unit.Kind.SECONDS),
    # Ultimate Weapons
    ParameterKey("uw", "black_hole", "Damage", Unit.Kind.COUNT),
    ParameterKey("uw", "black_hole", "Proc Chance", Unit.Kind.PERCENT),
    ParameterKey("uw", "black_hole", "Cooldown", Unit.Kind.SECONDS),
    ParameterKey("uw", "golden_tower", "Damage", Unit.Kind.COUNT),
    ParameterKey("uw", "golden_tower", "Proc Chance", Unit.Kind.PERCENT),
    ParameterKey("uw", "golden_tower", "Cooldown", Unit.Kind.SECONDS),
    ParameterKey("uw", "laser_beam", "Damage", Unit.Kind.COUNT),
    ParameterKey("uw", "laser_beam", "Proc Chance", Unit.Kind.PERCENT),
    ParameterKey("uw", "laser_beam", "Cooldown", Unit.Kind.SECONDS),
    ParameterKey("uw", "orbital_strike", "Damage", Unit.Kind.COUNT),
    ParameterKey("uw", "orbital_strike", "Proc Chance", Unit.Kind.PERCENT),
    ParameterKey("uw", "orbital_strike", "Cooldown", Unit.Kind.SECONDS),
)

_INDEX: Mapping[tuple[str, str, str], ParameterKey] = _index_registry(PARAMETER_KEY_REGISTRY)


def get_parameter_key(system: str, entity_slug: str, parameter: str) -> ParameterKey | None:
    """Return a registry entry when the triple is allowed."""

    return _INDEX.get((system, entity_slug, parameter))


def allowed_parameters_for(system: str, entity_slug: str) -> dict[str, ParameterKey]:
    """Return a mapping of allowed parameter headers for an entity."""

    return {
        entry.parameter: entry
        for entry in PARAMETER_KEY_REGISTRY
        if entry.system == system and entry.entity_slug == entity_slug
    }

