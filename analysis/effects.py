"""Parameterized effects for wiki-derived entities.

Effects are deterministic computations that transform a selected entity's raw
wiki parameters into derived numeric metrics. Effects must remain pure and
defensive: missing inputs should yield partial outputs (None values) rather
than exceptions.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .context import ParameterInput
from .dto import UsedParameter


@dataclass(frozen=True, slots=True)
class EffectResult:
    """Result container for an effect computation.

    Args:
        value: Derived numeric value for the effect, or None when inputs are
            missing/invalid.
        used_parameters: Parameters referenced during evaluation (for UI
            transparency).
    """

    value: float | None
    used_parameters: tuple[UsedParameter, ...]


def uptime_percent_from_parameters(
    *,
    entity_type: str,
    entity_name: str,
    parameters: tuple[ParameterInput, ...],
    duration_key: str = "duration",
    cooldown_key: str = "cooldown",
) -> EffectResult:
    """Compute uptime percent from duration and cooldown parameters.

    Formula:
        uptime_percent = 100 * clamp(duration_seconds / cooldown_seconds, 0..1)

    Args:
        entity_type: Entity category label (e.g. "ultimate_weapon", "bot").
        entity_name: Human-readable entity name for trace output.
        parameters: ParameterInput entries (raw + parsed values).
        duration_key: Parameter key used for duration seconds.
        cooldown_key: Parameter key used for cooldown seconds.

    Returns:
        EffectResult with uptime percent and referenced parameters.
    """

    duration: float | None = None
    cooldown: float | None = None
    used: list[UsedParameter] = []

    for param in parameters:
        if param.key == duration_key:
            duration = _float_or_none(param.parsed.normalized_value)
            used.append(_used(entity_type=entity_type, entity_name=entity_name, param=param))
        elif param.key == cooldown_key:
            cooldown = _float_or_none(param.parsed.normalized_value)
            used.append(_used(entity_type=entity_type, entity_name=entity_name, param=param))

    value = _uptime_percent(duration_seconds=duration, cooldown_seconds=cooldown)
    return EffectResult(value=value, used_parameters=tuple(used))


def activations_per_minute_from_parameters(
    *,
    entity_type: str,
    entity_name: str,
    parameters: tuple[ParameterInput, ...],
    cooldown_key: str = "cooldown",
) -> EffectResult:
    """Compute activations/minute from a cooldown parameter.

    Formula:
        activations_per_minute = 60 / cooldown_seconds

    Args:
        entity_type: Entity category label (e.g. "guardian_chip").
        entity_name: Human-readable entity name for trace output.
        parameters: ParameterInput entries (raw + parsed values).
        cooldown_key: Parameter key used for cooldown seconds.

    Returns:
        EffectResult with activations/minute and referenced parameters.
    """

    cooldown: float | None = None
    used: list[UsedParameter] = []
    for param in parameters:
        if param.key != cooldown_key:
            continue
        cooldown = _float_or_none(param.parsed.normalized_value)
        used.append(_used(entity_type=entity_type, entity_name=entity_name, param=param))
        break

    if cooldown is None or cooldown <= 0:
        return EffectResult(value=None, used_parameters=tuple(used))
    return EffectResult(value=60.0 / cooldown, used_parameters=tuple(used))


def _uptime_percent(*, duration_seconds: float | None, cooldown_seconds: float | None) -> float | None:
    """Return uptime percent for (duration, cooldown) inputs."""

    if duration_seconds is None or cooldown_seconds is None:
        return None
    if duration_seconds < 0 or cooldown_seconds <= 0:
        return None
    fraction = duration_seconds / cooldown_seconds
    if fraction < 0:
        fraction = 0.0
    if fraction > 1.0:
        fraction = 1.0
    return 100.0 * fraction


def _float_or_none(value: Decimal | None) -> float | None:
    """Convert a Decimal to float, returning None when missing."""

    if value is None:
        return None
    return float(value)


def _used(*, entity_type: str, entity_name: str, param: ParameterInput) -> UsedParameter:
    """Build a UsedParameter record for a parameter input."""

    return UsedParameter(
        entity_type=entity_type,
        entity_name=entity_name,
        key=param.key,
        raw_value=param.raw_value,
        normalized_value=_float_or_none(param.parsed.normalized_value),
        wiki_revision_id=param.wiki_revision_id,
    )
