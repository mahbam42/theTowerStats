"""Translate versioned WikiData revisions into structured Phase 3 models.

This module intentionally performs a *lossless* mapping:
- raw strings from `core.models.WikiData.raw_row` are copied as-is (no math),
- every created structured row records the exact `source_wikidata` revision used.

The primary entry points are used by the `populate_cards_from_wiki` management
command and are safe to run repeatedly (idempotent for a given wiki revision).
"""

from __future__ import annotations

from dataclasses import dataclass

from django.db import transaction

from core.models import (
    BotDefinition,
    BotLevel,
    BotParameter,
    CardDefinition,
    CardLevel,
    CardParameter,
    CardSlot,
    GuardianChipDefinition,
    GuardianChipLevel,
    GuardianChipParameter,
    UltimateWeaponDefinition,
    UltimateWeaponLevel,
    UltimateWeaponParameter,
    Unit,
    WikiData,
)
from core.parameter_registry import allowed_parameters_for
from core.wiki_ingestion import make_entity_id


@dataclass(frozen=True, slots=True)
class WikiPopulationSummary:
    """Counts for a wiki->model population run.

    Attributes:
        created_card_slots: Number of new CardSlot rows created.
        updated_card_slots: Number of existing CardSlot rows updated.
        created_card_definitions: Number of new CardDefinition rows created.
        updated_card_definitions: Number of existing CardDefinition rows updated.
        created_card_parameters: Number of new CardParameter rows created.
        created_card_levels: Number of new CardLevel rows created.
        created_bot_definitions: Number of new BotDefinition rows created.
        updated_bot_definitions: Number of existing BotDefinition rows updated.
        created_bot_levels: Number of new BotLevel rows created.
        created_bot_parameters: Number of new BotParameter rows created.
        created_guardian_chip_definitions: Number of new GuardianChipDefinition rows created.
        updated_guardian_chip_definitions: Number of existing GuardianChipDefinition rows updated.
        created_guardian_chip_levels: Number of new GuardianChipLevel rows created.
        created_guardian_chip_parameters: Number of new GuardianChipParameter rows created.
        created_ultimate_weapon_definitions: Number of new UltimateWeaponDefinition rows created.
        updated_ultimate_weapon_definitions: Number of existing UltimateWeaponDefinition rows updated.
        created_ultimate_weapon_levels: Number of new UltimateWeaponLevel rows created.
        created_ultimate_weapon_parameters: Number of new UltimateWeaponParameter rows created.
    """

    created_card_slots: int = 0
    updated_card_slots: int = 0
    created_card_definitions: int = 0
    updated_card_definitions: int = 0
    created_card_parameters: int = 0
    created_card_levels: int = 0
    created_bot_definitions: int = 0
    updated_bot_definitions: int = 0
    created_bot_levels: int = 0
    created_bot_parameters: int = 0
    created_guardian_chip_definitions: int = 0
    updated_guardian_chip_definitions: int = 0
    created_guardian_chip_levels: int = 0
    created_guardian_chip_parameters: int = 0
    created_ultimate_weapon_definitions: int = 0
    updated_ultimate_weapon_definitions: int = 0
    created_ultimate_weapon_levels: int = 0
    created_ultimate_weapon_parameters: int = 0

    def __add__(self, other: "WikiPopulationSummary") -> "WikiPopulationSummary":
        """Combine two summaries."""

        return WikiPopulationSummary(
            created_card_slots=self.created_card_slots + other.created_card_slots,
            updated_card_slots=self.updated_card_slots + other.updated_card_slots,
            created_card_definitions=self.created_card_definitions + other.created_card_definitions,
            updated_card_definitions=self.updated_card_definitions + other.updated_card_definitions,
            created_card_parameters=self.created_card_parameters + other.created_card_parameters,
            created_card_levels=self.created_card_levels + other.created_card_levels,
            created_bot_definitions=self.created_bot_definitions + other.created_bot_definitions,
            updated_bot_definitions=self.updated_bot_definitions + other.updated_bot_definitions,
            created_bot_levels=self.created_bot_levels + other.created_bot_levels,
            created_bot_parameters=self.created_bot_parameters + other.created_bot_parameters,
            created_guardian_chip_definitions=self.created_guardian_chip_definitions
            + other.created_guardian_chip_definitions,
            updated_guardian_chip_definitions=self.updated_guardian_chip_definitions
            + other.updated_guardian_chip_definitions,
            created_guardian_chip_levels=self.created_guardian_chip_levels
            + other.created_guardian_chip_levels,
            created_guardian_chip_parameters=self.created_guardian_chip_parameters
            + other.created_guardian_chip_parameters,
            created_ultimate_weapon_definitions=self.created_ultimate_weapon_definitions
            + other.created_ultimate_weapon_definitions,
            updated_ultimate_weapon_definitions=self.updated_ultimate_weapon_definitions
            + other.updated_ultimate_weapon_definitions,
            created_ultimate_weapon_levels=self.created_ultimate_weapon_levels
            + other.created_ultimate_weapon_levels,
            created_ultimate_weapon_parameters=self.created_ultimate_weapon_parameters
            + other.created_ultimate_weapon_parameters,
        )


