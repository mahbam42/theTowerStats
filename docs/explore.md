# Explore

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
3. Enter a name on the first line so you can save or edit the query later.
4. Review the Scope lines and replace any placeholders with real values when needed.
5. Use all or * when you want a scope line to stay open.
6. Add Filter lines to narrow the runs in scope.
7. To exclude tournaments, add not tournament to the Tier scope line.
8. To exclude specific dates, add not followed by one or more ISO dates on the date scope line.
9. To include presets by name, list one or more preset names on the preset scope line.
10. To exclude presets by name, add not followed by one or more preset names on the preset scope line.
11. Add a Breakdown line to group results.
12. Add a Metric line and an Aggregation.
13. Add an Output line when you want a chart or KPI.
14. Select **Run query**.

## How to Read the Results

- **Runs in scope** tells you how many runs were included before aggregation.
- **Breakdowns** define the groups you are comparing.
- **Sum** adds the selected metric across runs in each group.
- **Count** shows how many runs contributed a value to each group.
- The table always shows the grouped totals for your query.
- Bar and donut charts repeat the same totals as the table, grouped by your breakdown.
- Donut charts show percent contribution, not raw totals.

## Notes & Limitations

> ⚠️ Note
> Explore only uses data you have imported. Missing values appear as warnings and can reduce the counts shown.

> ⚠️ Note
> Explore does not change Battle History, add columns, or fill in missing values.

> ⚠️ Note
> Queries are player-scoped. Results are based only on your own runs.

> ⚠️ Note
> Placeholders are shown in brackets to indicate a required format, such as a date or tier. Replace them with real values when you want to narrow the scope.

> ⚠️ Note
> The app excludes tournament runs by default. Adding not tournament makes the exclusion explicit in the query.

> ⚠️ Note
> Date exclusions must use ISO format (YYYY-MM-DD).

> ℹ️ Note
> A full syntax reference is available in the [Explore DSL](explore_dsl.md) developer documentation.
