# Ultimate Weapons

## Overview

The Ultimate Weapons page helps you track which Ultimate Weapons you have unlocked, how far each upgrade parameter has progressed, and how often each weapon appears in your imported Battle Reports. Ultimate Weapon names and descriptions are based on the [Ultimate Weapons](https://the-tower-idle-tower-defense.fandom.com/wiki/Ultimate_Weapons) page on the The Tower Idle Tower Defense Fandom Wiki (external).

## When to Use This

- You want to confirm which Ultimate Weapons are unlocked in your tracker.
- You want to record upgrade progress for a weapon’s three parameters.
- You want to compare total Stones invested across different Ultimate Weapons.
- You want to review whether a weapon appears in your imported runs.
- You want to view a descriptive sync graph for Golden Tower, Black Hole, and Death Wave based on your saved cooldown values, plus duration values for Golden Tower and Black Hole.
- You want to include Golden Bot timing in the same sync graph when you track Golden Bot cooldown and duration.

## How to Use

1. Select **Ultimate Weapons** in the navigation.
2. Select **Show** to filter to **Unlocked only** or **Locked only**.
3. Review a weapon’s **Status** to confirm whether it is unlocked.
4. (Optional) Select **Wiki** next to a weapon name to open its external wiki page.
5. Select **Unlock** on a locked weapon to mark it as unlocked in the app.
6. Select **Details** on an unlocked weapon to view its three upgrade parameters.
7. Select **Level Up** on a parameter to increase its level by 1.
8. Select **Level Down** on a parameter to reduce its level by 1.
9. Review **Total Stones invested** to compare overall investment between weapons.
10. (Optional) View the **Sync graph** section to see when Golden Tower, Black Hole, and Death Wave are active at the same time.
11. (Optional) Select a saved snapshot in **Ultimate Weapons snapshot** to render a chart above the table.

## How to Read the Results

- **Total Stones invested** is the sum of the upgrade costs for the levels you have increased in the app.
- **Runs used (observed)** counts how many of your imported Battle Reports show evidence of that Ultimate Weapon being active.
- **Level** is your saved upgrade level for that parameter.
- **Current** is the current raw value for your saved level.
- **Next** shows the next-level value, with the change emphasized in parentheses when it can be parsed.
- **Cost** shows the next-level upgrade cost (informational only).
- **MAX** indicates the parameter has reached the highest known level and cannot be increased further in the app.
- In the **Sync graph**, each row shows that weapon’s activation schedule within the displayed horizon.
    - Each colored block represents a time window where that weapon is active.
    - The **All overlap** row shows time windows where all modeled rows are active at the same time.
    - The first activation begins after the first cooldown completes. Rows do not start at 0 seconds.
    - In the **Sync graph**, **Death Wave** is shown as a short activation marker. Its on-map persistence can vary and is not modeled. Cumulative overlap excludes Death Wave.
- The **Ultimate Weapons snapshot** chart shows the metric(s) saved in the selected snapshot, using the snapshot’s saved filters.

## Notes & Limitations

> **Note**
> Upgrades currently assume sufficient Stones. Costs are informational only, and the app does not check affordability.

> **Note**
> Locked weapons do not display parameter rows until they are unlocked in the app.

> **Note**
> **Level Down** is available as a safety option if you accidentally record an upgrade you did not intend.

> **Caution**
> If no Battle Reports have been imported yet, **Runs used (observed)** will show “No battles recorded yet”.

> **Caution**
> **Runs used (observed)** is based on what appears in your imported Battle Reports. Some game effects (such as Perks) can temporarily enable an Ultimate Weapon for a single run, so this count may include runs where the weapon is not permanently unlocked.

> **Note**
> Runs used (observed) is detected from specific Battle Report rows and requires a value greater than 0. For example, Black Hole uses “Black Hole Damage” and Golden Tower uses “Coins From Golden Tower”.

> **Caution**
> Some Battle Report rows can be affected by other game effects. This can create false positives in Runs used (observed). For example, Spotlight can fire missiles that may be recorded under Smart Missiles, and the Space Displacer module can deploy Inner Land Mines even if Inner Land Mines is not unlocked.

> **Note**
> Chrono Field does not currently have a reliable Battle Report row for activity detection, so Runs used (observed) may remain 0 even when it is active in the game.

> **Caution**
> If an Ultimate Weapon’s upgrade parameters are incomplete or not recognized, it may not appear on this page until the underlying data is available.

> **Note**
> The Sync graph is descriptive. It uses your saved cooldown and duration values where available and does not include run-by-run timing or recommendations. When Golden Bot timing is available, the graph includes Golden Bot and updates overlap accordingly.

> **Note**
> Death Wave is shown as a short activation marker so that it can be included in the Sync graph. The game does not provide a duration value for Death Wave, and its persistence depends on what it hits.

> **Note**
> The Sync graph uses the same cooldown and duration values shown in each weapon’s **Details** rows.

> **Caution**
> Cooldown and duration values are based on external wiki tables and are shown in seconds. Wiki values can be inaccurate or drift over time.

> **Note**
> Ultimate Weapons snapshots are created from the **Charts** page by saving a snapshot and selecting **Ultimate Weapons** as the snapshot target.

## Advanced Usage

1. Select **Unlocked only** to review only the weapons you actively track.
2. Select **Locked only** to focus on the remaining weapons not yet unlocked in the app.