def _select_latest_per_entity(qs) -> dict[str, WikiData]:
    """Select the latest WikiData revision per entity_id for a queryset."""

    latest: dict[str, WikiData] = {}
    for row in qs.order_by("entity_id", "-last_seen", "-id").iterator():
        if row.entity_id not in latest:
            latest[row.entity_id] = row
    return latest


_LEVEL_KEYS: tuple[str, ...] = ("Level", "Lvl", "Lv")
_STAR_KEYS: tuple[str, ...] = ("Star", "Tier")
_METADATA_KEYS: tuple[str, ...] = ("Description", "Rarity", "Unlock", "Unlock Text", "Unlock Condition")


def _latest_per_entity_level(qs) -> dict[tuple[str, int | None, int | None], WikiData]:
    """Select the latest WikiData revision per (entity, level, star)."""

    latest: dict[tuple[str, int | None, int | None], WikiData] = {}
    for row in qs.order_by("entity_id", "-last_seen", "-id").iterator():
        level, star = _parse_level_fields(row.raw_row)
        base_entity_id = (row.raw_row.get("_wiki_entity_id") or row.entity_id or "").strip()
        key = (base_entity_id, level, star)
        if key not in latest:
            latest[key] = row
    return latest


def _parse_level_fields(raw_row: dict) -> tuple[int | None, int | None]:
    """Parse level and star integers from a raw wiki row."""

    level_raw = _first_key(raw_row, _LEVEL_KEYS)
    level_value: int | None = None
    if level_raw:
        try:
            level_value = int((raw_row.get(level_raw) or "").strip())
        except ValueError:
            level_value = None
    star_raw = _first_key(raw_row, _STAR_KEYS)
    star_value: int | None = None
    if star_raw:
        try:
            star_value = int((raw_row.get(star_raw) or "").strip())
        except ValueError:
            star_value = None
    return level_value, star_value


def _entity_name(raw_row: dict, *, name_keys: tuple[str, ...], fallback: str) -> str:
    """Extract an entity name from known name columns or fall back."""

    for key in name_keys:
        value = (raw_row.get(key) or "").strip()
        if value:
            return value
    return fallback.strip()


def _unit_for_kind(kind: Unit.Kind) -> Unit:
    """Return or create a Unit row for the given Unit.Kind."""

    defaults = {
        Unit.Kind.COUNT: {"symbol": "", "kind": Unit.Kind.COUNT},
        Unit.Kind.PERCENT: {"symbol": "%", "kind": Unit.Kind.PERCENT},
        Unit.Kind.SECONDS: {"symbol": "s", "kind": Unit.Kind.SECONDS},
        Unit.Kind.MULTIPLIER: {"symbol": "x", "kind": Unit.Kind.MULTIPLIER},
        Unit.Kind.CURRENCY: {"symbol": "", "kind": Unit.Kind.CURRENCY},
        Unit.Kind.UNKNOWN: {"symbol": "", "kind": Unit.Kind.UNKNOWN},
    }
    return Unit.objects.get_or_create(name=kind.label, defaults=defaults[kind])[0]


