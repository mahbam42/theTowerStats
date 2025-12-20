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
7. (Optional) Select **Snapshot A** in the **Advice** section to compare a saved snapshot with your current filters.
8. (Optional) Select **Compare** in the **Advice** section to choose **Snapshot vs current filters** or **Snapshot vs snapshot**.
9. (Optional) If you selected **Snapshot vs snapshot**, select **Snapshot B**.
10. (Optional) In **Goal-aware comparison**, select a **Goal** to choose a preset set of weights.
11. (Optional) In **Goal-aware comparison**, edit the **Weight** values if you want to change how the percent-change summary is calculated.
12. Select **Apply** to refresh the dashboard.
13. (Optional) Select **Export derived metrics (CSV)** to download a snapshot of derived chart values.
14. (Optional) Select **Download PNG** on a chart to save an image of the chart as currently displayed.
15. (Optional) In the **Filters** panel, select **Chart Builder** to open the chart builder panel.
16. In **Chart Builder**, select **Metrics**, then select a **Chart type** and **Group by** option.
17. (Optional) In **Chart Builder**, select a **Comparison** mode to compare two runs or two date windows.
18. Select **Apply to dashboard** to add the custom chart to the dashboard.
19. (Optional) In **Chart Builder**, in **Snapshots**, enter a **Snapshot name**.
20. (Optional) In **Chart Builder**, in **Snapshots**, select a **Snapshot target** to choose where you plan to use the snapshot.
21. (Optional) In **Chart Builder**, in **Snapshots**, select **Save snapshot**.

## How to Read the Results

- The x-axis shows dates from your imported runs.
- The y-axis shows the value for the selected chart, using the unit shown in the chart title.
- When a chart includes multiple lines, each line label tells you what group it represents (for example, a tier or a preset label).
- If a value is missing in the underlying Battle Report, the chart may show a gap for that date.
- For donut charts, each slice represents the total for that value within your current filters. A slice named “Other coins” groups any remaining coins that are not listed as a named source.
- If a point is flagged, the tooltip includes a short reason that explains the signal.
- The Advice section summarizes observed differences using the snapshots you selected and the current filters you applied. It describes the basis and limitations and does not recommend actions.
- The Goal-aware comparison summary is a weighted percent-change index across multiple metrics. A positive value means the selected metrics increased, after applying your selected weights.

## Notes & Limitations

> **Note**
> Charts use only the data you have imported. If you have not imported runs for a date range, the chart cannot display values for that period.

> **Note**
> Exports are snapshots of what you are viewing. They do not update after download.

> **Note**
> CSV export includes derived metrics only. If your current selection contains no derived charts, the export will be empty or unavailable.

> **Note**
> PNG export downloads a chart image as currently displayed, including your current filters and chart options.

> **Caution**
> Some charts require additional selections. For example, “Runs Using Selected UW” needs an Ultimate Weapon selection.

> **Note**
> Moving averages change what you see on the chart, but they do not change your stored data.

> **Note**
> Snapshots are saved as named references and are not editable after creation.

> **Note**
> Snapshots are disabled while Demo Data is active.

> **Caution**
> Advice summaries require at least 3 runs in each scope. If either scope is thin or empty, the Advice section will show “Insufficient data”.

> **Note**
> Goal-aware summaries use percent changes. If a baseline average is zero, a percent change cannot be calculated for that metric.

> **Caution**
> Data quality flags are advisory signals. They do not change values, and they do not block chart rendering.

## Advanced Usage

1. Select a comparison chart (for example, “Coins Earned (Compare Tiers)”).
2. Select **Tier** or **Preset** filters only when you want to narrow the comparison set.
3. Review the legend to confirm which lines correspond to which groups.
4. Select **Chart Builder**, then select **Load snapshot** to apply a previously saved snapshot.
