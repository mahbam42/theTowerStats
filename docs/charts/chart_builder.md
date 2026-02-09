# Chart Builder

This page is **User Guide**. It explains how to build and reuse custom charts.

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
6. If **Aggregation** is available, select **Sum** or **Average**.
7. (Optional) In **Step 3 — Comparison**, select a comparison mode when you want an additional line or grouping.
8. Select **Apply to dashboard** to add the custom chart to the dashboard.
9. (Optional) Use **Saved charts** to load a previously saved Chart Builder entry.
10. (Optional) Enter a name and select **Save chart builder entry** to save or update the current setup.
11. (Optional) Select **Delete saved chart** to remove a saved entry you no longer need.
12. (Optional) Select **Save snapshot** to save the current builder selections under a name.
13. (Optional) Select **Load snapshot** to restore a previously saved chart configuration.

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
- **Aggregation** controls whether per-day values are summed or averaged before charting.
- If a chart shows multiple lines, the legend describes what each line represents for the comparison you selected.
- If a chart shows gaps, at least one run in the scope is missing the underlying value for that point.
- Saved charts store your Chart Builder selections so you can reuse and adjust them later.
- The full list of metrics shared by Chart Builder and Explore is available in [Metrics Reference](../metrics_reference.md).

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