def _apply_metadata(definition, raw_row: dict) -> bool:
    """Update definition metadata fields from a wiki row.

    Returns True if the definition was updated.
    """

    updated = False
    description = (raw_row.get("Description") or "").strip()
    rarity = (raw_row.get("Rarity") or "").strip()
    unlock_text = (raw_row.get("Unlock") or raw_row.get("Unlock Text") or raw_row.get("Unlock Condition") or "").strip()

    if description and getattr(definition, "description", "") != description:
        definition.description = description
        updated = True
    if rarity and getattr(definition, "rarity", "") != rarity:
        definition.rarity = rarity
        updated = True
    if unlock_text and getattr(definition, "unlock_text", "") != unlock_text:
        definition.unlock_text = unlock_text
        updated = True
    if updated:
        definition.save(update_fields=["description", "rarity", "unlock_text"])
    return updated


def _first_key(raw_row: dict, keys: tuple[str, ...]) -> str | None:
    """Return the first matching key present in a WikiData raw_row.

    Args:
        raw_row: The WikiData row mapping (raw column names -> values).
        keys: Candidate keys to check, in priority order.

    Returns:
        The matching key if present, otherwise None.
    """

    for key in keys:
        if key in raw_row:
            return key
    return None


def _is_card_slot_row(raw_row: dict) -> bool:
    """Return True when a raw_row looks like the Card Slots table.

    The wiki has used multiple header variants over time. This helper accepts
    known pairs while staying strict to avoid misclassifying other rows.

    Args:
        raw_row: The WikiData row mapping (raw column names -> values).

    Returns:
        True if the row looks like a card-slot row, otherwise False.
    """

    slot_key = _first_key(raw_row, ("Slots", "Slot"))
    cost_key = _first_key(raw_row, ("Cost", "Gem Cost", "Unlock Cost"))
    return slot_key is not None and cost_key is not None


def populate_card_slots_from_wiki(*, write: bool) -> WikiPopulationSummary:
    """Create/update CardSlot rows from wiki-derived slot tables.

    The slot table is identified heuristically by the presence of a `Slot`/`Slots`
    column and a cost column (ex: `Gem Cost`).

    Args:
        write: When True, persist changes to the database. When False, compute
            counts only.

    Returns:
        A WikiPopulationSummary containing slot create/update counts.
    """

    candidates = WikiData.objects.filter(
        deprecated=False,
        parse_version__in=("cards_v1", "cards_slots_v1"),
    )
    slot_ids: list[int] = []
    for row in candidates.order_by("-last_seen", "-id").iterator():
        if _is_card_slot_row(row.raw_row):
            slot_ids.append(row.id)
    latest_by_entity = _select_latest_per_entity(WikiData.objects.filter(id__in=slot_ids))

    created = 0
    updated = 0
    for row in latest_by_entity.values():
        slot_key = _first_key(row.raw_row, ("Slots", "Slot"))
        cost_key = _first_key(row.raw_row, ("Cost", "Gem Cost", "Unlock Cost"))
        if slot_key is None or cost_key is None:
            continue

        slot_raw = (row.raw_row.get(slot_key) or "").strip()
        cost_raw = (row.raw_row.get(cost_key) or "").strip()
        try:
            slot_number = int(slot_raw)
        except ValueError:
            continue

        existing = CardSlot.objects.filter(slot_number=slot_number).first()
        if existing is None:
            created += 1
            if write:
                CardSlot.objects.create(
                    slot_number=slot_number,
                    unlock_cost_raw=cost_raw,
                    source_wikidata=row,
                )
            continue

        needs_update = (
            existing.unlock_cost_raw != cost_raw or existing.source_wikidata_id != row.id
        )
        if needs_update:
            updated += 1
            if write:
                existing.unlock_cost_raw = cost_raw
                existing.source_wikidata = row
                existing.save(update_fields=["unlock_cost_raw", "source_wikidata"])

    return WikiPopulationSummary(created_card_slots=created, updated_card_slots=updated)


