# Explore

This page is **User Guide**. It explains how to run Explore queries and read the results.

## Overview

Explore helps you build your own questions about past runs and see aggregated answers without changing Battle History.

## When to Use This

- You want to summarize results across many runs without adding columns.
- You want to group outcomes by tier, preset, or death cause.
- You want to check how a single metric varies by a chosen breakdown.
- You want to reuse a saved query for the same scope later.

## How to Use

1. Select **Explore** in the navigation.
2. Review the Query Builder text area at the top of the page.
3. Use the Saved query dropdown to load a built-in query such as Farming Efficiency by Tier.
4. Review the [Metrics Reference](metrics_reference.md) to see the full list of metrics shared with Chart Builder.
5. Review [Explore Breakdowns](explore_breakdowns.md) when you want to group results by a category.
6. Review the [Explore DSL](explore_dsl.md) reference if you want the full syntax list.
7. Enter a name on the first line so you can save or edit the query later.
8. Review the Scope lines and replace any placeholders with real values when needed.
9. Use all or * when you want a scope line to stay open.
10. Add Filter lines to narrow the runs in scope.
11. Add a Patch boundary filter when you want to limit results to one or more patch windows.
12. To exclude tournaments, add not tournament to the Tier scope line.
13. To exclude specific dates, add not followed by one or more ISO dates on the date scope line.
14. To include presets by name, list one or more preset names on the preset scope line.
15. To exclude presets by name, add not followed by one or more preset names on the preset scope line.
16. Add a Breakdown line to group results.
17. Add a Metric line and an Aggregation.
18. Add an Output line when you want a chart or KPI.
19. Select **Run query**.

## How to Read the Results

- **Runs in scope** tells you how many runs were included before aggregation.
- **Runs counted** shows how many runs contributed values within each row, with a marker when metrics use different counts.
- **Breakdowns** define the groups you are comparing.
- **Sum** adds the selected metric across runs in each group.
- **Count** shows how many runs contributed a value to each group.
- **Average** shows the per-run mean for the selected metric within each group.
- **Percent of total** shows each group as a share of the total across the current breakdown.
- The table always shows the grouped totals for your query.
- Bar and donut charts repeat the same totals as the table, grouped by your breakdown.
- Donut charts show percent contribution, not raw totals.
- Farming Efficiency by Tier adds a summary of the best observed tier, the plateau point, and any warnings.

## Notes & Limitations

> ⚠️ Note
> Explore only uses data you have imported. Missing values appear as warnings and can reduce the counts shown.

> ⚠️ Note
> Explore does not change Battle History, add columns, or fill in missing values.

> ⚠️ Note
> Queries are player-scoped. Results are based only on your own runs.

> ⚠️ Note
> Average is available only for currency, counter, and time metrics.

> ⚠️ Note
> Percent of total uses the current breakdown total and shows blank values when the total is zero.

> ⚠️ Note
> Multi-metric queries are displayed in tables only. Charts and KPI outputs require a single metric.

> ⚠️ Note
> Farming efficiency summaries describe observed results only and do not provide recommendations.

> ⚠️ Note
> Farming efficiency summaries use the first metric in the query as the primary metric, even when secondary metrics are included.

> ⚠️ Note
> Placeholders are shown in brackets to indicate a required format, such as a date or tier. Replace them with real values when you want to narrow the scope.

> ⚠️ Note
> The app excludes tournament runs by default. Adding not tournament makes the exclusion explicit in the query.

> ⚠️ Note
> Patch boundary filters include runs between the selected patch date and the next boundary date.

> ⚠️ Note
> Date exclusions must use ISO format (YYYY-MM-DD).

> ℹ️ Note
> A full syntax reference is available in the [Explore DSL](explore_dsl.md) developer documentation.
