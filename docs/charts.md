# Charts

## Overview

Charts help you review how your run results change over time using the same values stored from your imported Battle Reports, including custom charts you build from a limited set of options.

## When to Use This

- You want to see whether a value is trending up or down across recent runs.
- You want to compare results across tiers or preset labels.
- You want to review resource outcomes (coins, cash, cells, reroll shards) without scanning a table.
- You want a daily view that smooths out run-to-run variability.
- You want to build a chart that is not in the default list, using only registered metrics.
- You want to save a named snapshot to revisit the same chart and filters later.

## How to Use

1. Select **Charts** in the navigation.
2. Select one or more items in **Charts** to choose what you want to display.
3. Select a **Start date** and **End date** to limit the time window.
4. Select a **Tier** to focus on a single tier.
5. Select a **Preset** to focus on runs tagged with that preset label.
6. (Optional) Select a **Moving average window** to smooth the displayed line.
7. Select **Apply** to refresh the dashboard.
8. (Optional) Select **Chart Builder** to create a custom chart.
9. In **Chart Builder**, select **Metrics**, then select a **Chart type** and **Group by** option.
10. (Optional) In **Chart Builder**, select a **Comparison** mode to compare two runs or two date windows.
11. Select **Apply to dashboard** to add the custom chart to the dashboard.
12. (Optional) In **Chart Builder**, enter a **Snapshot name**, then select **Save snapshot**.

## How to Read the Results

- The x-axis shows dates from your imported runs.
- The y-axis shows the value for the selected chart, using the unit shown in the chart title.
- When a chart includes multiple lines, each line label tells you what group it represents (for example, a tier or a preset label).
- If a value is missing in the underlying Battle Report, the chart may show a gap for that date.
- For donut charts, each slice represents the total for that value within your current filters. A slice named “Other coins” groups any remaining coins that are not listed as a named source.
- If a point is flagged, the tooltip includes a short reason that explains the signal.
- The Advice section summarizes an observed comparison when you use the Compare controls. It describes the basis and limitations and does not recommend actions.

## Notes & Limitations

> **Note**
> Charts use only the data you have imported. If you have not imported runs for a date range, the chart cannot display values for that period.

> **Caution**
> Some charts require additional selections. For example, “Runs Using Selected UW” needs an Ultimate Weapon selection.

> **Note**
> Moving averages change what you see on the chart, but they do not change your stored data.

> **Note**
> Snapshots are saved as named references and are not editable after creation.

> **Caution**
> Data quality flags are advisory signals. They do not change values, and they do not block chart rendering.

## Advanced Usage

1. Select a comparison chart (for example, “Coins Earned (Compare Tiers)”).
2. Select **Tier** or **Preset** filters only when you want to narrow the comparison set.
3. Review the legend to confirm which lines correspond to which groups.
4. Select **Chart Builder**, then select **Load snapshot** to apply a previously saved snapshot.
