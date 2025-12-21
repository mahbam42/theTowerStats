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
2. In **Context**, select a **Start** and **End** date to limit the time window.
3. In **Context**, select a **Tier** and **Preset** to narrow the scope.
4. Select **Apply** to refresh the dashboard.
5. (Optional) Open **More options** to select one or more items in **Charts**.
6. (Optional) In **More options**, select a **Rolling window** and **Rolling window size**.
7. (Optional) In **More options**, select **Ultimate Weapon**, **Guardian Chip**, or **Bot** to narrow the scope to runs where that item appears.
8. (Optional) In **More options**, select a **Moving average window** to smooth the displayed line.
9. (Optional) Open **Advanced analysis** to configure **Advice** and **Goal-aware comparison**.
10. (Optional) In **Advanced analysis**, select **Snapshot A** and an advice comparison mode.
11. (Optional) In **Advanced analysis**, adjust goal weights when a weighted summary is needed.
12. (Optional) In **Advanced analysis**, select **Export derived metrics (CSV)** to download a snapshot of derived chart values.
13. (Optional) Select **Chart Builder** to open the chart builder modal.
14. In **Chart Builder**, complete **Step 1 — Metrics** and review the constraint messages when present.
15. In **Chart Builder**, complete **Step 2 — Chart settings** and (optional) **Step 3 — Comparison**.
16. In **Chart Builder**, select **Apply to dashboard** to add the custom chart to the dashboard.
17. (Optional) Select **Download PNG** on a chart to save an image of the chart as currently displayed.
18. (Optional) Open **Compare** to run the separate compare workflow.
19. (Optional) Open **Quick import** to paste a Battle Report without leaving the Charts page.

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
