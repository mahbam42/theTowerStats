"""DTOs for passing player context and parameter tables into analysis.

The Analysis Engine must remain pure: no Django imports, no database access, and
no side effects. The core app is responsible for building these DTOs from ORM
models.
"""

from __future__ import annotations

from dataclasses import dataclass

from .quantity import Quantity


@dataclass(frozen=True, slots=True)
class ParameterInput:
    """A single parameter value selected for analysis.

    Args:
        key: Stable parameter key (caller-defined).
        raw_value: Raw string as captured from wiki or user input.
        parsed: Best-effort parsed quantity containing normalized value.
        wiki_revision_id: Optional `core.WikiData` primary key representing the
            immutable revision of the source table row used for this parameter.
    """

    key: str
    raw_value: str
    parsed: Quantity
    wiki_revision_id: int | None


@dataclass(frozen=True, slots=True)
class PlayerCardInput:
    """Player card context for analysis computations."""

    name: str
    owned: bool
    level: int | None
    star: int | None
    parameters: tuple[ParameterInput, ...] = ()
    level_parameters: tuple[ParameterInput, ...] = ()


@dataclass(frozen=True, slots=True)
class PlayerUltimateWeaponInput:
    """Player ultimate weapon context for analysis computations."""

    name: str
    unlocked: bool
    level: int | None
    star: int | None
    parameters: tuple[ParameterInput, ...] = ()


@dataclass(frozen=True, slots=True)
class PlayerGuardianChipInput:
    """Player guardian chip context for analysis computations."""

    name: str
    owned: bool
    level: int | None
    star: int | None
    parameters: tuple[ParameterInput, ...] = ()


@dataclass(frozen=True, slots=True)
class PlayerBotInput:
    """Player bot context for analysis computations."""

    name: str
    unlocked: bool
    level: int | None
    parameters: tuple[ParameterInput, ...] = ()


@dataclass(frozen=True, slots=True)
class PlayerContextInput:
    """Container for all player context provided to analysis.

    The Analysis Engine must handle missing context gracefully. Callers may pass
    `None` instead of a PlayerContextInput when no player state is available.
    """

    cards: tuple[PlayerCardInput, ...] = ()
    ultimate_weapons: tuple[PlayerUltimateWeaponInput, ...] = ()
    guardian_chips: tuple[PlayerGuardianChipInput, ...] = ()
    bots: tuple[PlayerBotInput, ...] = ()

