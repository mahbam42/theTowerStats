"""Static modifier explanation registry for Base vs Effective value displays.

Phase 6 requires that dashboards can show:
- base value (from the raw parameter level table), and
- effective value (authoritative, never computed here),
along with optional explanatory strings describing *possible* modifier sources.

This module is intentionally:
- read-only (no database writes),
- non-computational (never performs modifier math),
- best-effort (partial coverage is acceptable and explicit).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Literal, Sequence

from definitions.models import CardDefinition
from player_state.models import Player, PlayerCard

SourceType = Literal["Card", "Lab", "Relic", "Other"]
EffectType = Literal["percent", "multiplier", "flat", "time"]


@dataclass(frozen=True, slots=True)
class ModifierExplanation:
    """An explanation string describing a possible modifier source.

    Args:
        parameter_key: Scoped parameter key, e.g. `ultimate_weapon.cooldown`.
        source_type: Source category (Card/Lab/Relic/Other).
        effect_type: Display kind (%, x, flat, time).
        description: Human-readable explanation string (no math).
    """

    parameter_key: str
    source_type: SourceType
    effect_type: EffectType
    description: str


Predicate = Callable[
    [Player, str, str, str, object, Sequence[PlayerCard]],
    Iterable[ModifierExplanation],
]


@dataclass(frozen=True, slots=True)
class ModifierExplanationTemplate:
    """Declarative template describing how to emit explanations for a parameter.

    Args:
        parameter_key: Scoped key (or `*` for wildcard).
        source_type: Source category.
        effect_type: Display kind (%, x, flat, time).
        description_template: Human-readable template (used when applicable).
        predicate: Callable that may emit 0..N explanations (must not do math).
    """

    parameter_key: str
    source_type: SourceType
    effect_type: EffectType
    description_template: str
    predicate: Predicate


def _infer_effect_type(effect_raw: str) -> EffectType:
    """Infer a display effect type from raw wiki card text."""

    cleaned = (effect_raw or "").strip()
    if cleaned.startswith("x") or "x" in cleaned:
        return "multiplier"
    if "%" in cleaned:
        return "percent"
    if "s" in cleaned.casefold():
        return "time"
    return "flat"


def _manual_effective_override(
    player: Player,
    parameter_key: str,
    base_value_raw: str,
    effective_value_raw: str,
    player_param: object,
    player_cards: Sequence[PlayerCard],
) -> Iterable[ModifierExplanation]:
    """Emit a generic explanation when an effective override is recorded."""

    _ = player, player_cards
    raw_override = (getattr(player_param, "effective_value_raw", "") or "").strip()
    if not raw_override:
        return ()
    if (base_value_raw or "").strip() == (effective_value_raw or "").strip():
        return ()
    return (
        ModifierExplanation(
            parameter_key=parameter_key,
            source_type="Other",
            effect_type="flat",
            description="Effective value is recorded separately and may reflect multiple modifiers.",
        ),
    )


def _manual_notes(
    player: Player,
    parameter_key: str,
    base_value_raw: str,
    effective_value_raw: str,
    player_param: object,
    player_cards: Sequence[PlayerCard],
) -> Iterable[ModifierExplanation]:
    """Emit user-supplied note lines as explanations (no interpretation)."""

    _ = player, base_value_raw, effective_value_raw, player_cards
    notes = (getattr(player_param, "effective_notes", "") or "").strip()
    if not notes:
        return ()
    out: list[ModifierExplanation] = []
    for line in [ln.strip() for ln in notes.splitlines()]:
        if not line:
            continue
        out.append(
            ModifierExplanation(
                parameter_key=parameter_key,
                source_type="Other",
                effect_type="flat",
                description=line,
            )
        )
    return tuple(out)


def _cooldown_cards(
    player: Player,
    parameter_key: str,
    base_value_raw: str,
    effective_value_raw: str,
    player_param: object,
    player_cards: Sequence[PlayerCard],
) -> Iterable[ModifierExplanation]:
    """Emit best-effort card-based explanations for cooldown-like parameters."""

    _ = base_value_raw, effective_value_raw, player_param
    if not player_cards:
        return ()
    out: list[ModifierExplanation] = []
    for pc in player_cards:
        if pc.player_id != player.id:
            continue
        if pc.stars_unlocked <= 0:
            continue
        card_def: CardDefinition | None = pc.card_definition
        if card_def is None:
            continue
        name = (card_def.name or "").strip()
        if "cooldown" not in name.casefold():
            continue
        effect_raw = (card_def.effect_raw or "").strip()
        effect_type = _infer_effect_type(effect_raw)
        effect_display = effect_raw if effect_raw else "Modifier"
        out.append(
            ModifierExplanation(
                parameter_key=parameter_key,
                source_type="Card",
                effect_type=effect_type,
                description=f"{effect_display} from {name} (Stars {pc.stars_unlocked}).",
            )
        )
    return tuple(out)


REGISTRY: tuple[ModifierExplanationTemplate, ...] = (
    ModifierExplanationTemplate(
        parameter_key="*",
        source_type="Other",
        effect_type="flat",
        description_template="Effective value is recorded separately and may reflect multiple modifiers.",
        predicate=_manual_effective_override,
    ),
    ModifierExplanationTemplate(
        parameter_key="*",
        source_type="Other",
        effect_type="flat",
        description_template="{note}",
        predicate=_manual_notes,
    ),
    ModifierExplanationTemplate(
        parameter_key="ultimate_weapon.cooldown",
        source_type="Card",
        effect_type="percent",
        description_template="{effect_raw} from {card_name}.",
        predicate=_cooldown_cards,
    ),
    ModifierExplanationTemplate(
        parameter_key="guardian_chip.cooldown",
        source_type="Card",
        effect_type="percent",
        description_template="{effect_raw} from {card_name}.",
        predicate=_cooldown_cards,
    ),
    ModifierExplanationTemplate(
        parameter_key="bot.cooldown",
        source_type="Card",
        effect_type="percent",
        description_template="{effect_raw} from {card_name}.",
        predicate=_cooldown_cards,
    ),
)


def collect_modifier_explanations(
    *,
    player: Player,
    parameter_key: str,
    base_value_raw: str,
    effective_value_raw: str,
    player_param: object,
    player_cards: Sequence[PlayerCard] = (),
) -> tuple[ModifierExplanation, ...]:
    """Collect modifier explanations for a parameter from the static registry.

    Args:
        player: Player owning the parameter.
        parameter_key: Scoped key like `ultimate_weapon.cooldown`.
        base_value_raw: Base value derived from the raw level table.
        effective_value_raw: Effective value treated as authoritative.
        player_param: Player parameter object (used only for read-only inspection).
        player_cards: Optional pre-fetched player cards for explanation detection.

    Returns:
        Tuple of ModifierExplanation entries (possibly empty).
    """

    explanations: list[ModifierExplanation] = []
    for template in REGISTRY:
        if template.parameter_key != "*" and template.parameter_key != parameter_key:
            continue
        explanations.extend(
            list(
                template.predicate(
                    player,
                    parameter_key,
                    base_value_raw,
                    effective_value_raw,
                    player_param,
                    player_cards,
                )
            )
        )
    # De-dupe while preserving order.
    seen: set[str] = set()
    unique: list[ModifierExplanation] = []
    for entry in explanations:
        key = f"{entry.source_type}:{entry.effect_type}:{entry.description}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(entry)
    return tuple(unique)