def populate_cards_from_wiki(*, write: bool) -> WikiPopulationSummary:
    """Create/update CardDefinition and CardParameter rows from wiki-derived card tables.

    Card rows are identified by the presence of a `Card` or `Name` column in
    `WikiData.raw_row`. When `_wiki_table_label` is present (from the
    `cards_list` scrape), it is stored as a `Rarity` parameter.

    Args:
        write: When True, persist changes to the database. When False, compute
            counts only.

    Returns:
        A WikiPopulationSummary containing card definition/parameter counts.
    """

    candidates = WikiData.objects.filter(deprecated=False)
    cards_list = candidates.filter(parse_version="cards_list_v1").order_by("entity_id", "-last_seen", "-id")
    cards_v1 = candidates.filter(parse_version="cards_v1").order_by("entity_id", "-last_seen", "-id")

    latest_list = _select_latest_per_entity(cards_list)
    latest_v1 = {
        entity_id: row
        for entity_id, row in _select_latest_per_entity(cards_v1).items()
        if not _is_card_slot_row(row.raw_row)
    }

    selected_by_entity: dict[str, WikiData] = {}
    for entity_id in set(latest_list) | set(latest_v1):
        row = latest_list.get(entity_id) or latest_v1.get(entity_id)
        if row is None:
            continue
        if not ({"Card", "Name"} & set(row.raw_row.keys())) and row.canonical_name == "Unknown":
            continue
        selected_by_entity[entity_id] = row

    created_defs = 0
    updated_defs = 0
    cleared_params = 0

    for row in selected_by_entity.values():
        name = (row.raw_row.get("Card") or row.raw_row.get("Name") or row.canonical_name).strip()
        if not name:
            continue

        raw_row = dict(row.raw_row)
        table_label = raw_row.pop("_wiki_table_label", "").strip()
        if table_label and "Rarity" not in raw_row:
            raw_row["Rarity"] = table_label

        existing = CardDefinition.objects.filter(name=name).first()
        if existing is None:
            created_defs += 1
            if write:
                existing = CardDefinition.objects.create(
                    name=name,
                    wiki_page_url=row.page_url,
                    wiki_entity_id=row.entity_id,
                    rarity=raw_row.get("Rarity", ""),
                    description=raw_row.get("Description", ""),
                    unlock_text=raw_row.get("Unlock", "") or raw_row.get("Unlock Text", "") or raw_row.get("Unlock Condition", ""),
                )
        else:
            needs_update = False
            if not existing.wiki_page_url and row.page_url:
                existing.wiki_page_url = row.page_url
                needs_update = True
            if not existing.wiki_entity_id and row.entity_id:
                existing.wiki_entity_id = row.entity_id
                needs_update = True
            if needs_update and write:
                updated_defs += 1
                existing.save(update_fields=["wiki_page_url", "wiki_entity_id"])
            elif needs_update:
                updated_defs += 1
            if write and existing is not None:
                cleared_params += CardParameter.objects.filter(card_definition=existing).delete()[0]
                _apply_metadata(existing, raw_row)

    return WikiPopulationSummary(
        created_card_definitions=created_defs,
        updated_card_definitions=updated_defs,
        created_card_parameters=0,
        created_card_levels=0,
    )


