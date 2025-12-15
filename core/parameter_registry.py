"""Registry of allowed parameter keys for wiki ingestion.

The registry enforces a closed set of parameter names per entity to prevent
metadata or unknown headers from being treated as numeric parameters. Each
entry captures the owning system, a stable entity slug, the parameter key as it
appears in wiki tables, and the expected :class:`core.models.Unit.Kind`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Tuple, cast

from core.models import Unit

_COUNT = cast(Unit.Kind, Unit.Kind.COUNT)
_PERCENT = cast(Unit.Kind, Unit.Kind.PERCENT)
_SECONDS = cast(Unit.Kind, Unit.Kind.SECONDS)


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
    ParameterKey("bot", "amplify", "Damage", _COUNT),
    ParameterKey("bot", "amplify", "Duration", _SECONDS),
    ParameterKey("bot", "amplify", "Cooldown", _SECONDS),
    ParameterKey("bot", "flame", "Damage", _COUNT),
    ParameterKey("bot", "flame", "Duration", _SECONDS),
    ParameterKey("bot", "flame", "Cooldown", _SECONDS),
    ParameterKey("bot", "thunder", "Damage", _COUNT),
    ParameterKey("bot", "thunder", "Duration", _SECONDS),
    ParameterKey("bot", "thunder", "Cooldown", _SECONDS),
    ParameterKey("bot", "golden", "Damage", _COUNT),
    ParameterKey("bot", "golden", "Duration", _SECONDS),
    ParameterKey("bot", "golden", "Cooldown", _SECONDS),
    # Guardian Chips
    ParameterKey("guardian", "ally", "Damage", _COUNT),
    ParameterKey("guardian", "ally", "Duration", _SECONDS),
    ParameterKey("guardian", "ally", "Cooldown", _SECONDS),
    ParameterKey("guardian", "core", "Damage", _COUNT),
    ParameterKey("guardian", "core", "Duration", _SECONDS),
    ParameterKey("guardian", "core", "Cooldown", _SECONDS),
    ParameterKey("guardian", "fortress", "Damage", _COUNT),
    ParameterKey("guardian", "fortress", "Duration", _SECONDS),
    ParameterKey("guardian", "fortress", "Cooldown", _SECONDS),
    ParameterKey("guardian", "recovery", "Damage", _COUNT),
    ParameterKey("guardian", "recovery", "Duration", _SECONDS),
    ParameterKey("guardian", "recovery", "Cooldown", _SECONDS),
    ParameterKey("guardian", "overclock", "Damage", _COUNT),
    ParameterKey("guardian", "overclock", "Duration", _SECONDS),
    ParameterKey("guardian", "overclock", "Cooldown", _SECONDS),
    # Ultimate Weapons
    ParameterKey("uw", "black_hole", "Damage", _COUNT),
    ParameterKey("uw", "black_hole", "Proc Chance", _PERCENT),
    ParameterKey("uw", "black_hole", "Cooldown", _SECONDS),
    ParameterKey("uw", "golden_tower", "Damage", _COUNT),
    ParameterKey("uw", "golden_tower", "Proc Chance", _PERCENT),
    ParameterKey("uw", "golden_tower", "Cooldown", _SECONDS),
    ParameterKey("uw", "laser_beam", "Damage", _COUNT),
    ParameterKey("uw", "laser_beam", "Proc Chance", _PERCENT),
    ParameterKey("uw", "laser_beam", "Cooldown", _SECONDS),
    ParameterKey("uw", "orbital_strike", "Damage", _COUNT),
    ParameterKey("uw", "orbital_strike", "Proc Chance", _PERCENT),
    ParameterKey("uw", "orbital_strike", "Cooldown", _SECONDS),
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
