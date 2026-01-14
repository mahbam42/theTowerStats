# Battle Report Modal

## Overview

The Battle Report Modal lets you view the full raw report for a single run while keeping a quick list of key metrics, so you can review exact values without leaving your current page.

## When to Use This

- You want to confirm a run’s raw Battle Report without re-importing it.
- You want to step through runs in the current sort order or chart sequence.
- You want to jump from a single metric to its corresponding chart.

## How to Use

1. Select a run row in Battle History to open the Battle Report Modal.
2. In Charts, select a chart tooltip to open the same modal for that run.
3. Select Previous or Next to move through runs in the current order.
4. Select a metric label to open its related chart.
5. Review the raw report content in the Raw Battle Report section.

## How to Read the Results

- The header shows the run timestamp and run identifier.
- The Metrics section lists key values from the report; metric labels link to charts when available.
- The Raw Battle Report section preserves the original report layout and spacing.
- Missing values display as an em dash so you can see where the report did not include a value.
- When the report lacks a Battle Date, the header uses the import timestamp and marks it as **Imported**.
- Large values are abbreviated in the Metrics list using the same unit formatting as Charts and Battle History.

## Notes & Limitations

> ⚠️ Note
> Navigation follows the current sorting and filters from Battle History or the current order on the chart.

> ⚠️ Note
> Imported timestamps use UTC.

> ⚠️ Note
> Some report keys do not have a matching chart. Those values appear without links.

> ⚠️ Note
> Metric links open Charts with the full date range and preserve your current filters when available.

> ⚠️ Note
> The modal shows raw report text as imported. It does not correct or infer missing values.