def populate_card_levels_from_wiki(*, write: bool) -> WikiPopulationSummary:
    """Create CardLevel rows from wiki-derived level tables (when available).

    This is a forward-compatible hook: current wiki ingestion focuses on card
    slots and card lists, so this function is expected to be a no-op until
    `WikiData` includes a dedicated card-level parse_version.

    Args:
        write: When True, persist changes to the database. When False, compute
            counts only.

    Returns:
        A WikiPopulationSummary containing card level create counts.
    """

    candidates = WikiData.objects.filter(deprecated=False, parse_version="card_levels_v1")
    latest = _select_latest_per_entity(candidates)

    created_levels = 0
    for row in latest.values():
        name = (row.raw_row.get("Card") or row.raw_row.get("Name") or row.canonical_name).strip()
        if not name:
            continue
        level_raw = (row.raw_row.get("Level") or "").strip()
        star_raw = (row.raw_row.get("Star") or "").strip()
        try:
            level = int(level_raw)
        except ValueError:
            continue
        star = None
        if star_raw:
            try:
                star = int(star_raw)
            except ValueError:
                star = None

        card = CardDefinition.objects.filter(name=name).first()
        if card is None:
            continue

        exists = CardLevel.objects.filter(
            card_definition=card,
            level=level,
            star=star,
            source_wikidata=row,
        ).exists()
        if exists:
            continue
        created_levels += 1
        if write:
            CardLevel.objects.create(
                card_definition=card,
                level=level,
                star=star,
                raw_row=row.raw_row,
                source_wikidata=row,
            )

    return WikiPopulationSummary(created_card_levels=created_levels)


def populate_all_cards_from_wiki(*, write: bool) -> WikiPopulationSummary:
    """Populate all card-related Phase 3 models from existing WikiData.

    Args:
        write: When True, persist changes to the database. When False, compute
            counts only.

    Returns:
        A combined WikiPopulationSummary.
    """

    if not write:
        return (
            populate_card_slots_from_wiki(write=False)
            + populate_cards_from_wiki(write=False)
            + populate_card_levels_from_wiki(write=False)
        )

    with transaction.atomic():
        return (
            populate_card_slots_from_wiki(write=True)
            + populate_cards_from_wiki(write=True)
            + populate_card_levels_from_wiki(write=True)
        )


def populate_bots_from_wiki(*, write: bool) -> WikiPopulationSummary:
    """Create/update bot definitions, levels, and parameters from wiki tables."""

    candidates = WikiData.objects.filter(deprecated=False, parse_version__in=("bots_v1",))
    latest = _latest_per_entity_level(candidates)

    created_defs = 0
    updated_defs = 0
    created_levels = 0
    created_params = 0

    for (entity_id, level_value, star_value), row in latest.items():
        name = _entity_name(row.raw_row, name_keys=("Bot", "Name"), fallback=row.canonical_name)
        if not name:
            continue

        slug = entity_id or make_entity_id(name)
        defaults = {
            "wiki_page_url": row.page_url,
            "wiki_entity_id": entity_id,
        }
        bot_def, created = BotDefinition.objects.get_or_create(name=name, defaults=defaults)
        if created:
            created_defs += 1
        else:
            needs_update = False
            if not bot_def.wiki_page_url and row.page_url:
                bot_def.wiki_page_url = row.page_url
                needs_update = True
            if not bot_def.wiki_entity_id and entity_id:
                bot_def.wiki_entity_id = entity_id
                needs_update = True
            if needs_update and write:
                bot_def.save(update_fields=["wiki_page_url", "wiki_entity_id"])
                updated_defs += 1
            elif needs_update:
                updated_defs += 1
        if write:
            _apply_metadata(bot_def, row.raw_row)

        allowed = allowed_parameters_for("bot", slug)
        if write and not allowed:
            BotParameter.objects.filter(bot_definition=bot_def).delete()

        if level_value is None:
            continue

        bot_level, level_created = BotLevel.objects.get_or_create(
            bot_definition=bot_def,
            level=level_value,
            star=star_value,
            defaults={"raw_row": row.raw_row, "source_wikidata": row},
        )
        if level_created:
            created_levels += 1
        elif write:
            bot_level.raw_row = row.raw_row
            bot_level.source_wikidata = row
            bot_level.save(update_fields=["raw_row", "source_wikidata"])

        if not allowed:
            continue

        if write:
            BotParameter.objects.filter(bot_definition=bot_def).exclude(key__in=allowed.keys()).delete()

        skip_keys = set(_LEVEL_KEYS + _STAR_KEYS + _METADATA_KEYS + ("Bot", "Name"))
        for key, value in row.raw_row.items():
            if key in skip_keys or not value:
                continue
            entry = allowed.get(key)
            if entry is None:
                continue
            unit = _unit_for_kind(entry.unit_kind)
            param, created_param = BotParameter.objects.update_or_create(
                bot_level=bot_level,
                key=key,
                defaults={
                    "raw_value": value,
                    "unit": unit,
                    "source_wikidata": row,
                },
            )
            if created_param:
                created_params += 1

    return WikiPopulationSummary(
        created_bot_definitions=created_defs,
        updated_bot_definitions=updated_defs,
        created_bot_levels=created_levels,
        created_bot_parameters=created_params,
    )


