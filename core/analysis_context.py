"""Build Analysis Engine context DTOs from Django models.

This module lives in `core` (Django side) and is responsible for:
- selecting parameter revisions explicitly (by policy),
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

from core.models import (
    BotParameter,
    CardLevel,
    CardParameter,
    GuardianChipParameter,
    PlayerBot,
    PlayerCard,
    PlayerGuardianChip,
    PlayerUltimateWeapon,
    UltimateWeaponParameter,
)


@dataclass(frozen=True, slots=True)
class RevisionPolicy:
    """Policy controlling which parameter revision is selected.

    Args:
        mode: Either "latest" or "manual".
            - latest: choose the most recently seen wiki revision (by `last_seen`, then id).
            - manual: treat non-wiki (NULL revision) rows as the selected revision.
        overrides: Optional explicit per-entity wiki revision overrides.
            Keys are (entity_type, entity_name).
    """

    mode: str = "latest"
    overrides: dict[tuple[str, str], int] | None = None


def build_player_context(*, revision_policy: RevisionPolicy | None = None) -> PlayerContextInput:
    """Build PlayerContextInput from persisted player state and parameters.

    Args:
        revision_policy: Policy for selecting wiki revisions. Defaults to "latest".

    Returns:
        PlayerContextInput suitable for passing into analysis.
    """

    policy = revision_policy or RevisionPolicy()

    cards = tuple(_build_cards(policy))
    ultimate_weapons = tuple(_build_ultimate_weapons(policy))
    guardian_chips = tuple(_build_guardian_chips(policy))
    bots = tuple(_build_bots(policy))

    return PlayerContextInput(
        cards=cards,
        ultimate_weapons=ultimate_weapons,
        guardian_chips=guardian_chips,
        bots=bots,
    )


def _infer_unit_type(key: str) -> UnitType:
    """Infer a UnitType for parsing a parameter key.

    This is intentionally conservative; unknown keys fall back to `count`.
    """

    lowered = key.casefold()
    if "cooldown" in lowered or lowered.endswith("_seconds") or lowered.endswith("_sec"):
        return UnitType.time
    if "chance" in lowered or "percent" in lowered or lowered.endswith("_pct"):
        return UnitType.multiplier
    if "multiplier" in lowered or lowered.endswith("_mult"):
        return UnitType.multiplier
    return UnitType.count


def _as_parameter_input(model_key: str, raw_value: str, *, wiki_revision_id: int | None) -> ParameterInput:
    """Convert a raw key/value string into a ParameterInput DTO."""

    parsed = parse_quantity(raw_value, unit_type=_infer_unit_type(model_key))
    return ParameterInput(
        key=model_key,
        raw_value=raw_value,
        parsed=parsed,
        wiki_revision_id=wiki_revision_id,
    )


def _latest_wiki_revision_id_for_queryset(qs) -> int | None:
    """Return the latest source_wikidata id for a parameter queryset."""

    return (
        qs.filter(source_wikidata__isnull=False)
        .order_by("-source_wikidata__last_seen", "-source_wikidata__id")
        .values_list("source_wikidata_id", flat=True)
        .first()
    )


def _select_parameters_for_card(card: PlayerCard, policy: RevisionPolicy) -> tuple[ParameterInput, ...]:
    """Select CardParameter rows for a player card using an explicit revision policy."""

    qs = CardParameter.objects.filter(card_definition=card.card_definition)
    override_key = ("card", card.card_definition.name)
    override = (policy.overrides or {}).get(override_key)
    revision_id: int | None
    if override is not None:
        revision_id = override
    elif policy.mode == "manual":
        revision_id = None
    else:
        revision_id = _latest_wiki_revision_id_for_queryset(qs)

    if revision_id is None:
        selected = qs.filter(source_wikidata__isnull=True).order_by("key", "id")
    else:
        selected = qs.filter(source_wikidata_id=revision_id).order_by("key", "id")

    return tuple(
        _as_parameter_input(row.key, row.raw_value, wiki_revision_id=row.source_wikidata_id)
        for row in selected
    )


def _select_level_parameters_for_card(card: PlayerCard, policy: RevisionPolicy) -> tuple[ParameterInput, ...]:
    """Select a CardLevel row for the player's level/star and return it as parameters."""

    if card.level is None:
        return ()
    qs = CardLevel.objects.filter(card_definition=card.card_definition, level=card.level)
    if card.star is not None:
        qs = qs.filter(star=card.star)
    else:
        qs = qs.filter(star__isnull=True)

    if policy.mode == "manual":
        qs = qs.filter(source_wikidata__isnull=True)
    else:
        qs = qs.order_by("-source_wikidata__last_seen", "-source_wikidata__id")

    row = qs.first()
    if row is None:
        return ()

    wiki_revision_id = row.source_wikidata_id
    return tuple(
        _as_parameter_input(str(key), str(value), wiki_revision_id=wiki_revision_id)
        for key, value in (row.raw_row or {}).items()
    )


