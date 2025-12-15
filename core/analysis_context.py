"""Build Analysis Engine context DTOs from Django models.

This module lives in `core` (Django side) and is responsible for:
- selecting definition tables explicitly (by policy),
- resolving player context (cards/UWs/guardian chips/bots),
- converting ORM rows into pure analysis DTOs.

The Analysis Engine itself must not import Django.
"""

from __future__ import annotations

from dataclasses import dataclass

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
    BotParameterLevel,
    GuardianChipParameterLevel,
    UltimateWeaponParameterLevel,
    Unit,
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

    - mode="latest": use whatever is currently present in definitions tables.
    - overrides: reserved for future explicit revision pinning.
    """

    mode: str = "latest"
    overrides: dict[tuple[str, str], int] | None = None


def build_player_context(*, revision_policy: RevisionPolicy | None = None) -> PlayerContextInput:
    """Build PlayerContextInput from persisted player state and parameters.

    Args:
        revision_policy: Optional policy controlling definition selection.

    Returns:
        PlayerContextInput suitable for passing into analysis.
    """

    _ = revision_policy or RevisionPolicy()
    player = Player.objects.filter(name="default").first()
    if player is None:
        return PlayerContextInput()

    return PlayerContextInput(
        cards=tuple(_build_cards(player)),
        ultimate_weapons=tuple(_build_ultimate_weapons(player)),
        guardian_chips=tuple(_build_guardian_chips(player)),
        bots=tuple(_build_bots(player)),
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


def _build_ultimate_weapons(player: Player) -> list[PlayerUltimateWeaponInput]:
    """Build ultimate weapon context entries from per-parameter levels."""

    uws: list[PlayerUltimateWeaponInput] = []
    for uw in (
        PlayerUltimateWeapon.objects.filter(player=player)
        .select_related("ultimate_weapon_definition")
        .order_by("ultimate_weapon_slug")
    ):
        params = _uw_parameters(uw)
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


def _uw_parameters(uw: PlayerUltimateWeapon) -> tuple[ParameterInput, ...]:
    """Select parameter-level rows for an ultimate weapon."""

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
        level_row = UltimateWeaponParameterLevel.objects.filter(
            parameter_definition=player_param.parameter_definition,
            level=player_param.level,
        ).first()
        if level_row is None:
            continue
        used.append(
            _as_parameter_input(
                key=str(player_param.parameter_definition.key),
                raw_value=level_row.value_raw,
                unit_kind=str(player_param.parameter_definition.unit_kind),
                wiki_revision_id=level_row.source_wikidata_id,
            )
        )
    return tuple(used)


def _build_guardian_chips(player: Player) -> list[PlayerGuardianChipInput]:
    """Build guardian chip context entries from per-parameter levels."""

    chips: list[PlayerGuardianChipInput] = []
    for chip in (
        PlayerGuardianChip.objects.filter(player=player)
        .select_related("guardian_chip_definition")
        .order_by("guardian_chip_slug")
    ):
        params = _guardian_parameters(chip)
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


def _guardian_parameters(chip: PlayerGuardianChip) -> tuple[ParameterInput, ...]:
    """Select parameter-level rows for a guardian chip."""

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
        level_row = GuardianChipParameterLevel.objects.filter(
            parameter_definition=player_param.parameter_definition,
            level=player_param.level,
        ).first()
        if level_row is None:
            continue
        used.append(
            _as_parameter_input(
                key=str(player_param.parameter_definition.key),
                raw_value=level_row.value_raw,
                unit_kind=str(player_param.parameter_definition.unit_kind),
                wiki_revision_id=level_row.source_wikidata_id,
            )
        )
    return tuple(used)


def _build_bots(player: Player) -> list[PlayerBotInput]:
    """Build bot context entries from per-parameter levels."""

    bots: list[PlayerBotInput] = []
    for bot in (
        PlayerBot.objects.filter(player=player)
        .select_related("bot_definition")
        .order_by("bot_slug")
    ):
        params = _bot_parameters(bot)
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


def _bot_parameters(bot: PlayerBot) -> tuple[ParameterInput, ...]:
    """Select parameter-level rows for a bot."""

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
        level_row = BotParameterLevel.objects.filter(
            parameter_definition=player_param.parameter_definition,
            level=player_param.level,
        ).first()
        if level_row is None:
            continue
        used.append(
            _as_parameter_input(
                key=str(player_param.parameter_definition.key),
                raw_value=level_row.value_raw,
                unit_kind=str(player_param.parameter_definition.unit_kind),
                wiki_revision_id=level_row.source_wikidata_id,
            )
        )
    return tuple(used)

