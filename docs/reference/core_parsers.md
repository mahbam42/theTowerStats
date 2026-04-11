# Core Parsers

Developer-facing API reference for the `core.parsers` package.

## Notes

- Battle Report parsing must remain non-destructive: preserve reported values, tolerate unknown labels, and keep raw text available for later backfills.
- Newer section-based reports may be pasted with single-space separators instead of tabs; parser support should not assume wide spacing.
- Parser expansions should be paired with regression coverage and a `reparse_battle_reports` pass when stored derived metrics depend on the newly supported rows.

## v28 Alias Guide

The newer v28 Battle Report format reuses short labels across multiple sections. Parser work must map these rows by section, not by label text alone.

| Section | Report label | Metric or field |
| --- | --- | --- |
| Top-level | `Coins Per Hour` | `game_reported_coins_per_hour` |
| Top-level | `Cells Per Hour` | `game_reported_cells_per_hour` |
| Records | `Highest Coins / Minute` | `record_highest_coins_per_minute` |
| Records | `Largest Wave Skip` | `record_largest_wave_skip` |
| Damage | `Black Hole` | `black_hole_damage` |
| Damage | `Flame Bot` | `flame_bot_damage` |
| Damage | `Attack Chip` | `guardian_damage` |
| Damage Taken | `Tower` | `tower_damage_taken` |
| Damage Taken | `Wall` | `wall_damage_taken` |
| Health Regenerated | `Lifesteal` | `lifesteal_healing` |
| Damage Blocked | `Flame Bot` | `flame_bot_blocked_damage` |
| Coins | `Golden Tower` | `coins_from_golden_tower` |
| Coins | `Black Hole` | `coins_from_black_hole` |
| Coins | `Critical Coin` | `coins_from_critical_coin` |
| Coins | `Golden Combo` | `coins_from_golden_combo` |
| Cash | `Golden Tower` | `cash_from_golden_tower` |
| Currencies | `Gems` | `gems_earned` |
| Currencies | `Ad Gems` | `ad_gems_earned` |
| Currencies | `Medals` | `medals_earned` |
| Enemies Destroyed By | `Black Hole` | `enemies_destroyed_by_black_hole` |
| Enemies Destroyed By | `Other` | `enemies_destroyed_by_other` |

Parser behavior should continue to accept legacy flat labels such as `Black Hole Damage` and `Blackhole Damage` alongside these v28 section-based aliases.

## Package

::: core.parsers
    options:
      show_root_heading: true
      members: false

## Modules

::: core.parsers.battle_report
    options:
      show_root_heading: true
      members: true
