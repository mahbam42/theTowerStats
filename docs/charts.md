# Charts

## Overview

Charts help you review how your run results change over time using the same values stored from your imported Battle Reports, including custom charts you build from a limited set of options. For custom charts, see [Chart Builder](charts/chart_builder.md).

## When to Use This

- You want to see whether a value is trending up or down across recent runs.
- You want to compare results across tiers or preset labels.
- You want to review resource outcomes (coins, cash, cells, reroll shards) without scanning a table.
- You want a daily view that smooths out run-to-run variability.
- You want to build a chart that is not in the default list, using only registered metrics.
- You want to save a named snapshot to revisit the same chart and filters later.

## How to Use

1. Select **Charts** in the navigation.
2. (Optional) Select **Show walkthrough** when available to see a guided tour of the dashboard.
3. In **Context**, review the **Start** and **End** dates. The app defaults to the current in-game Event window (14 days).
  A. Select **Previous**, **Next**, or **All** to change the date window.
4. In **Context**, review **Granularity**. It defaults to **By battle log**, and you can switch to **By date** when needed.
5. In **Context**, select a **Tier or Tournament** and **Preset** to narrow the scope.
  A. Choose a tournament rank when you want only that tournament bracket.
  B. Toggle **Include tournaments** to include tournament runs in the charts.
6. (Optional) In **Context**, select a **Snapshot** or enter **Past N runs** to tighten the scope.
7. Select **Apply** to refresh the dashboard.
8. Select **Query Explorer** to open Explore with your current scope.


* Open **More options** to refine charts, windowing, and item filters. For details, see [More Options](charts/more_options.md).
* In **More options**, hold **Ctrl** (Windows) or **Cmd** (Mac) to select multiple charts in the chart list.
* Open **Advanced analysis** to configure Advice, Goal-aware comparison, or derived metric export. For details, see [Advanced Analysis](charts/advanced_analysis.md).
* Use **Chart Builder** to create a custom chart and apply it to your dashboard. For the full workflow, see [Chart Builder](charts/chart_builder.md).
* Select **Full screen** to view a single chart in a larger, focused modal.
* Select **Download PNG** on a chart to save an image of the chart as currently displayed.
* Select a chart tooltip to open the Battle Report Modal for that run. The linked chart opens with the full date range and preserves your current filters so you can see data immediately. For details, see [Battle Report Modal](battle_report_modal.md).
* Open **Compare** to compare two scopes of runs. For details, see [Compare](charts/compare.md).
* Open **Quick import** to paste a Battle Report without leaving the Charts page.
  * In **Quick import**, enable **Tournament run** when the run was a tournament round. The app cannot detect tournament runs automatically from pasted text.

## How to Read the Results

- The scope summary shows **Runs in scope** so you can confirm how many runs are included before you interpret a chart.
- The **Why am I seeing this?** panel explains what your current filters include or exclude and how values are grouped.
- The x-axis shows either dates or individual runs, based on the **Granularity** selection.
- When you use **By battle log** and multiple runs share the same date, the x-axis label adds a Run number so each run stays distinct.
- Run numbers are based on your own run history and do not use a global counter.
- The y-axis shows the value for the selected chart, using the unit shown in the chart title.
- Charts are grouped by domain:
  - **Economy** shows what your run produced (coins, cash, cells, reroll shards).
  - **Damage** shows where damage came from.
  - **Enemy Destruction** shows what actually killed enemies.
  - **Efficiency** shows time-normalized rates (per hour).
- For per-hour charts (such as coins/real hour), the rate uses the run’s **Real Time** duration as reported in the Battle Report.
- Snapshot filters apply alongside date ranges and other scope controls, so you can combine them.
- When a chart includes multiple lines, each line label tells you what group it represents (for example, a tier or a preset label).
- If a value is missing in the underlying Battle Report, the chart may show a gap for that date.
- Scatter charts compare two values per run. Each dot represents a single run in your current filters.
- Area charts emphasize momentum over time by shading the space under the line.
- For donut charts, each slice represents the total for that value within your current filters, and the label includes the percent of the donut total. A slice named “Other coins” groups any remaining coins that are not listed as a named source.
- For **Free Upgrades by Run**, the **Total** badge confirms that hovering a bar shows the total of Attack, Defense, and Utility upgrades.
- **Free Upgrades vs Coins Earned** compares total free upgrades to coins earned for each run.
- If a point is flagged, the tooltip includes a short reason that explains the signal.
- Advanced analysis sections summarize observed differences using the snapshots you selected and the current filters you applied. They describe the basis and limitations and do not recommend actions.
- Goal-aware comparisons report a weighted percent-change index across multiple metrics. A positive value means the selected metrics increased, after applying your selected weights.
- Compare results summarize two scopes. When you select multiple runs per scope, the Compare output includes a summary table for the selected **Summary focus** and omits metrics that do not have enough samples.

## Notes & Limitations

> **Note**
> Charts use only the data you have imported. If you have not imported runs for a date range, the chart cannot display values for that period.

> **Note**
> If a Battle Report does not include a Battle Date, charts place the run using the time you imported the report.

> **Note**
> Exports are snapshots of what you are viewing. They do not update after download.

> **Note**
> CSV export includes derived metrics only. If your current selection contains no derived charts, the export will be empty or unavailable.

> **Note**
> PNG export downloads a chart image as currently displayed, including your current filters and chart options.

> **Note**
> Large values in charts are abbreviated in axes and tooltips (K, M, B, T, q, Q). Exports keep the full numeric values.

> **Caution**
> Some charts require additional selections. For example, “Runs Using Selected UW” needs an Ultimate Weapon selection.

> **Note**
> The walkthrough button appears only during demo mode or on your first login. Selecting “Don’t show again” hides it for this browser.

> **Note**
> Moving averages change what you see on the chart, but they do not change your stored data.

> **Note**
> Per-hour metrics use “Real Time” from each imported Battle Report. In-game seconds (such as cooldowns) are a different time scale and come from reference tables.

> **Note**
> Cash represents in-run purchasing power. It resets every run, does not persist, and is not directly comparable to coins.

> **Caution**
> Enemy totals shown in the Battle Report are not used. Enemy Destruction charts derive totals by summing the per-type rows, which may not match the game’s “Total Enemies” and “Total Elites” lines.

> **Note**
> Snapshots are saved as named references and are not editable after creation.

> **Note**
> Snapshots are disabled while Demo Data is active.

> **Caution**
> Advice summaries require at least 3 runs in each scope. If either scope is thin or empty, the Advice section will show “Insufficient data”.

> **Note**
> Goal-aware summaries in Compare are available only when the Summary focus is set to **Economy**.

> **Note**
> Goal-aware summaries use percent changes. If a baseline average is zero, a percent change cannot be calculated for that metric.

> **Caution**
> Data quality flags are advisory signals. They do not change values, and they do not block chart rendering.

## Advanced Usage

1. Select a comparison chart (for example, “Coins Earned (Compare Tiers)”).
2. Select **Tier** or **Preset** filters only when you want to narrow the comparison set.
3. Review the legend to confirm which lines correspond to which groups.
4. Load a previously saved custom chart snapshot using **Chart Builder**. For steps, see [Chart Builder](charts/chart_builder.md).
5.  Use **Compare** when you want to compare two groups of runs directly. For steps, see [Compare](charts/compare.md).
