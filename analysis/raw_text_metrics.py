"""Helpers for extracting persisted Battle Report metrics from raw text."""

from __future__ import annotations

from typing import Final

from .battle_report_extract import ExtractedNumber, extract_numeric_value
from .quantity import UnitType


RAW_TEXT_METRIC_SPECS: Final[dict[str, tuple[str, UnitType]]] = {
    "coins_from_death_wave": ("Coins From Death Wave", UnitType.coins),
    "interest_earned": ("Interest earned", UnitType.cash),
    "cash_from_golden_tower": ("Cash From Golden Tower", UnitType.cash),
    "coins_from_golden_tower": ("Coins From Golden Tower", UnitType.coins),
    "coins_from_black_hole": ("Coins From Black Hole", UnitType.coins),
    "coins_from_spotlight": ("Coins From Spotlight", UnitType.coins),
    "coins_from_orb": ("Coins From Orb", UnitType.coins),
    "coins_from_coin_upgrade": ("Coins from Coin Upgrade", UnitType.coins),
    "coins_from_coin_bonuses": ("Coins from Coin Bonuses", UnitType.coins),
    "damage_dealt": ("Damage dealt", UnitType.damage),
    "projectiles_damage": ("Projectiles Damage", UnitType.damage),
    "thorn_damage": ("Thorn Damage", UnitType.damage),
    "orb_damage": ("Orb Damage", UnitType.damage),
    "land_mine_damage": ("Land Mine Damage", UnitType.damage),
    "inner_land_mine_damage": ("Inner Land Mine Damage", UnitType.damage),
    "chain_lightning_damage": ("Chain Lightning Damage", UnitType.damage),
    "death_wave_damage": ("Death Wave Damage", UnitType.damage),
    "death_ray_damage": ("Death Ray Damage", UnitType.damage),
    "smart_missile_damage": ("Smart Missile Damage", UnitType.damage),
    "black_hole_damage": ("Black Hole Damage", UnitType.damage),
    "swamp_damage": ("Swamp Damage", UnitType.damage),
    "electrons_damage": ("Electrons Damage", UnitType.damage),
    "rend_armor_damage": ("Rend Armor Damage", UnitType.damage),
    "enemies_hit_by_orbs": ("Enemies Hit by Orbs", UnitType.count),
    "enemies_destroyed_basic": ("Basic", UnitType.count),
    "enemies_destroyed_fast": ("Fast", UnitType.count),
    "enemies_destroyed_tank": ("Tank", UnitType.count),
    "enemies_destroyed_ranged": ("Ranged", UnitType.count),
    "enemies_destroyed_boss": ("Boss", UnitType.count),
    "enemies_destroyed_protector": ("Protector", UnitType.count),
    "enemies_destroyed_vampires": ("Vampires", UnitType.count),
    "enemies_destroyed_rays": ("Rays", UnitType.count),
    "enemies_destroyed_scatters": ("Scatters", UnitType.count),
    "enemies_destroyed_saboteur": ("Saboteur", UnitType.count),
    "enemies_destroyed_commander": ("Commander", UnitType.count),
    "enemies_destroyed_overcharge": ("Overcharge", UnitType.count),
    "enemies_destroyed_by_orbs": ("Destroyed By Orbs", UnitType.count),
    "enemies_destroyed_by_thorns": ("Destroyed by Thorns", UnitType.count),
    "enemies_destroyed_by_death_ray": ("Destroyed by Death Ray", UnitType.count),
    "enemies_destroyed_by_land_mine": ("Destroyed by Land Mine", UnitType.count),
    "enemies_destroyed_in_spotlight": ("Destroyed in Spotlight", UnitType.count),
    "enemies_destroyed_in_golden_bot": ("Destroyed in Golden Bot", UnitType.count),
    "guardian_damage": ("Damage", UnitType.damage),
    "guardian_summoned_enemies": ("Summoned enemies", UnitType.count),
    "guardian_coins_stolen": ("Guardian coins stolen", UnitType.coins),
    "guardian_coins_fetched": ("Coins Fetched", UnitType.coins),
    "guardian_gems_fetched": ("Gems", UnitType.count),
    "guardian_medals_fetched": ("Medals", UnitType.count),
    "guardian_reroll_shards_fetched": ("Reroll Shards", UnitType.count),
    "guardian_cannon_shards_fetched": ("Cannon Shards", UnitType.count),
    "guardian_armor_shards_fetched": ("Armor Shards", UnitType.count),
    "guardian_generator_shards_fetched": ("Generator Shards", UnitType.count),
    "guardian_core_shards_fetched": ("Core Shards", UnitType.count),
    "guardian_common_modules_fetched": ("Common Modules", UnitType.count),
    "guardian_rare_modules_fetched": ("Rare Modules", UnitType.count),
}


def extract_raw_text_metrics(raw_text: str) -> dict[str, ExtractedNumber]:
    """Return all parseable metric values from Battle Report text.

    Args:
        raw_text: Raw Battle Report text to parse.

    Returns:
        Mapping of metric_key -> ExtractedNumber for every metric present in the
        text. Missing or invalid labels are omitted, keeping extraction
        defensive and non-fatal.
    """

    extracted: dict[str, ExtractedNumber] = {}
    for key, (label, unit_type) in RAW_TEXT_METRIC_SPECS.items():
        parsed = extract_numeric_value(raw_text, label=label, unit_type=unit_type)
        if parsed is None:
            continue
        extracted[key] = parsed
    return extracted