def _build_cards(policy: RevisionPolicy):
    """Yield PlayerCardInput entries."""

    for card in PlayerCard.objects.select_related("card_definition").order_by(
        "card_definition__name"
    ):
        yield PlayerCardInput(
            name=card.card_definition.name,
            owned=card.owned,
            level=card.level,
            star=card.star,
            parameters=_select_parameters_for_card(card, policy),
            level_parameters=_select_level_parameters_for_card(card, policy),
        )


def _select_parameters_for_uw(uw: PlayerUltimateWeapon, policy: RevisionPolicy) -> tuple[ParameterInput, ...]:
    """Select UltimateWeaponParameter rows using an explicit revision policy."""

    qs = UltimateWeaponParameter.objects.filter(weapon_name=uw.weapon_name)
    override_key = ("ultimate_weapon", uw.weapon_name)
    override = (policy.overrides or {}).get(override_key)
    revision_id: int | None
    if override is not None:
        revision_id = override
    elif policy.mode == "manual":
        revision_id = None
    else:
        revision_id = _latest_wiki_revision_id_for_queryset(qs)

    if revision_id is None:
        selected = qs.filter(source_wikidata__isnull=True).order_by("key", "id")
    else:
        selected = qs.filter(source_wikidata_id=revision_id).order_by("key", "id")

    return tuple(
        _as_parameter_input(row.key, row.raw_value, wiki_revision_id=row.source_wikidata_id)
        for row in selected
    )


def _build_ultimate_weapons(policy: RevisionPolicy):
    """Yield PlayerUltimateWeaponInput entries."""

    for uw in PlayerUltimateWeapon.objects.order_by("weapon_name"):
        yield PlayerUltimateWeaponInput(
            name=uw.weapon_name,
            unlocked=uw.unlocked,
            level=uw.level,
            star=uw.star,
            parameters=_select_parameters_for_uw(uw, policy),
        )


def _select_parameters_for_guardian(
    chip: PlayerGuardianChip, policy: RevisionPolicy
) -> tuple[ParameterInput, ...]:
    """Select GuardianChipParameter rows using an explicit revision policy."""

    qs = GuardianChipParameter.objects.filter(chip_name=chip.chip_name)
    override_key = ("guardian_chip", chip.chip_name)
    override = (policy.overrides or {}).get(override_key)
    revision_id: int | None
    if override is not None:
        revision_id = override
    elif policy.mode == "manual":
        revision_id = None
    else:
        revision_id = _latest_wiki_revision_id_for_queryset(qs)

    if revision_id is None:
        selected = qs.filter(source_wikidata__isnull=True).order_by("key", "id")
    else:
        selected = qs.filter(source_wikidata_id=revision_id).order_by("key", "id")

    return tuple(
        _as_parameter_input(row.key, row.raw_value, wiki_revision_id=row.source_wikidata_id)
        for row in selected
    )


def _build_guardian_chips(policy: RevisionPolicy):
    """Yield PlayerGuardianChipInput entries."""

    for chip in PlayerGuardianChip.objects.order_by("chip_name"):
        yield PlayerGuardianChipInput(
            name=chip.chip_name,
            owned=chip.owned,
            level=chip.level,
            star=chip.star,
            parameters=_select_parameters_for_guardian(chip, policy),
        )


def _select_parameters_for_bot(bot: PlayerBot, policy: RevisionPolicy) -> tuple[ParameterInput, ...]:
    """Select BotParameter rows using an explicit revision policy."""

    qs = BotParameter.objects.filter(bot_name=bot.bot_name)
    override_key = ("bot", bot.bot_name)
    override = (policy.overrides or {}).get(override_key)
    revision_id: int | None
    if override is not None:
        revision_id = override
    elif policy.mode == "manual":
        revision_id = None
    else:
        revision_id = _latest_wiki_revision_id_for_queryset(qs)

    if revision_id is None:
        selected = qs.filter(source_wikidata__isnull=True).order_by("key", "id")
    else:
        selected = qs.filter(source_wikidata_id=revision_id).order_by("key", "id")

    return tuple(
        _as_parameter_input(row.key, row.raw_value, wiki_revision_id=row.source_wikidata_id)
        for row in selected
    )


def _build_bots(policy: RevisionPolicy):
    """Yield PlayerBotInput entries."""

    for bot in PlayerBot.objects.order_by("bot_name"):
        yield PlayerBotInput(
            name=bot.bot_name,
            unlocked=bot.unlocked,
            level=bot.level,
            parameters=_select_parameters_for_bot(bot, policy),
        )
