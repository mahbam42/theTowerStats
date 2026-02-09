# Metrics Reference

This page is **User Guide**. It lists the metrics available in Chart Builder and Explore.

## Overview

Metrics Reference lists the values you can chart or summarize so you can confirm what is available before building charts or queries.

## When to Use This

- You want to confirm whether a metric exists before building a chart or Explore query.
- You want to understand whether a metric is observed, derived, or planned.
- You want to compare two related metrics in Chart Builder.
- You want to reference the same metric list for Chart Builder and Explore.

## How to Use

1. Open **Charts** and select **Chart Builder**, or open **Explore**.
2. Review the metrics list below.
3. Match the metric name to the one shown in the selection list.
4. Use the Source column to confirm whether the value is observed, derived, or planned.
5. Review [Explore Breakdowns](explore_breakdowns.md) when you want to group results by a category.

## How to Read the Results

- **Metric** is the label you see in Chart Builder and Explore.
- **Key** is the Explore DSL name for the metric.
- **Source** tells you where the value comes from.
- **Notes** clarifies how a metric is grouped or labeled in the Battle Report.

### Lifetime Stats (Global Stats)

Lifetime Stats (sometimes labeled Global Stats) summarizes a fixed subset of metrics for quick totals.

Economy metrics:
- Coins Earned
- Cash Earned
- Cells Earned
- Reroll Shards Earned
- Recent Coins per Hour
- Stones Spent
- Bits Spent

Combat metrics:
- Damage Dealt
- Thorn Damage
- Enemies Destroyed
- Orb Kills
- Death Ray Kills

Utility metrics:
- Waves Completed
- Free Upgrades
- Interest Earned
- Waves Skipped

### Metrics List

