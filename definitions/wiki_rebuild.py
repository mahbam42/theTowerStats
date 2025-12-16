"""Rebuild structured Definitions from versioned WikiData.

This module performs the "WikiData -> Definitions" translation step for the
Prompt11/Prompt12 architecture:
- Definitions are upserted by slug (stable identity),
- Parameter *levels* are recreated from the latest WikiData rows,
- Player and GameData tables are not modified.

This module is intentionally offline: it reads only from the local `WikiData`
table. Fetching/scraping is handled separately (see `fetch_wiki_data`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace

from django.db import transaction

from definitions.models import (
    BotDefinition,
    BotParameterDefinition,
    BotParameterLevel,
    CardDefinition,
    Currency,
    GuardianChipDefinition,
    GuardianChipParameterDefinition,
    GuardianChipParameterLevel,
    ParameterKey,
    UltimateWeaponDefinition,
    UltimateWeaponParameterDefinition,
    UltimateWeaponParameterLevel,
    WikiData,
)

_SLUG_RE = re.compile(r"[^a-z0-9]+")
_PLACEHOLDER_RE = re.compile(r"^(?:-|—|–|null|none)?$", re.IGNORECASE)


def _slugify(value: str) -> str:
    """Convert an arbitrary display name into a stable slug."""

    lowered = (value or "").strip().casefold()
    slug = _SLUG_RE.sub("_", lowered).strip("_")
    return slug or "unknown"


@dataclass(frozen=True, slots=True)
class RebuildSummary:
    """Counts for a rebuild run."""

    created_definitions: int = 0
    updated_definitions: int = 0
    created_parameter_definitions: int = 0
    updated_parameter_definitions: int = 0
    created_parameter_levels: int = 0
    deleted_parameter_levels: int = 0


def _latest_rows_for_parse_version(parse_version: str) -> list[WikiData]:
    """Return the latest WikiData row per (entity_id) for a parse_version."""

    latest_by_entity: dict[str, WikiData] = {}
    qs = WikiData.objects.filter(parse_version=parse_version).order_by("entity_id", "-last_seen", "-id")
    for row in qs.iterator():
        if row.entity_id not in latest_by_entity:
            latest_by_entity[row.entity_id] = row
    return list(latest_by_entity.values())


def _latest_leveled_rows(parse_version: str) -> dict[str, list[WikiData]]:
    """Return latest leveled WikiData rows grouped by base `_wiki_entity_id`."""

    grouped: dict[str, list[WikiData]] = {}
    rows = _latest_rows_for_parse_version(parse_version)
    for row in rows:
        base_entity_id = (row.raw_row.get("_wiki_entity_id") or row.entity_id or "").strip()
        if not base_entity_id:
            continue
        grouped.setdefault(base_entity_id, []).append(row)
    for base, items in grouped.items():
        items.sort(key=lambda r: _safe_int(r.raw_row.get("Level")), reverse=False)
        grouped[base] = items
    return grouped


def _safe_int(value: object) -> int:
    """Best-effort integer conversion for wiki level fields."""

    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return 0


def rebuild_cards_from_wikidata(*, write: bool, parse_version: str = "cards_list_v1") -> RebuildSummary:
    """Upsert CardDefinition rows from card list WikiData.

    Cards are definitions-only: no ParameterKey, and no upgrade tables in this phase.
    """

    summary = RebuildSummary()
    latest = _latest_rows_for_parse_version(parse_version)
    if not write:
        return RebuildSummary(created_definitions=len(latest))

    with transaction.atomic():
        for row in latest:
            slug = _slugify(row.canonical_name)
            defaults = {
                "name": row.canonical_name,
                "slug": slug,
                "wiki_page_url": row.page_url,
                "wiki_entity_id": row.raw_row.get("_wiki_entity_id", row.entity_id),
                "description": (row.raw_row.get("Description") or "").strip(),
                "rarity": (row.raw_row.get("Rarity") or "").strip(),
                "unlock_text": (row.raw_row.get("Unlock") or row.raw_row.get("Unlock Text") or "").strip(),
                "source_wikidata": row,
            }
            obj, created = CardDefinition.objects.update_or_create(slug=slug, defaults=defaults)
            summary = _bump_definition(summary, created)
    return summary


def rebuild_bots_from_wikidata(*, write: bool, parse_version: str = "bots_v1") -> RebuildSummary:
    """Upsert BotDefinition + bot parameter tables from bot upgrade WikiData."""

    summary = RebuildSummary()
    grouped = _latest_leveled_rows(parse_version)
    if not write:
        return RebuildSummary(created_definitions=len(grouped))

    with transaction.atomic():
        for slug, rows in grouped.items():
            example = rows[0]
            name = (example.raw_row.get("Bot") or example.canonical_name or slug).strip()
            bot, created = BotDefinition.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "slug": slug,
                    "wiki_page_url": example.page_url,
                    "wiki_entity_id": slug,
                    "description": (example.raw_row.get("Description") or "").strip(),
                    "source_wikidata": example,
                },
            )
            summary = _bump_definition(summary, created)

            # Bot table format: Level, Cost, then 4 parameters (Duration/Cooldown/Bonus/Range).
            parameter_headers = [h for h in rows[0].raw_row.keys() if h not in {"Level", "Cost"} and not str(h).startswith("_") and h != "Bot"]
            if len(parameter_headers) != 4:
                raise ValueError(
                    f"Bot upgrade table drift for slug={slug}: expected 4 parameters, got {parameter_headers!r}"
                )
            for header in parameter_headers:
                key = _bot_parameter_key(header)
                unit_kind = _bot_unit_kind(key)
                param_def, created_pd = BotParameterDefinition.objects.update_or_create(
                    bot_definition=bot,
                    key=key,
                    defaults={"display_name": header, "unit_kind": unit_kind},
                )
                summary = _bump_param_def(summary, created_pd)

                deleted = BotParameterLevel.objects.filter(parameter_definition=param_def).count()
                if deleted:
                    BotParameterLevel.objects.filter(parameter_definition=param_def).delete()
                    summary = replace(
                        summary,
                        deleted_parameter_levels=summary.deleted_parameter_levels + deleted,
                    )

                created_levels = 0
                for row in rows:
                    level = _safe_int(row.raw_row.get("Level"))
                    if level <= 0:
                        continue
                    value_raw = str(row.raw_row.get(header, "")).strip()
                    cost_raw = str(row.raw_row.get("Cost", "")).strip()
                    if _is_placeholder_or_total(value_raw) or _is_placeholder_or_total(cost_raw):
                        continue
                    BotParameterLevel.objects.create(
                        parameter_definition=param_def,
                        level=level,
                        value_raw=value_raw,
                        cost_raw=cost_raw,
                        currency=Currency.MEDALS,
                        source_wikidata=row,
                    )
                    created_levels += 1
                summary = replace(
                    summary,
                    created_parameter_levels=summary.created_parameter_levels + created_levels,
                )
    return summary


def _is_placeholder_or_total(value: str) -> bool:
    """Return True when a value represents a placeholder or a total row marker."""

    cleaned = (value or "").strip()
    if cleaned.casefold() == "total":
        return True
    return _PLACEHOLDER_RE.match(cleaned) is not None


def rebuild_ultimate_weapons_from_wikidata(
    *, write: bool, parse_version: str = "ultimate_weapons_v1"
) -> RebuildSummary:
    """Upsert UltimateWeaponDefinition + parameter tables from UW WikiData."""

    summary = RebuildSummary()
    grouped = _latest_leveled_rows(parse_version)
    if not write:
        return RebuildSummary(created_definitions=len(grouped))

    with transaction.atomic():
        for slug, rows in grouped.items():
            example = rows[0]
            name = (example.raw_row.get("Ultimate Weapon") or example.canonical_name or slug).strip()
            uw, created = UltimateWeaponDefinition.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "slug": slug,
                    "wiki_page_url": example.page_url,
                    "wiki_entity_id": slug,
                    "description": (example.raw_row.get("Description") or "").strip(),
                    "source_wikidata": example,
                },
            )
            summary = _bump_definition(summary, created)

            mapping = _uw_value_headers_for_slug(slug)
            if len(mapping) != 3:
                raise ValueError(
                    f"Ultimate weapon mapping missing or incomplete for slug={slug}: mapping={mapping!r}"
                )
            for value_header, key in mapping.items():
                cost_header = _uw_cost_header(value_header=value_header, raw_row=example.raw_row)
                if cost_header is None:
                    raise ValueError(
                        f"Ultimate weapon cost header not found for slug={slug} value_header={value_header!r}"
                    )
                unit_kind = _uw_unit_kind(key)
                param_def, created_pd = UltimateWeaponParameterDefinition.objects.update_or_create(
                    ultimate_weapon_definition=uw,
                    key=key,
                    defaults={"display_name": value_header, "unit_kind": unit_kind},
                )
                summary = _bump_param_def(summary, created_pd)

                deleted = UltimateWeaponParameterLevel.objects.filter(parameter_definition=param_def).count()
                if deleted:
                    UltimateWeaponParameterLevel.objects.filter(parameter_definition=param_def).delete()
                    summary = replace(
                        summary,
                        deleted_parameter_levels=summary.deleted_parameter_levels + deleted,
                    )

                created_levels = 0
                for row in rows:
                    level = _safe_int(row.raw_row.get("Level"))
                    if level <= 0:
                        continue
                    value_raw = str(row.raw_row.get(value_header, "")).strip()
                    cost_raw = str(row.raw_row.get(cost_header, "")).strip()
                    if _is_placeholder_or_total(value_raw) or _is_placeholder_or_total(cost_raw):
                        continue
                    UltimateWeaponParameterLevel.objects.create(
                        parameter_definition=param_def,
                        level=level,
                        value_raw=value_raw,
                        cost_raw=cost_raw,
                        currency=Currency.STONES,
                        source_wikidata=row,
                    )
                    created_levels += 1
                summary = replace(
                    summary,
                    created_parameter_levels=summary.created_parameter_levels + created_levels,
                )
    return summary


def rebuild_guardian_chips_from_wikidata(
    *, write: bool, parse_version: str = "guardian_chips_v1"
) -> RebuildSummary:
    """Upsert GuardianChipDefinition + parameter tables from guardian WikiData."""

    summary = RebuildSummary()
    grouped = _latest_leveled_rows(parse_version)
    if not write:
        return RebuildSummary(created_definitions=len(grouped))

    with transaction.atomic():
        for slug, rows in grouped.items():
            example = rows[0]
            name = (example.raw_row.get("Guardian") or example.canonical_name or slug).strip()
            chip, created = GuardianChipDefinition.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "slug": slug,
                    "wiki_page_url": example.page_url,
                    "wiki_entity_id": slug,
                    "description": (example.raw_row.get("Description") or "").strip(),
                    "source_wikidata": example,
                },
            )
            summary = _bump_definition(summary, created)

            pairs = _guardian_header_pairs(example.raw_row, slug=slug)
            if len(pairs) != 3:
                raise ValueError(
                    f"Guardian upgrade table drift for slug={slug}: expected 3 parameters, got {pairs!r}"
                )
            for value_header, cost_header in pairs:
                key = _guardian_parameter_key(value_header, slug=slug)
                unit_kind = _guardian_unit_kind(key)
                param_def, created_pd = GuardianChipParameterDefinition.objects.update_or_create(
                    guardian_chip_definition=chip,
                    key=key,
                    defaults={"display_name": value_header, "unit_kind": unit_kind},
                )
                summary = _bump_param_def(summary, created_pd)

                deleted = GuardianChipParameterLevel.objects.filter(parameter_definition=param_def).count()
                if deleted:
                    GuardianChipParameterLevel.objects.filter(parameter_definition=param_def).delete()
                    summary = replace(
                        summary,
                        deleted_parameter_levels=summary.deleted_parameter_levels + deleted,
                    )

                created_levels = 0
                for row in rows:
                    level = _safe_int(row.raw_row.get("Level"))
                    if level <= 0:
                        continue
                    value_raw = str(row.raw_row.get(value_header, "")).strip()
                    cost_raw = str(row.raw_row.get(cost_header, "")).strip()
                    if _is_placeholder_or_total(value_raw) or _is_placeholder_or_total(cost_raw):
                        continue
                    GuardianChipParameterLevel.objects.create(
                        parameter_definition=param_def,
                        level=level,
                        value_raw=value_raw,
                        cost_raw=cost_raw,
                        currency=Currency.BITS,
                        source_wikidata=row,
                    )
                    created_levels += 1
                summary = replace(
                    summary,
                    created_parameter_levels=summary.created_parameter_levels + created_levels,
                )
    return summary


def _bump_definition(summary: RebuildSummary, created: bool) -> RebuildSummary:
    """Return an updated summary for a created/updated definition."""

    if created:
        return replace(summary, created_definitions=summary.created_definitions + 1)
    return replace(summary, updated_definitions=summary.updated_definitions + 1)


def _bump_param_def(summary: RebuildSummary, created: bool) -> RebuildSummary:
    """Return an updated summary for a created/updated parameter definition."""

    if created:
        return replace(
            summary,
            created_parameter_definitions=summary.created_parameter_definitions + 1,
        )
    return replace(
        summary,
        updated_parameter_definitions=summary.updated_parameter_definitions + 1,
    )


def _bot_parameter_key(header: str) -> str:
    """Map a bot upgrade table header to a ParameterKey."""

    normalized = header.strip().casefold()
    if normalized == "duration":
        return ParameterKey.DURATION.value
    if normalized == "cooldown":
        return ParameterKey.COOLDOWN.value
    if normalized == "range":
        return ParameterKey.RANGE.value
    if normalized == "bonus":
        return ParameterKey.MULTIPLIER.value
    if normalized == "damage":
        return ParameterKey.DAMAGE.value
    if normalized == "damage reduction":
        return ParameterKey.DAMAGE_REDUCTION.value
    if normalized == "linger":
        return ParameterKey.LINGER.value
    return ParameterKey.MULTIPLIER.value


def _bot_unit_kind(key: str) -> str:
    """Infer a Unit.Kind for bot parameter keys."""

    if key in {ParameterKey.COOLDOWN.value, ParameterKey.DURATION.value}:
        return "seconds"
    if key == ParameterKey.LINGER.value:
        return "seconds"
    if key == ParameterKey.DAMAGE_REDUCTION.value:
        return "percent"
    if key == ParameterKey.RANGE.value:
        return "count"
    if key == ParameterKey.DAMAGE.value:
        return "count"
    return "multiplier"


def _uw_value_headers_for_slug(slug: str) -> dict[str, str]:
    """Return expected value headers and ParameterKey mapping for a UW slug."""

    mapping: dict[str, dict[str, str]] = {
        "chain_lightning": {
            "Damage": ParameterKey.DAMAGE.value,
            "Quantity": ParameterKey.QUANTITY.value,
            "Chance": ParameterKey.CHANCE.value,
        },
        "death_wave": {
            "Damage": ParameterKey.DAMAGE_MULTIPLIER.value,
            "Effect Wave Quantity": ParameterKey.EFFECT_WAVE.value,
            "Cooldown": ParameterKey.COOLDOWN.value,
        },
        "golden_tower": {
            "Multiplier": ParameterKey.COINS_MULTIPLIER.value,
            "Duration": ParameterKey.DURATION.value,
            "Cooldown": ParameterKey.COOLDOWN.value,
        },
        "spotlight": {
            "Bonus": ParameterKey.COINS_BONUS.value,
            "Angle": ParameterKey.ANGLE.value,
            "Quantity": ParameterKey.QUANTITY.value,
        },
        "smart_missiles": {
            "Damage": ParameterKey.DAMAGE_MULTIPLIER.value,
            "Quantity": ParameterKey.QUANTITY.value,
            "Cooldown": ParameterKey.COOLDOWN.value,
        },
        "chrono_field": {
            "Duration": ParameterKey.DURATION.value,
            "Slow": ParameterKey.SLOW.value,
            "Cooldown": ParameterKey.COOLDOWN.value,
        },
        "inner_land_mines": {
            "Damage %": ParameterKey.DAMAGE_PERCENT.value,
            "Quantity": ParameterKey.QUANTITY.value,
            "Cooldown": ParameterKey.COOLDOWN.value,
        },
        "poison_swamp": {
            "Damage": ParameterKey.DAMAGE_MULTIPLIER.value,
            "Duration": ParameterKey.DURATION.value,
            "Cooldown": ParameterKey.COOLDOWN.value,
        },
        "black_hole": {
            "Size": ParameterKey.SIZE.value,
            "Duration": ParameterKey.DURATION.value,
            "Cooldown": ParameterKey.COOLDOWN.value,
        },
    }
    return mapping.get(slug, {})


def _uw_cost_header(*, value_header: str, raw_row: dict) -> str | None:
    """Find the cost column header for a UW value header."""

    candidates = [
        f"Stones ({value_header})",
        f"Stone ({value_header})",
        f"Cost (Stones) ({value_header})",
        f"Cost (Stones) ({value_header})",
    ]
    for candidate in candidates:
        if candidate in raw_row:
            return candidate
    for key in raw_row.keys():
        if "Stones" in str(key) and value_header in str(key):
            return str(key)
    # Fallback: some tables interleave value/cost columns using generic "Cost" headers.
    keys = [str(k) for k in raw_row.keys()]
    for idx, key in enumerate(keys):
        if key == value_header:
            for j in range(idx + 1, min(idx + 4, len(keys))):
                if keys[j].casefold().startswith("cost"):
                    return keys[j]
    return None


def _uw_unit_kind(key: str) -> str:
    """Infer a Unit.Kind for UW parameter keys."""

    if key in {ParameterKey.COOLDOWN.value, ParameterKey.DURATION.value}:
        return "seconds"
    if key in {ParameterKey.CHANCE.value, ParameterKey.SLOW.value}:
        return "percent"
    if key in {
        ParameterKey.DAMAGE_MULTIPLIER.value,
        ParameterKey.COINS_MULTIPLIER.value,
        ParameterKey.MULTIPLIER.value,
    }:
        return "multiplier"
    return "count"


def _guardian_header_pairs(raw_row: dict, *, slug: str) -> list[tuple[str, str]]:
    """Return ordered (value_header, cost_header) pairs for a guardian chip row."""

    header_pairs: list[tuple[str, str]] = []
    keys = [str(k) for k in raw_row.keys()]
    seen_value: set[str] = set()
    for idx, key in enumerate(keys):
        if key in {"Level", "_wiki_entity_id", "Guardian"}:
            continue
        if key.startswith("_"):
            continue
        if "Bits" in key or "Cost (Bits)" in key:
            continue
        if key in seen_value:
            continue
        cost = None
        for j in range(idx + 1, min(idx + 4, len(keys))):
            candidate = keys[j]
            if "Bits" in candidate or "Cost (Bits)" in candidate:
                cost = candidate
                break
        if cost is None:
            continue
        header_pairs.append((key, cost))
        seen_value.add(key)
    # Ensure exactly three parameters per chip (Prompt11).
    return header_pairs[:3]


def _guardian_parameter_key(value_header: str, *, slug: str) -> str:
    """Map guardian chip value headers to ParameterKey."""

    normalized = value_header.strip().casefold()
    if slug == "ally":
        if "recovery amount" in normalized:
            return ParameterKey.RECOVERY_AMOUNT.value
        if "cooldown" in normalized:
            return ParameterKey.COOLDOWN.value
        if "max recovery" in normalized:
            return ParameterKey.MAX_RECOVERY.value
    if slug == "attack":
        if "percentage" in normalized:
            return ParameterKey.PERCENTAGE.value
        if "cooldown" in normalized:
            return ParameterKey.COOLDOWN.value
        if "targets" in normalized:
            return ParameterKey.TARGETS.value
    if slug == "fetch":
        if "cooldown" in normalized:
            return ParameterKey.COOLDOWN.value
        if "find chance" in normalized and "double" not in normalized:
            return ParameterKey.FIND_CHANCE.value
        if "double find chance" in normalized:
            return ParameterKey.DOUBLE_FIND_CHANCE.value
    if slug == "bounty":
        if "multiplier" in normalized:
            return ParameterKey.MULTIPLIER.value
        if "cooldown" in normalized:
            return ParameterKey.COOLDOWN.value
        if "targets" in normalized:
            return ParameterKey.TARGETS.value
    if slug == "summon":
        if "cooldown" in normalized:
            return ParameterKey.COOLDOWN.value
        if "duration" in normalized:
            return ParameterKey.DURATION.value
        if "cash bonus" in normalized:
            return ParameterKey.CASH_BONUS.value
    # Fallback: keep it stable but explicit failures should be enforced by tests.
    return ParameterKey.MULTIPLIER.value


def _guardian_unit_kind(key: str) -> str:
    """Infer a Unit.Kind for guardian parameter keys."""

    if key in {ParameterKey.COOLDOWN.value, ParameterKey.DURATION.value}:
        return "seconds"
    if key in {
        ParameterKey.FIND_CHANCE.value,
        ParameterKey.DOUBLE_FIND_CHANCE.value,
        ParameterKey.PERCENTAGE.value,
    }:
        return "percent"
    if key in {ParameterKey.MULTIPLIER.value}:
        return "multiplier"
    return "count"
