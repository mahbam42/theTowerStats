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

from core.models import CardDefinition, CardLevel, CardParameter, CardSlot, WikiData


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
    """

    created_card_slots: int = 0
    updated_card_slots: int = 0
    created_card_definitions: int = 0
    updated_card_definitions: int = 0
    created_card_parameters: int = 0
    created_card_levels: int = 0

    def __add__(self, other: "WikiPopulationSummary") -> "WikiPopulationSummary":
        """Combine two summaries."""

        return WikiPopulationSummary(
            created_card_slots=self.created_card_slots + other.created_card_slots,
            updated_card_slots=self.updated_card_slots + other.updated_card_slots,
            created_card_definitions=self.created_card_definitions + other.created_card_definitions,
            updated_card_definitions=self.updated_card_definitions + other.updated_card_definitions,
            created_card_parameters=self.created_card_parameters + other.created_card_parameters,
            created_card_levels=self.created_card_levels + other.created_card_levels,
        )


def _select_latest_per_entity(qs) -> dict[str, WikiData]:
    """Select the latest WikiData revision per entity_id for a queryset."""

    latest: dict[str, WikiData] = {}
    for row in qs.order_by("entity_id", "-last_seen", "-id").iterator():
        if row.entity_id not in latest:
            latest[row.entity_id] = row
    return latest


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
    created_params = 0

    for row in selected_by_entity.values():
        name = (row.raw_row.get("Card") or row.raw_row.get("Name") or row.canonical_name).strip()
        if not name:
            continue

        existing = CardDefinition.objects.filter(name=name).first()
        definition_will_exist = existing is not None
        if existing is None:
            created_defs += 1
            definition_will_exist = True
            if write:
                existing = CardDefinition.objects.create(
                    name=name,
                    wiki_page_url=row.page_url,
                    wiki_entity_id=row.entity_id,
                )
        else:
            needs_update = False
            if not existing.wiki_page_url and row.page_url:
                existing.wiki_page_url = row.page_url
                needs_update = True
            if not existing.wiki_entity_id and row.entity_id:
                existing.wiki_entity_id = row.entity_id
                needs_update = True
            if needs_update:
                updated_defs += 1
                if write:
                    existing.save(update_fields=["wiki_page_url", "wiki_entity_id"])

        if not definition_will_exist:
            continue

        raw_row = dict(row.raw_row)
        table_label = raw_row.pop("_wiki_table_label", "").strip()
        if table_label and "Rarity" not in raw_row:
            raw_row["Rarity"] = table_label

        for key, value in raw_row.items():
            if key in {"Card", "Name"}:
                continue
            if not value:
                continue
            if existing is None:
                created_params += 1
                continue
            already = CardParameter.objects.filter(
                card_definition=existing,
                key=key,
                raw_value=value,
                source_wikidata=row,
            ).exists()
            if already:
                continue
            created_params += 1
            if write:
                CardParameter.objects.create(
                    card_definition=existing,
                    key=key,
                    raw_value=value,
                    unit=None,
                    source_wikidata=row,
                )

    return WikiPopulationSummary(
        created_card_definitions=created_defs,
        updated_card_definitions=updated_defs,
        created_card_parameters=created_params,
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