| Metric | Key | Source | Notes |
| --- | --- | --- | --- |
| Black Hole Damage | black_hole_damage | Battle Report (observed) |  |
| Runs using selected bot | bot_runs_count | Planned (not yet ingested) | Run-level bot presence will be available after bot usage ingestion is implemented. |
| Bot uptime | bot_uptime_percent | Planned (not yet ingested) | Bot uptime is planned; current bot-related values come from Battle Report metrics only. |
| Cash earned | cash_earned | Battle Report (observed) |  |
| Cash From Golden Tower | cash_from_golden_tower | Battle Report (observed) | Battle Report utility breakdown: cash earned from Golden Tower. |
| Other cash | cash_from_other_sources | Battle Report (derived) | Residual cash not covered by named sources. |
| Cells earned | cells_earned | Battle Report (observed) |  |
| Cells/hour | cells_per_hour | Battle Report (derived) | Observed cells earned divided by real time (hours). |
| Chain Lightning Damage | chain_lightning_damage | Battle Report (observed) |  |
| Coins earned | coins_earned | Battle Report (observed) |  |
| Coins From Black Hole | coins_from_black_hole | Battle Report (observed) | Battle Report utility breakdown: coins earned from Black Hole. |
| Coins from Coin Bonuses | coins_from_coin_bonuses | Battle Report (observed) | Battle Report utility breakdown: coins earned from coin bonuses. |
| Coins from Coin Upgrade | coins_from_coin_upgrade | Battle Report (observed) | Battle Report utility breakdown: coins earned from coin upgrades. |
| Coins From Death Wave | coins_from_death_wave | Battle Report (observed) | Battle Report utility breakdown: coins earned from Death Wave. |
| Coins From Golden Tower | coins_from_golden_tower | Battle Report (observed) | Battle Report utility breakdown: coins earned from Golden Tower. |
| Coins From Orb | coins_from_orb | Battle Report (observed) | Battle Report utility breakdown: coins earned from Orbs. |
| Other coins | coins_from_other_sources | Battle Report (observed) | Residual coins not covered by named sources; ensures sources sum to total coins earned. |
| Coins From Spotlight | coins_from_spotlight | Battle Report (observed) | Battle Report utility breakdown: coins earned from Spotlight. |
| Coins/hour | coins_per_hour | Battle Report (observed) | Observed coins earned divided by real time (hours). |
| Run duration (hours) | real_time_hours | Battle Report (derived) | Real-time run duration converted to hours. |
| Coins per wave | coins_per_wave | Battle Report (derived) | Coins earned divided by waves reached. |
| Free Attack Upgrade | free_attack_upgrades | Battle Report (observed) | Battle Report utility breakdown: free attack upgrades. |
| Free Defense Upgrade | free_defense_upgrades | Battle Report (observed) | Battle Report utility breakdown: free defense upgrades. |
| Free Utility Upgrade | free_utility_upgrades | Battle Report (observed) | Battle Report utility breakdown: free utility upgrades. |
| Free Upgrades (Total) | free_upgrades_total | Battle Report (derived) | Derived total across free upgrade types. |
| Recovery Packages | recovery_packages | Battle Report (derived) | Derived from the Recovery Packages line in the Battle Report. |
| Effective cooldown | cooldown_reduction_effective | Planned (not yet ingested) | Ultimate Weapon cooldown reductions are planned and not populated yet. |
| Damage dealt | damage_dealt | Battle Report (observed) | Total damage dealt from Battle Reports. |
| Death Ray Damage | death_ray_damage | Battle Report (observed) |  |
| Death Wave Damage | death_wave_damage | Battle Report (observed) |  |
| Electrons Damage | electrons_damage | Battle Report (observed) |  |
| Basic | enemies_destroyed_basic | Battle Report (observed) |  |
| Boss | enemies_destroyed_boss | Battle Report (observed) |  |
| Destroyed by Death Ray | enemies_destroyed_by_death_ray | Battle Report (observed) |  |
| Destroyed by Land Mine | enemies_destroyed_by_land_mine | Battle Report (observed) |  |
| Destroyed By Orbs | enemies_destroyed_by_orbs | Battle Report (observed) |  |
| Destroyed by Thorns | enemies_destroyed_by_thorns | Battle Report (observed) |  |
| Commander | enemies_destroyed_commander | Battle Report (observed) |  |
| Enemies destroyed (common) | enemies_destroyed_common | Battle Report (derived) | Derived from Basic, Fast, Ranged, Tank, and Protector counts. |
| Enemies destroyed (elite) | enemies_destroyed_elite | Battle Report (derived) | Derived from Vampire, Ray, and Scatter counts. |
| Enemies destroyed (fleet) | enemies_destroyed_fleet | Battle Report (derived) | Derived from Saboteur, Commander, and Overcharge counts. |
| Fast | enemies_destroyed_fast | Battle Report (observed) |  |
| Destroyed in Golden Bot | enemies_destroyed_in_golden_bot | Battle Report (observed) |  |
| Destroyed in Spotlight | enemies_destroyed_in_spotlight | Battle Report (observed) |  |
| Overcharge | enemies_destroyed_overcharge | Battle Report (observed) |  |
| Enemies destroyed/hour | enemies_destroyed_per_hour | Battle Report (derived) | Derived total divided by real-time hours. |
| Protector | enemies_destroyed_protector | Battle Report (observed) |  |
| Ranged | enemies_destroyed_ranged | Battle Report (observed) |  |
| Rays | enemies_destroyed_rays | Battle Report (observed) |  |
| Saboteur | enemies_destroyed_saboteur | Battle Report (observed) |  |
| Scatters | enemies_destroyed_scatters | Battle Report (observed) |  |
| Tank | enemies_destroyed_tank | Battle Report (observed) |  |
| Enemies destroyed (derived total) | enemies_destroyed_total | Battle Report (derived) | Derived from per-type counts; ignores game-reported totals. |
| Vampires | enemies_destroyed_vampires | Battle Report (observed) |  |
| Enemies Hit by Orbs | enemies_hit_by_orbs | Battle Report (observed) |  |
| Guardian activations/minute | guardian_activations_per_minute | Planned (not yet ingested) | Guardian chip activation rates are planned and not populated yet. |
| Armor Shards | guardian_armor_shards_fetched | Battle Report (observed) | Battle Report Guardian section: armor shards fetched. |
| Cannon Shards | guardian_cannon_shards_fetched | Battle Report (observed) | Battle Report Guardian section: cannon shards fetched. |
| Coins Fetched | guardian_coins_fetched | Battle Report (observed) | Battle Report Guardian section: coins fetched (rolls up into Coins Earned by Source). |
| Guardian coins stolen | guardian_coins_stolen | Battle Report (observed) | Battle Report Guardian section: coins stolen (rolls up into Coins Earned by Source). |
| Common Modules | guardian_common_modules_fetched | Battle Report (observed) | Battle Report Guardian section: common modules fetched. |
| Core Shards | guardian_core_shards_fetched | Battle Report (observed) | Battle Report Guardian section: core shards fetched. |
| Guardian Damage | guardian_damage | Battle Report (observed) | Battle Report Guardian section: damage dealt by the Guardian. Explore and Chart Builder support Sum and Average for this metric. |
| Gems | guardian_gems_fetched | Battle Report (observed) | Battle Report Guardian section: gems fetched. |
| Generator Shards | guardian_generator_shards_fetched | Battle Report (observed) | Battle Report Guardian section: generator shards fetched. |
| Medals | guardian_medals_fetched | Battle Report (observed) | Battle Report Guardian section: medals fetched. |
| Rare Modules | guardian_rare_modules_fetched | Battle Report (observed) | Battle Report Guardian section: rare modules fetched. |
| Reroll Shards | guardian_reroll_shards_fetched | Battle Report (observed) | Battle Report Guardian section: reroll shards fetched. |
| Runs using selected guardian chip | guardian_runs_count | Planned (not yet ingested) | Guardian chip presence per run is planned and not populated yet. |
| Guardian Summoned Enemies | guardian_summoned_enemies | Battle Report (observed) | Battle Report Guardian section: summoned enemies count. Explore and Chart Builder support Sum and Average for this metric. |
| Inner Land Mine Damage | inner_land_mine_damage | Battle Report (observed) |  |
| Interest earned | interest_earned | Battle Report (observed) | Observed interest earned from Battle Reports. |
| Land Mine Damage | land_mine_damage | Battle Report (observed) |  |
| Orb Damage | orb_damage | Battle Report (observed) |  |
| Projectiles Damage | projectiles_damage | Battle Report (observed) |  |
| Rend Armor Damage | rend_armor_damage | Battle Report (observed) |  |
| Reroll dice earned | reroll_dice_earned | Battle Report (observed) | Alias for reroll shards earned (legacy naming). |
| Reroll shards earned | reroll_shards_earned | Battle Report (observed) |  |
| Reroll shards/hour | reroll_shards_per_hour | Battle Report (derived) | Observed reroll shards earned divided by real time (hours). |
| Smart Missile Damage | smart_missile_damage | Battle Report (observed) |  |
| Swamp Damage | swamp_damage | Battle Report (observed) |  |
| Thorn Damage | thorn_damage | Battle Report (observed) |  |
| Ultimate Weapon effective cooldown | uw_effective_cooldown_seconds | Planned (not yet ingested) | Ultimate Weapon cooldown metrics are planned and not populated yet. |
| Runs using selected ultimate weapon | uw_runs_count | Planned (not yet ingested) | Ultimate Weapon run presence is planned and not populated yet. |
| Ultimate Weapon uptime | uw_uptime_percent | Planned (not yet ingested) | Ultimate Weapon uptime is planned and not populated yet. |
| Waves/hour | waves_per_hour | Battle Report (derived) | Waves reached divided by real-time hours. |
| Waves reached | waves_reached | Battle Report (observed) |  |

## Notes & Limitations

> Note
> Planned metrics appear in selection lists but remain empty until the related ingestion is implemented.

> Note
> Derived metrics are calculated from values in your Battle Reports. If a source value is missing, the derived metric may be blank.

> Note
> Some metrics are grouped under a broader label in the Battle Report. The Notes column calls out those groupings.

> Note
> Chart Builder and Explore only use the data you have imported.
