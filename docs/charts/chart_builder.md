# Chart Builder

## Overview

Chart Builder lets you create a custom chart from the available metrics and apply it to the Charts dashboard without changing any stored run data.

## When to Use This

- You want to chart a value that is not listed in the default chart list.
- You want to combine multiple related lines on one chart for comparison.
- You want to save a named snapshot so you can return to the same custom chart later.
- You want to save a reusable Chart Builder setup and edit it later.
- You want to confirm whether a metric is available before you export or compare it.

## How to Use

1. Select **Charts** in the navigation.
2. Select **Chart Builder**.
3. In **Step 1 — Metrics**, select one or more metrics to chart.
4. Review any constraint or availability messages shown for the metric selections.
5. In **Step 2 — Chart settings**, select the chart style (Line, Area, Bar, Scatter, or Donut) and the X-axis mode (**Time** or **Metric vs metric**).
6. (Optional) In **Step 3 — Comparison**, select a comparison mode when you want an additional line or grouping.
7. Select **Apply to dashboard** to add the custom chart to the dashboard.
8. (Optional) Use **Saved charts** to load a previously saved Chart Builder entry.
9. (Optional) Enter a name and select **Save chart builder entry** to save or update the current setup.
10. (Optional) Select **Delete saved chart** to remove a saved entry you no longer need.
11. (Optional) Select **Save snapshot** to save the current builder selections under a name.
12. (Optional) Select **Load snapshot** to restore a previously saved chart configuration.

### Example: Free Upgrades vs Coins Earned (Scatter)

1. Select **Charts** in the navigation.
2. Select **Chart Builder**.
3. In **Step 1 — Metrics**, select **Free Upgrades (Total)** and **Coins earned**.
4. In **Step 2 — Chart settings**, select **Scatter** and **Metric vs metric**.
5. Select **Apply to dashboard**.

## How to Read the Results

- The preview and the applied chart reflect your current Charts filters (date window, tier, preset, and other options).
- Constraint messages explain when a selection cannot be shown for the current scope (for example, missing values or not enough runs).
- **Time** uses dates or run labels on the X-axis, while **Metric vs metric** compares two selected values per run.
- If a chart shows multiple lines, the legend describes what each line represents for the comparison you selected.
- If a chart shows gaps, at least one run in the scope is missing the underlying value for that point.
- Saved charts store your Chart Builder selections so you can reuse and adjust them later.

## Metrics Reference

This table lists the metrics available in Chart Builder along with their sources and calculation notes.