def populate_guardian_chips_from_wiki(*, write: bool) -> WikiPopulationSummary:
    """Create/update guardian chip definitions, levels, and parameters from wiki tables."""

    candidates = WikiData.objects.filter(deprecated=False, parse_version__in=("guardian_chips_v1", "guardians_v1"))
    latest = _latest_per_entity_level(candidates)

    created_defs = 0
    updated_defs = 0
    created_levels = 0
    created_params = 0

    for (entity_id, level_value, star_value), row in latest.items():
        name = _entity_name(
            row.raw_row,
            name_keys=("Guardian", "Guardian Chip", "Name"),
            fallback=row.canonical_name,
        )
        if not name:
            continue

        slug = entity_id or make_entity_id(name)
        defaults = {
            "wiki_page_url": row.page_url,
            "wiki_entity_id": entity_id,
        }
        chip_def, created = GuardianChipDefinition.objects.get_or_create(name=name, defaults=defaults)
        if created:
            created_defs += 1
        else:
            needs_update = False
            if not chip_def.wiki_page_url and row.page_url:
                chip_def.wiki_page_url = row.page_url
                needs_update = True
            if not chip_def.wiki_entity_id and entity_id:
                chip_def.wiki_entity_id = entity_id
                needs_update = True
            if needs_update and write:
                chip_def.save(update_fields=["wiki_page_url", "wiki_entity_id"])
                updated_defs += 1
            elif needs_update:
                updated_defs += 1
        if write:
            _apply_metadata(chip_def, row.raw_row)

        allowed = allowed_parameters_for("guardian", slug)
        if write and not allowed:
            GuardianChipParameter.objects.filter(guardian_chip_definition=chip_def).delete()

        if level_value is None:
            continue

        chip_level, level_created = GuardianChipLevel.objects.get_or_create(
            guardian_chip_definition=chip_def,
            level=level_value,
            star=star_value,
            defaults={"raw_row": row.raw_row, "source_wikidata": row},
        )
        if level_created:
            created_levels += 1
        elif write:
            chip_level.raw_row = row.raw_row
            chip_level.source_wikidata = row
            chip_level.save(update_fields=["raw_row", "source_wikidata"])

        if not allowed:
            continue

        if write:
            GuardianChipParameter.objects.filter(guardian_chip_definition=chip_def).exclude(
                key__in=allowed.keys()
            ).delete()

        skip_keys = set(_LEVEL_KEYS + _STAR_KEYS + _METADATA_KEYS + ("Guardian", "Guardian Chip", "Name"))
        for key, value in row.raw_row.items():
            if key in skip_keys or not value:
                continue
            entry = allowed.get(key)
            if entry is None:
                continue
            unit = _unit_for_kind(entry.unit_kind)
            param, created_param = GuardianChipParameter.objects.update_or_create(
                guardian_chip_level=chip_level,
                key=key,
                defaults={
                    "raw_value": value,
                    "unit": unit,
                    "source_wikidata": row,
                },
            )
            if created_param:
                created_params += 1

    return WikiPopulationSummary(
        created_guardian_chip_definitions=created_defs,
        updated_guardian_chip_definitions=updated_defs,
        created_guardian_chip_levels=created_levels,
        created_guardian_chip_parameters=created_params,
    )


