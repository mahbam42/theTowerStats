# Charts: Compare

## Overview

Compare lets you review differences between two scopes of runs on the Charts dashboard. It helps you understand how results change across two groups or windows.

## When to Use This

- You want to compare two groups of runs side by side.
- You want to compare two date windows.
- You want a summary table focused on a specific metric category.

## How to Use

1. Select **Charts** in the navigation.
2. Select **Compare** to expand the comparison panel.
3. Select **Summary focus** to choose the category you want to emphasize.
4. (Optional) Enable **Average each scope** to compare per-run averages instead of totals.
5. Select multiple runs in **Scope A runs** and **Scope B runs**.
6. Use **Last 3**, **Last 10**, or **Clear** to adjust the selection quickly.
7. Use the **Tier** dropdown to select all runs that match a tier or preset.
8. Confirm each run entry by its tier, wave, date, and time.
9. Select **Compare** to view the delta summary and any available Advice.

## How to Read the Results

- The summary table compares the two scopes using the selected focus category.
- Each metric row shows baseline and comparison values along with the delta.
- When **Average each scope** is enabled, values are per-run averages; otherwise they are totals for the scope.
- When a scope has too few runs, the panel reports insufficient data.
- A warning appears when the two scopes are very different in size.

## Notes & Limitations

> **Caution**
> Advice summaries require at least 3 runs in each scope unless **Average each scope** is enabled. When averaging, single-run scopes are allowed but can be noisy.

> **Note**
> Goal-aware summaries in Compare are available only when Summary focus is set to **Economy**.

> **Note**
> Percent changes cannot be calculated when a baseline average is zero.

> **Note**
> When scope sizes differ widely, Compare highlights the mismatch so you can refine your selection.

> **Note**
> Averages help reduce skew when the two scopes have different run counts.
