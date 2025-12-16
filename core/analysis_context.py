"""Build Analysis Engine context DTOs from Django models.

This module lives in `core` (Django side) and is responsible for:
- selecting definition tables explicitly (by policy),
- resolving player context (cards/UWs/guardian chips/bots),
- converting ORM rows into pure analysis DTOs.

The Analysis Engine itself must not import Django.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from analysis.context import (
    ParameterInput,
    PlayerBotInput,
    PlayerCardInput,
    PlayerContextInput,
    PlayerGuardianChipInput,
    PlayerUltimateWeaponInput,
)
from analysis.quantity import UnitType, parse_quantity
from definitions.models import (
    Unit,
    WikiData,
)
from player_state.models import (
    Player,
    PlayerBot,
    PlayerBotParameter,
    PlayerCard,
    PlayerGuardianChip,
    PlayerGuardianChipParameter,
    PlayerUltimateWeapon,
    PlayerUltimateWeaponParameter,
)


@dataclass(frozen=True, slots=True)
class RevisionPolicy:
    """Policy controlling which definition revision is selected.

    The layered architecture rebuilds definition tables from wiki sources. In
    this phase, parameter-level rows are recreated on rebuild, so revision
    selection is intentionally minimal:

    - mode="latest": select the latest WikiData row per row-level entity id.
    - mode="as_of": select the latest WikiData row with `last_seen <= as_of`.
    """

    mode: str = "latest"
    as_of: datetime | None = None


_PARSE_VERSION_BOTS = "bots_v1"
_PARSE_VERSION_GUARDIAN_CHIPS = "guardian_chips_v1"
_PARSE_VERSION_ULTIMATE_WEAPONS = "ultimate_weapons_v1"


def build_player_context(*, revision_policy: RevisionPolicy | None = None) -> PlayerContextInput:
    """Build PlayerContextInput from persisted player state and parameters.

    Args:
        revision_policy: Optional policy controlling definition selection.

    Returns:
        PlayerContextInput suitable for passing into analysis.
    """

    policy = revision_policy or RevisionPolicy()
    player = Player.objects.filter(name="default").first()
    if player is None:
        return PlayerContextInput()

    return PlayerContextInput(
        cards=tuple(_build_cards(player)),
        ultimate_weapons=tuple(_build_ultimate_weapons(player, policy=policy)),
        guardian_chips=tuple(_build_guardian_chips(player, policy=policy)),
        bots=tuple(_build_bots(player, policy=policy)),
    )


def _unit_type_for_kind(unit_kind: str) -> UnitType:
    """Map a Unit.Kind value to an analysis UnitType."""

    if unit_kind == Unit.Kind.SECONDS:
        return UnitType.time
    if unit_kind == Unit.Kind.PERCENT:
        return UnitType.multiplier
    if unit_kind == Unit.Kind.MULTIPLIER:
        return UnitType.multiplier
    return UnitType.count


def _as_parameter_input(*, key: str, raw_value: str, unit_kind: str, wiki_revision_id: int | None) -> ParameterInput:
    """Convert a raw key/value string into a ParameterInput DTO."""

    parsed = parse_quantity(raw_value, unit_type=_unit_type_for_kind(unit_kind))
    return ParameterInput(
        key=key,
        raw_value=raw_value,
        parsed=parsed,
        wiki_revision_id=wiki_revision_id,
    )


def _build_cards(player: Player) -> list[PlayerCardInput]:
    """Build card context entries (stars only)."""

    cards: list[PlayerCardInput] = []
    for card in PlayerCard.objects.filter(player=player).select_related("card_definition").order_by("card_slug"):
        owned = card.stars_unlocked > 0
        name = card.card_definition.name if card.card_definition is not None else card.card_slug
        cards.append(
            PlayerCardInput(
                name=name,
                owned=owned,
                level=None,
                star=None,
                parameters=(),
                level_parameters=(),
            )
        )
    return cards


def _build_ultimate_weapons(player: Player, *, policy: RevisionPolicy) -> list[PlayerUltimateWeaponInput]:
    """Build ultimate weapon context entries from per-parameter levels."""

    uws: list[PlayerUltimateWeaponInput] = []
    for uw in (
        PlayerUltimateWeapon.objects.filter(player=player)
        .select_related("ultimate_weapon_definition")
        .order_by("ultimate_weapon_slug")
    ):
        params = _uw_parameters(uw, policy=policy)
        name = uw.ultimate_weapon_definition.name if uw.ultimate_weapon_definition is not None else uw.ultimate_weapon_slug
        uws.append(
            PlayerUltimateWeaponInput(
                name=name,
                unlocked=uw.unlocked,
                level=None,
                star=None,
                parameters=params,
            )
        )
    return uws


def _uw_parameters(uw: PlayerUltimateWeapon, *, policy: RevisionPolicy) -> tuple[ParameterInput, ...]:
    """Select revision-aware wiki parameter values for an ultimate weapon."""

    if uw.ultimate_weapon_definition_id is None:
        return ()
    used: list[ParameterInput] = []
    for player_param in (
        PlayerUltimateWeaponParameter.objects.filter(player_ultimate_weapon=uw)
        .select_related("parameter_definition")
        .order_by("parameter_definition__key", "id")
    ):
        if not uw.unlocked or not player_param.level or player_param.parameter_definition_id is None:
            continue
        value_raw, revision_id = _select_level_value(
            base_entity_id=uw.ultimate_weapon_slug,
            level=player_param.level,
            parse_version=_PARSE_VERSION_ULTIMATE_WEAPONS,
            value_header=player_param.parameter_definition.display_name,
            policy=policy,
        )
        if value_raw is None:
            continue
        used.append(
            _as_parameter_input(
                key=str(player_param.parameter_definition.key),
                raw_value=value_raw,
                unit_kind=str(player_param.parameter_definition.unit_kind),
                wiki_revision_id=revision_id,
            )
        )
    return tuple(used)


def _build_guardian_chips(player: Player, *, policy: RevisionPolicy) -> list[PlayerGuardianChipInput]:
    """Build guardian chip context entries from per-parameter levels."""

    chips: list[PlayerGuardianChipInput] = []
    for chip in (
        PlayerGuardianChip.objects.filter(player=player)
        .select_related("guardian_chip_definition")
        .order_by("guardian_chip_slug")
    ):
        params = _guardian_parameters(chip, policy=policy)
        name = (
            chip.guardian_chip_definition.name
            if chip.guardian_chip_definition is not None
            else chip.guardian_chip_slug
        )
        chips.append(
            PlayerGuardianChipInput(
                name=name,
                owned=chip.unlocked,
                level=None,
                star=None,
                parameters=params,
            )
        )
    return chips


def _guardian_parameters(chip: PlayerGuardianChip, *, policy: RevisionPolicy) -> tuple[ParameterInput, ...]:
    """Select revision-aware wiki parameter values for a guardian chip."""

    if chip.guardian_chip_definition_id is None:
        return ()
    used: list[ParameterInput] = []
    for player_param in (
        PlayerGuardianChipParameter.objects.filter(player_guardian_chip=chip)
        .select_related("parameter_definition")
        .order_by("parameter_definition__key", "id")
    ):
        if not chip.unlocked or not player_param.level or player_param.parameter_definition_id is None:
            continue
        value_raw, revision_id = _select_level_value(
            base_entity_id=chip.guardian_chip_slug,
            level=player_param.level,
            parse_version=_PARSE_VERSION_GUARDIAN_CHIPS,
            value_header=player_param.parameter_definition.display_name,
            policy=policy,
        )
        if value_raw is None:
            continue
        used.append(
            _as_parameter_input(
                key=str(player_param.parameter_definition.key),
                raw_value=value_raw,
                unit_kind=str(player_param.parameter_definition.unit_kind),
                wiki_revision_id=revision_id,
            )
        )
    return tuple(used)


def _build_bots(player: Player, *, policy: RevisionPolicy) -> list[PlayerBotInput]:
    """Build bot context entries from per-parameter levels."""

    bots: list[PlayerBotInput] = []
    for bot in (
        PlayerBot.objects.filter(player=player)
        .select_related("bot_definition")
        .order_by("bot_slug")
    ):
        params = _bot_parameters(bot, policy=policy)
        name = bot.bot_definition.name if bot.bot_definition is not None else bot.bot_slug
        bots.append(
            PlayerBotInput(
                name=name,
                unlocked=bot.unlocked,
                level=None,
                parameters=params,
            )
        )
    return bots


def _bot_parameters(bot: PlayerBot, *, policy: RevisionPolicy) -> tuple[ParameterInput, ...]:
    """Select revision-aware wiki parameter values for a bot."""

    if bot.bot_definition_id is None:
        return ()
    used: list[ParameterInput] = []
    for player_param in (
        PlayerBotParameter.objects.filter(player_bot=bot)
        .select_related("parameter_definition")
        .order_by("parameter_definition__key", "id")
    ):
        if not bot.unlocked or not player_param.level or player_param.parameter_definition_id is None:
            continue
        value_raw, revision_id = _select_level_value(
            base_entity_id=bot.bot_slug,
            level=player_param.level,
            parse_version=_PARSE_VERSION_BOTS,
            value_header=player_param.parameter_definition.display_name,
            policy=policy,
        )
        if value_raw is None:
            continue
        used.append(
            _as_parameter_input(
                key=str(player_param.parameter_definition.key),
                raw_value=value_raw,
                unit_kind=str(player_param.parameter_definition.unit_kind),
                wiki_revision_id=revision_id,
            )
        )
    return tuple(used)


def _select_level_value(
    *,
    base_entity_id: str,
    level: int,
    parse_version: str,
    value_header: str,
    policy: RevisionPolicy,
) -> tuple[str | None, int | None]:
    """Select a wiki-derived value for a leveled row under a revision policy.

    Args:
        base_entity_id: Stable entity id used in `_wiki_entity_id` (typically the definition slug).
        level: Player-selected level (1-based).
        parse_version: WikiData parse_version for this entity category.
        value_header: Column header to extract from WikiData.raw_row.
        policy: RevisionPolicy controlling which WikiData revision to select.

    Returns:
        Tuple of (value_raw, wiki_revision_id). Returns (None, None) when the
        appropriate row cannot be found or the value is missing.
    """

    composite_id = f"{base_entity_id}__level_{level}__star_none"
    row = _select_wikidata_row(entity_id=composite_id, parse_version=parse_version, policy=policy)
    if row is None:
        return None, None
    raw = str(row.raw_row.get(value_header, "")).strip()
    if not raw:
        return None, row.id
    return raw, row.id


def _select_wikidata_row(*, entity_id: str, parse_version: str, policy: RevisionPolicy) -> WikiData | None:
    """Select a WikiData row according to a RevisionPolicy."""

    qs = WikiData.objects.filter(parse_version=parse_version, entity_id=entity_id)
    if policy.mode == "as_of":
        as_of = policy.as_of
        if as_of is None:
            return None
        qs = qs.filter(last_seen__lte=as_of)
    return qs.order_by("-last_seen", "-id").first()