| Metric key | Label | Source | Calculation | Notes |
| --- | --- | --- | --- | --- |
| black_hole_damage | Black Hole Damage | BattleReport (observed) | sum of black_hole_damage |  |
| bot_runs_count | Runs using selected bot | Planned (not yet ingested) | sum of bot_present | Run-level bot presence will be available after bot usage ingestion is implemented. |
| bot_uptime_percent | Bot uptime | Planned (not yet ingested) | avg of bot_uptime_percent | Bot uptime is planned; current bot-related values come from Battle Report metrics only. |
| cash_earned | Cash earned | BattleReport (observed) | sum of cash_earned |  |
| cash_from_golden_tower | Cash From Golden Tower | BattleReport (observed) | sum of cash_from_golden_tower | Battle Report utility breakdown: cash earned from Golden Tower. |
| cash_from_other_sources | Other cash | BattleReport (derived) | sum of cash_earned - cash_from_golden_tower - interest_earned | Residual cash not covered by named sources (derived). |
| cells_earned | Cells earned | BattleReport (observed) | sum of cells_earned |  |
| chain_lightning_damage | Chain Lightning Damage | BattleReport (observed) | sum of chain_lightning_damage |  |
| coins_earned | Coins earned | BattleReport (observed) | sum of coins_earned |  |
| coins_from_black_hole | Coins From Black Hole | BattleReport (observed) | sum of coins_from_black_hole | Battle Report utility breakdown: coins earned from Black Hole. |
| coins_from_coin_bonuses | Coins from Coin Bonuses | BattleReport (observed) | sum of coins_from_coin_bonuses | Battle Report utility breakdown: coins earned from coin bonuses. |
| coins_from_coin_upgrade | Coins from Coin Upgrade | BattleReport (observed) | sum of coins_from_coin_upgrade | Battle Report utility breakdown: coins earned from coin upgrades. |
| coins_from_death_wave | Coins From Death Wave | BattleReport (observed) | sum of coins_from_death_wave | Battle Report utility breakdown: coins earned from Death Wave. |
| coins_from_golden_tower | Coins From Golden Tower | BattleReport (observed) | sum of coins_from_golden_tower | Battle Report utility breakdown: coins earned from Golden Tower. |
| coins_from_orb | Coins From Orb | BattleReport (observed) | sum of coins_from_orb | Battle Report utility breakdown: coins earned from Orbs. |
| coins_from_other_sources | Other coins | BattleReport (observed) | sum of coins_from_other_sources | Residual coins not covered by named sources; ensures sources sum to total coins earned. |
| coins_from_spotlight | Coins From Spotlight | BattleReport (observed) | sum of coins_from_spotlight | Battle Report utility breakdown: coins earned from Spotlight. |
| coins_per_hour | Coins/hour | BattleReport (observed) | avg of coins_per_hour | Observed coins earned divided by real time (hours). |
| real_time_hours | Run duration (hours) | BattleReport (derived) | avg of real_time_seconds / 3600 | Real-time run duration converted to hours. |
| coins_per_wave | Coins per wave | BattleReport (derived) | avg of coins_earned / wave | Computed as coins earned divided by waves reached. |
| free_attack_upgrades | Free Attack Upgrade | BattleReport (observed) | sum of free_attack_upgrades | Battle Report utility breakdown: free attack upgrades. |
| free_defense_upgrades | Free Defense Upgrade | BattleReport (observed) | sum of free_defense_upgrades | Battle Report utility breakdown: free defense upgrades. |
| free_utility_upgrades | Free Utility Upgrade | BattleReport (observed) | sum of free_utility_upgrades | Battle Report utility breakdown: free utility upgrades. |
| free_upgrades_total | Free Upgrades (Total) | BattleReport (derived) | sum of free_attack_upgrades + free_defense_upgrades + free_utility_upgrades | Derived total across free upgrade types. |
| recovery_packages | Recovery Packages | BattleReport (derived) | sum of recovery_packages | Derived from the Recovery Packages line in the Battle Report. |
| cooldown_reduction_effective | Effective cooldown | Planned (not yet ingested) | avg of effective_cooldown_seconds | Ultimate Weapon cooldown reductions are planned and not populated yet. |
| damage_dealt | Damage dealt | BattleReport (observed) | sum of damage_dealt | Total damage dealt from Battle Reports. |
| death_ray_damage | Death Ray Damage | BattleReport (observed) | sum of death_ray_damage |  |
| death_wave_damage | Death Wave Damage | BattleReport (observed) | sum of death_wave_damage |  |
| electrons_damage | Electrons Damage | BattleReport (observed) | sum of electrons_damage |  |
| enemies_destroyed_basic | Basic | BattleReport (observed) | sum of enemies_destroyed_basic |  |
| enemies_destroyed_boss | Boss | BattleReport (observed) | sum of enemies_destroyed_boss |  |
| enemies_destroyed_by_death_ray | Destroyed by Death Ray | BattleReport (observed) | sum of enemies_destroyed_by_death_ray |  |
| enemies_destroyed_by_land_mine | Destroyed by Land Mine | BattleReport (observed) | sum of enemies_destroyed_by_land_mine |  |
| enemies_destroyed_by_orbs | Destroyed By Orbs | BattleReport (observed) | sum of enemies_destroyed_by_orbs |  |
| enemies_destroyed_by_thorns | Destroyed by Thorns | BattleReport (observed) | sum of enemies_destroyed_by_thorns |  |
| enemies_destroyed_commander | Commander | BattleReport (observed) | sum of enemies_destroyed_commander |  |
| enemies_destroyed_common | Enemies destroyed (common) | BattleReport (derived) | sum of common enemy counts | Derived from Basic, Fast, Ranged, Tank, and Protector counts. |
| enemies_destroyed_elite | Enemies destroyed (elite) | BattleReport (derived) | sum of elite enemy counts | Derived from Vampire, Ray, and Scatter counts. |
| enemies_destroyed_fleet | Enemies destroyed (fleet) | BattleReport (derived) | sum of fleet enemy counts | Derived from Saboteur, Commander, and Overcharge counts. |
| enemies_destroyed_fast | Fast | BattleReport (observed) | sum of enemies_destroyed_fast |  |
| enemies_destroyed_in_golden_bot | Destroyed in Golden Bot | BattleReport (observed) | sum of enemies_destroyed_in_golden_bot |  |
| enemies_destroyed_in_spotlight | Destroyed in Spotlight | BattleReport (observed) | sum of enemies_destroyed_in_spotlight |  |
| enemies_destroyed_overcharge | Overcharge | BattleReport (observed) | sum of enemies_destroyed_overcharge |  |
| enemies_destroyed_per_hour | Enemies destroyed/hour | BattleReport (derived) | avg of enemies_destroyed_total / hours | Enemies destroyed (derived total) divided by real time (hours). |
| enemies_destroyed_protector | Protector | BattleReport (observed) | sum of enemies_destroyed_protector |  |
| enemies_destroyed_ranged | Ranged | BattleReport (observed) | sum of enemies_destroyed_ranged |  |
| enemies_destroyed_rays | Rays | BattleReport (observed) | sum of enemies_destroyed_rays |  |
| enemies_destroyed_saboteur | Saboteur | BattleReport (observed) | sum of enemies_destroyed_saboteur |  |
| enemies_destroyed_scatters | Scatters | BattleReport (observed) | sum of enemies_destroyed_scatters |  |
| enemies_destroyed_tank | Tank | BattleReport (observed) | sum of enemies_destroyed_tank |  |
| enemies_destroyed_total | Enemies destroyed (derived total) | BattleReport (derived) | sum of sum(enemy_type_counts) | Derived from per-type counts; ignores game-reported totals. |
| enemies_destroyed_vampires | Vampires | BattleReport (observed) | sum of enemies_destroyed_vampires |  |
| enemies_hit_by_orbs | Enemies Hit by Orbs | BattleReport (observed) | sum of enemies_hit_by_orbs |  |
| guardian_activations_per_minute | Guardian activations/minute | Planned (not yet ingested) | avg of guardian_activations_per_minute | Guardian chip activation rates are planned and not populated yet. |
| guardian_armor_shards_fetched | Armor Shards | BattleReport (observed) | sum of guardian_armor_shards_fetched | Battle Report Guardian section: armor shards fetched. |
| guardian_cannon_shards_fetched | Cannon Shards | BattleReport (observed) | sum of guardian_cannon_shards_fetched | Battle Report Guardian section: cannon shards fetched. |
| guardian_coins_fetched | Coins Fetched | BattleReport (observed) | sum of guardian_coins_fetched | Battle Report Guardian section: coins fetched (rolls up into Coins Earned by Source). |
| guardian_coins_stolen | Guardian coins stolen | BattleReport (observed) | sum of guardian_coins_stolen | Battle Report Guardian section: coins stolen (rolls up into Coins Earned by Source). |
| guardian_common_modules_fetched | Common Modules | BattleReport (observed) | sum of guardian_common_modules_fetched | Battle Report Guardian section: common modules fetched. |
| guardian_core_shards_fetched | Core Shards | BattleReport (observed) | sum of guardian_core_shards_fetched | Battle Report Guardian section: core shards fetched. |
| guardian_damage | Guardian Damage | BattleReport (observed) | avg of guardian_damage | Battle Report Guardian section: damage dealt by the Guardian. |
| guardian_gems_fetched | Gems | BattleReport (observed) | sum of guardian_gems_fetched | Battle Report Guardian section: gems fetched. |
| guardian_generator_shards_fetched | Generator Shards | BattleReport (observed) | sum of guardian_generator_shards_fetched | Battle Report Guardian section: generator shards fetched. |
| guardian_medals_fetched | Medals | BattleReport (observed) | sum of guardian_medals_fetched | Battle Report Guardian section: medals fetched. |
| guardian_rare_modules_fetched | Rare Modules | BattleReport (observed) | sum of guardian_rare_modules_fetched | Battle Report Guardian section: rare modules fetched. |
| guardian_reroll_shards_fetched | Reroll Shards | BattleReport (observed) | sum of guardian_reroll_shards_fetched | Battle Report Guardian section: reroll shards fetched. |
| guardian_runs_count | Runs using selected guardian chip | Planned (not yet ingested) | sum of guardian_chip_present | Guardian chip presence per run is planned and not populated yet. |
| guardian_summoned_enemies | Guardian Summoned Enemies | BattleReport (observed) | avg of guardian_summoned_enemies | Battle Report Guardian section: summoned enemies count. |
| inner_land_mine_damage | Inner Land Mine Damage | BattleReport (observed) | sum of inner_land_mine_damage |  |
| interest_earned | Interest earned | BattleReport (observed) | sum of interest_earned | Observed interest earned from Battle Reports. |
| land_mine_damage | Land Mine Damage | BattleReport (observed) | sum of land_mine_damage |  |
| orb_damage | Orb Damage | BattleReport (observed) | sum of orb_damage |  |
| projectiles_damage | Projectiles Damage | BattleReport (observed) | sum of projectiles_damage |  |
| rend_armor_damage | Rend Armor Damage | BattleReport (observed) | sum of rend_armor_damage |  |
| reroll_dice_earned | Reroll dice earned | BattleReport (observed) | sum of reroll_shards_earned | Alias for reroll shards earned (legacy naming). |
| reroll_shards_earned | Reroll shards earned | BattleReport (observed) | sum of reroll_shards_earned |  |
| smart_missile_damage | Smart Missile Damage | BattleReport (observed) | sum of smart_missile_damage |  |
| swamp_damage | Swamp Damage | BattleReport (observed) | sum of swamp_damage |  |
| thorn_damage | Thorn Damage | BattleReport (observed) | sum of thorn_damage |  |
| uw_effective_cooldown_seconds | Ultimate Weapon effective cooldown | Planned (not yet ingested) | avg of uw_effective_cooldown_seconds | Ultimate Weapon cooldown metrics are planned and not populated yet. |
| uw_runs_count | Runs using selected ultimate weapon | Planned (not yet ingested) | sum of ultimate_weapon_present | Ultimate Weapon run presence is planned and not populated yet. |
| uw_uptime_percent | Ultimate Weapon uptime | Planned (not yet ingested) | avg of uw_uptime_percent | Ultimate Weapon uptime is planned and not populated yet. |
| waves_per_hour | Waves/hour | BattleReport (derived) | avg of waves_reached / hours | Observed waves reached divided by real time (hours). |
| waves_reached | Waves reached | BattleReport (observed) | avg of wave |  |

## Notes & Limitations

> **Note**
> Chart Builder only uses values that exist in your imported Battle Reports and other available selections on the Charts page.

> **Note**
> Bot, Guardian Chip, and Ultimate Weapon run-usage metrics are planned but not populated yet. For now, related totals come from Battle Report metrics where available.

> **Note**
> Saving a snapshot stores the configuration you selected. It does not store a copy of your data.

> **Caution**
> If your current scope has very few runs, some comparisons may be unavailable or hard to interpret.

## Advanced Usage

1. Use **Save snapshot** to create a small set of named custom charts you reuse often (for example, one per event, tier, or farming goal).
2. When a chart looks surprising, change only one setting at a time (a metric, a filter, or a comparison mode), then re-apply to confirm what changed.
3. Compare **Coins From Golden Tower** against **Coins earned** to see how much your total coins track Golden Tower output.
4. Compare **Free Upgrades (Total)** against **Waves reached** to see whether longer runs also include higher free upgrade totals.