def populate_ultimate_weapons_from_wiki(*, write: bool) -> WikiPopulationSummary:
    """Create/update ultimate weapon definitions, levels, and parameters from wiki tables."""

    candidates = WikiData.objects.filter(deprecated=False, parse_version__in=("ultimate_weapons_v1",))
    latest = _latest_per_entity_level(candidates)

    created_defs = 0
    updated_defs = 0
    created_levels = 0
    created_params = 0

    for (entity_id, level_value, star_value), row in latest.items():
        name = _entity_name(row.raw_row, name_keys=("Ultimate Weapon", "Name", "Weapon"), fallback=row.canonical_name)
        if not name:
            continue

        slug = entity_id or make_entity_id(name)
        defaults = {
            "wiki_page_url": row.page_url,
            "wiki_entity_id": entity_id,
        }
        uw_def, created = UltimateWeaponDefinition.objects.get_or_create(name=name, defaults=defaults)
        if created:
            created_defs += 1
        else:
            needs_update = False
            if not uw_def.wiki_page_url and row.page_url:
                uw_def.wiki_page_url = row.page_url
                needs_update = True
            if not uw_def.wiki_entity_id and entity_id:
                uw_def.wiki_entity_id = entity_id
                needs_update = True
            if needs_update and write:
                uw_def.save(update_fields=["wiki_page_url", "wiki_entity_id"])
                updated_defs += 1
            elif needs_update:
                updated_defs += 1
        if write:
            _apply_metadata(uw_def, row.raw_row)

        allowed = allowed_parameters_for("uw", slug)
        if write and not allowed:
            UltimateWeaponParameter.objects.filter(ultimate_weapon_definition=uw_def).delete()

        if level_value is None:
            continue

        uw_level, level_created = UltimateWeaponLevel.objects.get_or_create(
            ultimate_weapon_definition=uw_def,
            level=level_value,
            star=star_value,
            defaults={"raw_row": row.raw_row, "source_wikidata": row},
        )
        if level_created:
            created_levels += 1
        elif write:
            uw_level.raw_row = row.raw_row
            uw_level.source_wikidata = row
            uw_level.save(update_fields=["raw_row", "source_wikidata"])

        if not allowed:
            continue

        if write:
            UltimateWeaponParameter.objects.filter(ultimate_weapon_definition=uw_def).exclude(
                key__in=allowed.keys()
            ).delete()

        skip_keys = set(_LEVEL_KEYS + _STAR_KEYS + _METADATA_KEYS + ("Ultimate Weapon", "Name", "Weapon"))
        for key, value in row.raw_row.items():
            if key in skip_keys or not value:
                continue
            entry = allowed.get(key)
            if entry is None:
                continue
            unit = _unit_for_kind(entry.unit_kind)
            param, created_param = UltimateWeaponParameter.objects.update_or_create(
                ultimate_weapon_level=uw_level,
                key=key,
                defaults={
                    "raw_value": value,
                    "unit": unit,
                    "source_wikidata": row,
                },
            )
            if created_param:
                created_params += 1

    return WikiPopulationSummary(
        created_ultimate_weapon_definitions=created_defs,
        updated_ultimate_weapon_definitions=updated_defs,
        created_ultimate_weapon_levels=created_levels,
        created_ultimate_weapon_parameters=created_params,
    )


def populate_all_from_wiki(*, write: bool) -> WikiPopulationSummary:
    """Populate cards, bots, guardian chips, and ultimate weapons."""

    if not write:
        return (
            populate_all_cards_from_wiki(write=False)
            + populate_bots_from_wiki(write=False)
            + populate_guardian_chips_from_wiki(write=False)
            + populate_ultimate_weapons_from_wiki(write=False)
        )

    with transaction.atomic():
        return (
            populate_all_cards_from_wiki(write=True)
            + populate_bots_from_wiki(write=True)
            + populate_guardian_chips_from_wiki(write=True)
            + populate_ultimate_weapons_from_wiki(write=True)
        )
