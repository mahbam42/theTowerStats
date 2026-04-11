"""Helpers for extracting persisted Battle Report metrics from raw text."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .battle_report_extract import MetricSelector, ExtractedNumber, extract_numeric_value_from_selectors
from .quantity import UnitType


@dataclass(frozen=True, slots=True)
class RawTextMetricSpec:
    """Selector metadata for an extracted Battle Report metric.

    Args:
        selectors: Ordered selectors that can provide the metric value.
        unit_type: Expected unit type used for parsing and validation.
    """

    selectors: tuple[MetricSelector, ...]
    unit_type: UnitType


def _top_level(label: str) -> MetricSelector:
    """Return a selector that matches a top-level report label."""

    return MetricSelector(label=label, section=None)


def _legacy(label: str) -> MetricSelector:
    """Return a selector that matches a legacy flat label anywhere."""

    return MetricSelector(label=label, match_any_section=True)


def _scoped(section: str, label: str) -> MetricSelector:
    """Return a selector for a v28 section-scoped label."""

    return MetricSelector(label=label, section=section)


RAW_TEXT_METRIC_SPECS: Final[dict[str, RawTextMetricSpec]] = {
    "game_reported_coins_per_hour": RawTextMetricSpec(
        selectors=(_top_level("Coins Per Hour"),),
        unit_type=UnitType.coins,
    ),
    "game_reported_cells_per_hour": RawTextMetricSpec(
        selectors=(_top_level("Cells Per Hour"),),
        unit_type=UnitType.count,
    ),
    "record_highest_coins_per_minute": RawTextMetricSpec(
        selectors=(_scoped("Records", "Highest Coins / Minute"),),
        unit_type=UnitType.coins,
    ),
    "record_largest_wave_skip": RawTextMetricSpec(
        selectors=(_scoped("Records", "Largest Wave Skip"),),
        unit_type=UnitType.count,
    ),
    "record_most_coins_from_wave_skip": RawTextMetricSpec(
        selectors=(_scoped("Records", "Most Coins From Wave Skip"),),
        unit_type=UnitType.coins,
    ),
    "record_most_cells_from_wave_skip": RawTextMetricSpec(
        selectors=(_scoped("Records", "Most Cells From Wave Skip"),),
        unit_type=UnitType.count,
    ),
    "record_largest_smart_missile_stack": RawTextMetricSpec(
        selectors=(_scoped("Records", "Largest Smart Missile Stack"),),
        unit_type=UnitType.count,
    ),
    "record_largest_golden_combo": RawTextMetricSpec(
        selectors=(_scoped("Records", "Largest Golden Combo"),),
        unit_type=UnitType.count,
    ),
    "record_most_coins_from_golden_combo": RawTextMetricSpec(
        selectors=(_scoped("Records", "Most Coins From Golden Combo"),),
        unit_type=UnitType.coins,
    ),
    "record_largest_inner_landmine_charge": RawTextMetricSpec(
        selectors=(_scoped("Records", "Largest Inner Landmine Charge"),),
        unit_type=UnitType.count,
    ),
    "coins_from_death_wave": RawTextMetricSpec(
        selectors=(
            _legacy("Coins From Death Wave"),
            _scoped("Coins", "Death Wave"),
        ),
        unit_type=UnitType.coins,
    ),
    "interest_earned": RawTextMetricSpec(
        selectors=(
            _legacy("Interest earned"),
            _scoped("Cash", "Interest earned"),
        ),
        unit_type=UnitType.cash,
    ),
    "cash_from_golden_tower": RawTextMetricSpec(
        selectors=(
            _legacy("Cash From Golden Tower"),
            _scoped("Cash", "Golden Tower"),
        ),
        unit_type=UnitType.cash,
    ),
    "coins_from_golden_tower": RawTextMetricSpec(
        selectors=(
            _legacy("Coins From Golden Tower"),
            _scoped("Coins", "Golden Tower"),
        ),
        unit_type=UnitType.coins,
    ),
    "coins_from_black_hole": RawTextMetricSpec(
        selectors=(
            _legacy("Coins From Black Hole"),
            _scoped("Coins", "Black Hole"),
        ),
        unit_type=UnitType.coins,
    ),
    "coins_from_spotlight": RawTextMetricSpec(
        selectors=(
            _legacy("Coins From Spotlight"),
            _scoped("Coins", "Spotlight"),
        ),
        unit_type=UnitType.coins,
    ),
    "coins_from_orb": RawTextMetricSpec(
        selectors=(
            _legacy("Coins From Orb"),
            _scoped("Coins", "Orbs"),
        ),
        unit_type=UnitType.coins,
    ),
    "coins_from_coin_upgrade": RawTextMetricSpec(
        selectors=(
            _legacy("Coins from Coin Upgrade"),
            _scoped("Coins", "Coin Bonus Upgrade"),
        ),
        unit_type=UnitType.coins,
    ),
    "coins_from_coin_bonuses": RawTextMetricSpec(
        selectors=(
            _legacy("Coins from Coin Bonuses"),
            _scoped("Coins", "Coins From Coin Bonuses"),
        ),
        unit_type=UnitType.coins,
    ),
    "coins_from_critical_coin": RawTextMetricSpec(
        selectors=(_scoped("Coins", "Critical Coin"),),
        unit_type=UnitType.coins,
    ),
    "coins_from_golden_combo": RawTextMetricSpec(
        selectors=(_scoped("Coins", "Golden Combo"),),
        unit_type=UnitType.coins,
    ),
    "free_attack_upgrades": RawTextMetricSpec(
        selectors=(_legacy("Free Attack Upgrade"), _scoped("Utility", "Free Attack Upgrade")),
        unit_type=UnitType.count,
    ),
    "free_defense_upgrades": RawTextMetricSpec(
        selectors=(_legacy("Free Defense Upgrade"), _scoped("Utility", "Free Defense Upgrade")),
        unit_type=UnitType.count,
    ),
    "free_utility_upgrades": RawTextMetricSpec(
        selectors=(_legacy("Free Utility Upgrade"), _scoped("Utility", "Free Utility Upgrade")),
        unit_type=UnitType.count,
    ),
    "recovery_packages": RawTextMetricSpec(
        selectors=(_legacy("Recovery Packages"), _scoped("Utility", "Recovery Packages")),
        unit_type=UnitType.count,
    ),
    "damage_dealt": RawTextMetricSpec(
        selectors=(_legacy("Damage dealt"), _scoped("Damage", "Damage Dealt")),
        unit_type=UnitType.damage,
    ),
    "projectiles_damage": RawTextMetricSpec(
        selectors=(_legacy("Projectiles Damage"), _scoped("Damage", "Projectiles")),
        unit_type=UnitType.damage,
    ),
    "thorn_damage": RawTextMetricSpec(
        selectors=(_legacy("Thorn Damage"), _legacy("Thorn damage"), _scoped("Damage", "Thorns")),
        unit_type=UnitType.damage,
    ),
    "orb_damage": RawTextMetricSpec(
        selectors=(_legacy("Orb Damage"), _scoped("Damage", "Orbs")),
        unit_type=UnitType.damage,
    ),
    "land_mine_damage": RawTextMetricSpec(
        selectors=(_legacy("Land Mine Damage"), _scoped("Damage", "Land Mines")),
        unit_type=UnitType.damage,
    ),
    "inner_land_mine_damage": RawTextMetricSpec(
        selectors=(_legacy("Inner Land Mine Damage"), _scoped("Damage", "Inner Land Mines")),
        unit_type=UnitType.damage,
    ),
    "chain_lightning_damage": RawTextMetricSpec(
        selectors=(_legacy("Chain Lightning Damage"), _scoped("Damage", "Chain Lightning")),
        unit_type=UnitType.damage,
    ),
    "death_wave_damage": RawTextMetricSpec(
        selectors=(_legacy("Death Wave Damage"), _scoped("Damage", "Death Wave")),
        unit_type=UnitType.damage,
    ),
    "death_ray_damage": RawTextMetricSpec(
        selectors=(_legacy("Death Ray Damage"), _scoped("Damage", "Death Ray")),
        unit_type=UnitType.damage,
    ),
    "smart_missile_damage": RawTextMetricSpec(
        selectors=(_legacy("Smart Missile Damage"), _scoped("Damage", "Smart Missiles")),
        unit_type=UnitType.damage,
    ),
    "black_hole_damage": RawTextMetricSpec(
        selectors=(
            _legacy("Black Hole Damage"),
            _legacy("Blackhole Damage"),
            _scoped("Damage", "Black Hole"),
        ),
        unit_type=UnitType.damage,
    ),
    "swamp_damage": RawTextMetricSpec(
        selectors=(_legacy("Swamp Damage"), _scoped("Damage", "Poison Swamp")),
        unit_type=UnitType.damage,
    ),
    "electrons_damage": RawTextMetricSpec(
        selectors=(_legacy("Electrons Damage"), _scoped("Damage", "Electrons")),
        unit_type=UnitType.damage,
    ),
    "rend_armor_damage": RawTextMetricSpec(
        selectors=(_legacy("Rend Armor Damage"), _scoped("Damage", "Rend Armor")),
        unit_type=UnitType.damage,
    ),
    "flame_bot_damage": RawTextMetricSpec(
        selectors=(_legacy("Flame Bot Damage"), _scoped("Damage", "Flame Bot")),
        unit_type=UnitType.damage,
    ),
    "golden_bot_coins_earned": RawTextMetricSpec(
        selectors=(
            _legacy("Golden Bot Coins Earned"),
            _scoped("Coins", "Golden Bot"),
        ),
        unit_type=UnitType.coins,
    ),
    "guardian_damage": RawTextMetricSpec(
        selectors=(
            _legacy("Damage"),
            _scoped("Guardian", "Damage"),
            _scoped("Damage", "Attack Chip"),
        ),
        unit_type=UnitType.damage,
    ),
    "tower_damage_taken": RawTextMetricSpec(
        selectors=(_scoped("Damage Taken", "Tower"),),
        unit_type=UnitType.damage,
    ),
    "wall_damage_taken": RawTextMetricSpec(
        selectors=(_scoped("Damage Taken", "Wall"),),
        unit_type=UnitType.damage,
    ),
    "hp_from_death_wave": RawTextMetricSpec(
        selectors=(
            _legacy("HP From Death Wave"),
            _scoped("Bonus Health Gained", "From Death Wave"),
        ),
        unit_type=UnitType.count,
    ),
    "lifesteal_healing": RawTextMetricSpec(
        selectors=(
            _legacy("Lifesteal"),
            _scoped("Health Regenerated", "Lifesteal"),
        ),
        unit_type=UnitType.count,
    ),
    "tower_health_regen": RawTextMetricSpec(
        selectors=(_scoped("Health Regenerated", "Tower Health Regen"),),
        unit_type=UnitType.count,
    ),
    "wall_health_regen": RawTextMetricSpec(
        selectors=(_scoped("Health Regenerated", "Wall Health Regen"),),
        unit_type=UnitType.count,
    ),
    "defense_percent_blocked_damage": RawTextMetricSpec(
        selectors=(_scoped("Damage Blocked", "Defense %"),),
        unit_type=UnitType.damage,
    ),
    "defense_absolute_blocked_damage": RawTextMetricSpec(
        selectors=(_scoped("Damage Blocked", "Defense Absolute"),),
        unit_type=UnitType.damage,
    ),
    "chrono_field_blocked_damage": RawTextMetricSpec(
        selectors=(_scoped("Damage Blocked", "Chrono Field"),),
        unit_type=UnitType.damage,
    ),
    "chain_thunder_blocked_damage": RawTextMetricSpec(
        selectors=(_scoped("Damage Blocked", "Chain Thunder"),),
        unit_type=UnitType.damage,
    ),
    "flame_bot_blocked_damage": RawTextMetricSpec(
        selectors=(_scoped("Damage Blocked", "Flame Bot"),),
        unit_type=UnitType.damage,
    ),
    "primordial_collapse_blocked_damage": RawTextMetricSpec(
        selectors=(_scoped("Damage Blocked", "Primordial Collapse"),),
        unit_type=UnitType.damage,
    ),
    "negative_mass_projector_blocked_damage": RawTextMetricSpec(
        selectors=(_scoped("Damage Blocked", "Negative Mass Projector"),),
        unit_type=UnitType.damage,
    ),
    "enemy_attack_levels_skipped": RawTextMetricSpec(
        selectors=(_scoped("Utility", "Enemy Attack Levels Skipped"),),
        unit_type=UnitType.count,
    ),
    "enemy_health_levels_skipped": RawTextMetricSpec(
        selectors=(_scoped("Utility", "Enemy Health Levels Skipped"),),
        unit_type=UnitType.count,
    ),
    "projectiles_count": RawTextMetricSpec(
        selectors=(_legacy("Projectiles Count"), _scoped("Counts", "Projectiles Count")),
        unit_type=UnitType.count,
    ),
    "land_mines_spawned": RawTextMetricSpec(
        selectors=(_legacy("Land Mines Spawned"), _scoped("Counts", "Land Mines Spawned")),
        unit_type=UnitType.count,
    ),
    "thunder_bot_stuns": RawTextMetricSpec(
        selectors=(_legacy("Thunder Bot Stuns"), _scoped("Counts", "Thunder Bot Stuns")),
        unit_type=UnitType.count,
    ),
    "waves_skipped": RawTextMetricSpec(
        selectors=(_legacy("Waves Skipped"), _scoped("Counts", "Waves Skipped")),
        unit_type=UnitType.count,
    ),
    "death_defy_count": RawTextMetricSpec(
        selectors=(_scoped("Counts", "Death Defy"),),
        unit_type=UnitType.count,
    ),
    "energy_shield_hits_absorbed": RawTextMetricSpec(
        selectors=(_scoped("Counts", "Hits Absorbed By Energy Shield"),),
        unit_type=UnitType.count,
    ),
    "nuke_uses": RawTextMetricSpec(
        selectors=(_scoped("Counts", "Nuke"),),
        unit_type=UnitType.count,
    ),
    "second_wind_uses": RawTextMetricSpec(
        selectors=(_scoped("Counts", "Second Wind"),),
        unit_type=UnitType.count,
    ),
    "demon_mode_uses": RawTextMetricSpec(
        selectors=(_scoped("Counts", "Demon Mode"),),
        unit_type=UnitType.count,
    ),
    "enemies_hit_by_projectiles": RawTextMetricSpec(
        selectors=(_scoped("Enemies Hit By", "Projectiles"),),
        unit_type=UnitType.count,
    ),
    "enemies_hit_by_thorns": RawTextMetricSpec(
        selectors=(_scoped("Enemies Hit By", "Thorns"),),
        unit_type=UnitType.count,
    ),
    "enemies_hit_by_orbs": RawTextMetricSpec(
        selectors=(_legacy("Enemies Hit by Orbs"), _scoped("Enemies Hit By", "Orbs")),
        unit_type=UnitType.count,
    ),
    "enemies_hit_by_death_ray": RawTextMetricSpec(
        selectors=(_scoped("Enemies Hit By", "Death Ray"),),
        unit_type=UnitType.count,
    ),
    "enemies_hit_by_chain_lightning": RawTextMetricSpec(
        selectors=(_scoped("Enemies Hit By", "Chain Lightning"),),
        unit_type=UnitType.count,
    ),
    "enemies_hit_by_smart_missiles": RawTextMetricSpec(
        selectors=(_scoped("Enemies Hit By", "Smart Missiles"),),
        unit_type=UnitType.count,
    ),
    "enemies_hit_by_inner_land_mines": RawTextMetricSpec(
        selectors=(_scoped("Enemies Hit By", "Inner Land Mines"),),
        unit_type=UnitType.count,
    ),
    "enemies_hit_by_poison_swamp": RawTextMetricSpec(
        selectors=(_scoped("Enemies Hit By", "Poison Swamp"),),
        unit_type=UnitType.count,
    ),
    "enemies_hit_by_death_wave": RawTextMetricSpec(
        selectors=(_scoped("Enemies Hit By", "Death Wave"),),
        unit_type=UnitType.count,
    ),
    "enemies_hit_by_black_hole": RawTextMetricSpec(
        selectors=(_scoped("Enemies Hit By", "Black Hole"),),
        unit_type=UnitType.count,
    ),
    "enemies_hit_by_chrono_field": RawTextMetricSpec(
        selectors=(_scoped("Enemies Hit By", "Chrono Field"),),
        unit_type=UnitType.count,
    ),
    "enemies_hit_by_land_mines": RawTextMetricSpec(
        selectors=(_scoped("Enemies Hit By", "Land Mines"),),
        unit_type=UnitType.count,
    ),
    "enemies_hit_by_thunder_bot": RawTextMetricSpec(
        selectors=(_scoped("Enemies Hit By", "Thunder Bot"),),
        unit_type=UnitType.count,
    ),
    "enemies_hit_by_flame_bot": RawTextMetricSpec(
        selectors=(_scoped("Enemies Hit By", "Flame Bot"),),
        unit_type=UnitType.count,
    ),
    "enemies_hit_by_attack_chip": RawTextMetricSpec(
        selectors=(_scoped("Enemies Hit By", "Attack Chip"),),
        unit_type=UnitType.count,
    ),
    "enemies_hit_by_orbital_augment": RawTextMetricSpec(
        selectors=(_scoped("Enemies Hit By", "Orbital Augment"),),
        unit_type=UnitType.count,
    ),
    "kills_with_golden_tower_active": RawTextMetricSpec(
        selectors=(_scoped("Killed With Effect Active", "Golden Tower"),),
        unit_type=UnitType.count,
    ),
    "kills_with_death_wave_active": RawTextMetricSpec(
        selectors=(_scoped("Killed With Effect Active", "Death Wave"),),
        unit_type=UnitType.count,
    ),
    "kills_with_spotlight_active": RawTextMetricSpec(
        selectors=(_scoped("Killed With Effect Active", "Spotlight"),),
        unit_type=UnitType.count,
    ),
    "kills_with_amplify_bot_active": RawTextMetricSpec(
        selectors=(_scoped("Killed With Effect Active", "Amplify Bot"),),
        unit_type=UnitType.count,
    ),
    "kills_with_golden_bot_active": RawTextMetricSpec(
        selectors=(_scoped("Killed With Effect Active", "Golden Bot"),),
        unit_type=UnitType.count,
    ),
    "kills_with_death_penalty_active": RawTextMetricSpec(
        selectors=(_scoped("Killed With Effect Active", "Death Penalty"),),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_basic": RawTextMetricSpec(
        selectors=(_legacy("Basic"), _scoped("Total Enemies", "Basic"), _scoped("Enemies Destroyed", "Basic")),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_fast": RawTextMetricSpec(
        selectors=(_legacy("Fast"), _scoped("Total Enemies", "Fast"), _scoped("Enemies Destroyed", "Fast")),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_tank": RawTextMetricSpec(
        selectors=(_legacy("Tank"), _scoped("Total Enemies", "Tank"), _scoped("Enemies Destroyed", "Tank")),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_ranged": RawTextMetricSpec(
        selectors=(_legacy("Ranged"), _scoped("Total Enemies", "Ranged"), _scoped("Enemies Destroyed", "Ranged")),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_boss": RawTextMetricSpec(
        selectors=(_legacy("Boss"), _scoped("Total Enemies", "Boss"), _scoped("Enemies Destroyed", "Boss")),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_protector": RawTextMetricSpec(
        selectors=(
            _legacy("Protector"),
            _scoped("Total Enemies", "Protector"),
            _scoped("Enemies Destroyed", "Protector"),
        ),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_vampires": RawTextMetricSpec(
        selectors=(
            _legacy("Vampires"),
            _scoped("Total Enemies", "Vampires"),
            _scoped("Enemies Destroyed", "Vampires"),
        ),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_rays": RawTextMetricSpec(
        selectors=(_legacy("Rays"), _scoped("Total Enemies", "Rays"), _scoped("Enemies Destroyed", "Rays")),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_scatters": RawTextMetricSpec(
        selectors=(
            _legacy("Scatters"),
            _scoped("Total Enemies", "Scatters"),
            _scoped("Enemies Destroyed", "Scatters"),
        ),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_saboteur": RawTextMetricSpec(
        selectors=(
            _legacy("Saboteur"),
            _scoped("Total Enemies", "Saboteur"),
            _scoped("Enemies Destroyed", "Saboteur"),
        ),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_commander": RawTextMetricSpec(
        selectors=(
            _legacy("Commander"),
            _scoped("Total Enemies", "Commander"),
            _scoped("Enemies Destroyed", "Commander"),
        ),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_overcharge": RawTextMetricSpec(
        selectors=(
            _legacy("Overcharge"),
            _scoped("Total Enemies", "Overcharge"),
            _scoped("Enemies Destroyed", "Overcharge"),
        ),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_by_projectiles": RawTextMetricSpec(
        selectors=(_scoped("Enemies Destroyed By", "Projectiles"),),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_by_orbs": RawTextMetricSpec(
        selectors=(
            _legacy("Destroyed By Orbs"),
            _scoped("Enemies Destroyed By", "Orbs"),
        ),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_by_thorns": RawTextMetricSpec(
        selectors=(
            _legacy("Destroyed by Thorns"),
            _scoped("Enemies Destroyed By", "Thorns"),
        ),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_by_death_ray": RawTextMetricSpec(
        selectors=(
            _legacy("Destroyed by Death Ray"),
            _scoped("Enemies Destroyed By", "Death Ray"),
        ),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_by_land_mine": RawTextMetricSpec(
        selectors=(
            _legacy("Destroyed by Land Mine"),
            _scoped("Enemies Destroyed By", "Land Mines"),
        ),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_by_chain_lightning": RawTextMetricSpec(
        selectors=(_scoped("Enemies Destroyed By", "Chain Lightning"),),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_by_smart_missiles": RawTextMetricSpec(
        selectors=(_scoped("Enemies Destroyed By", "Smart Missiles"),),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_by_inner_land_mines": RawTextMetricSpec(
        selectors=(_scoped("Enemies Destroyed By", "Inner Land Mines"),),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_by_poison_swamp": RawTextMetricSpec(
        selectors=(_scoped("Enemies Destroyed By", "Poison Swamp"),),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_by_black_hole": RawTextMetricSpec(
        selectors=(_scoped("Enemies Destroyed By", "Black Hole"),),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_by_flame_bot": RawTextMetricSpec(
        selectors=(_scoped("Enemies Destroyed By", "Flame Bot"),),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_by_other": RawTextMetricSpec(
        selectors=(_scoped("Enemies Destroyed By", "Other"),),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_in_spotlight": RawTextMetricSpec(
        selectors=(_legacy("Destroyed in Spotlight"),),
        unit_type=UnitType.count,
    ),
    "enemies_destroyed_in_golden_bot": RawTextMetricSpec(
        selectors=(_legacy("Destroyed in Golden Bot"),),
        unit_type=UnitType.count,
    ),
    "guardian_summoned_enemies": RawTextMetricSpec(
        selectors=(
            _legacy("Summoned enemies"),
            _scoped("Total Enemies", "Summoned Enemies"),
            _scoped("Guardian", "Summoned enemies"),
        ),
        unit_type=UnitType.count,
    ),
    "guardian_coins_stolen": RawTextMetricSpec(
        selectors=(
            _legacy("Guardian coins stolen"),
            _scoped("Guardian", "Guardian coins stolen"),
            _scoped("Coins", "Bounty Coins"),
        ),
        unit_type=UnitType.coins,
    ),
    "guardian_coins_fetched": RawTextMetricSpec(
        selectors=(
            _legacy("Coins Fetched"),
            _scoped("Coins", "Coins Fetched"),
            _scoped("Guardian", "Coins Fetched"),
        ),
        unit_type=UnitType.coins,
    ),
    "gems_earned": RawTextMetricSpec(
        selectors=(_scoped("Currencies", "Gems"),),
        unit_type=UnitType.count,
    ),
    "ad_gems_earned": RawTextMetricSpec(
        selectors=(_scoped("Currencies", "Ad Gems"),),
        unit_type=UnitType.count,
    ),
    "medals_earned": RawTextMetricSpec(
        selectors=(_scoped("Currencies", "Medals"),),
        unit_type=UnitType.count,
    ),
    "guardian_gems_fetched": RawTextMetricSpec(
        selectors=(
            _scoped("Currencies", "Fetch Gems"),
            _scoped("Guardian", "Gems"),
        ),
        unit_type=UnitType.count,
    ),
    "guardian_medals_fetched": RawTextMetricSpec(
        selectors=(
            _scoped("Guardian", "Medals"),
        ),
        unit_type=UnitType.count,
    ),
    "guardian_reroll_shards_fetched": RawTextMetricSpec(
        selectors=(
            _legacy("Reroll Shards"),
            _scoped("Guardian", "Reroll Shards"),
            _scoped("Currencies", "Reroll Shards Fetched"),
        ),
        unit_type=UnitType.count,
    ),
    "guardian_cannon_shards_fetched": RawTextMetricSpec(
        selectors=(
            _legacy("Cannon Shards"),
            _scoped("Guardian", "Cannon Shards"),
            _scoped("Currencies", "Cannon Shards"),
        ),
        unit_type=UnitType.count,
    ),
    "guardian_armor_shards_fetched": RawTextMetricSpec(
        selectors=(
            _legacy("Armor Shards"),
            _scoped("Guardian", "Armor Shards"),
            _scoped("Currencies", "Armor Shards"),
        ),
        unit_type=UnitType.count,
    ),
    "guardian_generator_shards_fetched": RawTextMetricSpec(
        selectors=(
            _legacy("Generator Shards"),
            _scoped("Guardian", "Generator Shards"),
            _scoped("Currencies", "Generator Shards"),
        ),
        unit_type=UnitType.count,
    ),
    "guardian_core_shards_fetched": RawTextMetricSpec(
        selectors=(
            _legacy("Core Shards"),
            _scoped("Guardian", "Core Shards"),
            _scoped("Currencies", "Core Shards"),
        ),
        unit_type=UnitType.count,
    ),
    "guardian_common_modules_fetched": RawTextMetricSpec(
        selectors=(
            _legacy("Common Modules"),
            _scoped("Guardian", "Common Modules"),
            _scoped("Currencies", "Common Modules"),
        ),
        unit_type=UnitType.count,
    ),
    "guardian_rare_modules_fetched": RawTextMetricSpec(
        selectors=(
            _legacy("Rare Modules"),
            _scoped("Guardian", "Rare Modules"),
            _scoped("Currencies", "Rare Modules"),
        ),
        unit_type=UnitType.count,
    ),
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
    for key, spec in RAW_TEXT_METRIC_SPECS.items():
        parsed = extract_numeric_value_from_selectors(
            raw_text,
            selectors=spec.selectors,
            unit_type=spec.unit_type,
        )
        if parsed is None:
            continue
        extracted[key] = parsed
    return extracted
