
# Table of Contents

1.  [Fix Advice Limits](#orgd0a65f7)
2.  [Advice — expand and formalize](#org9c9b0e1)
3.  [Comparison / Scenario View + reusable Snapshots](#org2e320c1)
4.  [Open analysis/context feature gaps](#org9261a36)
5.  [Test taxonomy and marker enforcement](#orgf649ce4)


<a id="orgd0a65f7"></a>

# TODO Fix Advice Limits (Compare → Advice-capable scopes)

## Problem

* Charts dashboard “Compare” allows only Run A vs Run B, but Advice requires ≥3 runs per scope, so run-vs-run comparisons always produce “Insufficient data”.

## Goal

* Make the “Compare” workflow support multi-run Scope A vs Scope B so Advice (including goal-aware mode) can be generated from those scopes.

## Non-goals

* No prescriptive recommendations.
* No new analysis math beyond summarizing existing derived metrics.

## UI/UX Requirements

* In dashboard.html, update the “Compare” section to support:
    * Scope A runs: multi-select list of runs.
    *   Scope B runs: multi-select list of runs.
    * Keep existing window-vs-window fields (date windows) as an alternative path.
* Add help text: “Advice requires at least 3 runs in each scope.”
* Add quick actions (buttons) to populate Scope A/B by tier (and optionally “last N runs”) without manual selection.
* Keep the existing single-run selectors as a fallback, but they should clearly indicate that advice won’t summarize single-run comparisons.

## View Wiring

* In views.py, extend ComparisonForm consumption so _build_comparison_result(...) can produce a comparison result from:
    * run-set vs run-set (preferred when provided),
    * window vs window,
    * run vs run (existing).
* The comparison result payload should include run counts for each scope so advice.py can apply the same insufficiency logic deterministically.

## Advice Alignment (Goal-aware)

* Reuse existing goal-aware plumbing and types in advice.py:
* Build GoalScopeSample for Scope A and Scope B using existing derived metrics (coins/hour, coins/wave, waves reached).
* Use existing weight parsing already on the dashboard (goal_intent + per-weight query params) and call generate_goal_weighted_advice(...) for compare scopes the same way snapshots do.
* Ensure all generated items pass _assert_non_prescriptive(...).

## Acceptance Criteria

* Selecting ≥3 runs in each scope produces:
* A deterministic delta summary (coins/hour at minimum).
* A goal-aware summary item (weighted percent index) using the existing goal weights.
* Selecting <3 runs in either scope produces a single, clear “Insufficient data” item with basis/context/limitations.
* Ordering of advice items is stable for the same inputs.

## Tests

* Update/add Django tests in test_dashboard_view.py:
* Multi-run scope compare generates a non-empty advice_items with expected titles.
* Insufficient multi-run scope compare generates the “Insufficient data” message.
* Goal-aware item appears when scopes are sufficient.
* Add/extend unit tests in test_phase7_advice.py if needed to cover any new comparison “kind” added to generate_optimization_advice(...).

## Docs (User Guide)

* Update charts.md to reflect the new Compare workflow:
* How to select multiple runs per scope.
* Reminder that advice needs ≥3 runs per scope.
* Mention goal-aware summary applies to multi-run scopes. 

# TODO Advice — expand and formalize

Advice is part of the app’s “contract surface”: it must be deterministic, explainable, and strictly non-prescriptive. It should help players interpret differences in their own data, without telling them what to do.

## Advice contract (invariants)

-   Advice output is descriptive only and must reject prescriptive language (guardrails must be tested).
-   Advice must degrade safely: when data is thin or missing, return “Insufficient data” with a clear basis and limitations.
-   Advice must be traceable: each item must state its basis (what was compared), context (which filters/snapshots), and limitations.
-   Advice must consume existing derived metrics/DTOs and must not introduce new hidden calculations in views.

## Advice modes (expand UI coverage)

-   Snapshot vs current filters (already supported; ensure UI makes this easy and obvious).
-   Snapshot vs snapshot (already supported; ensure it works across dashboards once snapshot reuse is solved).
-   Goal-aware advice (weighted, transparent index over existing percent deltas):
    -   Provide a small set of named goals (e.g. “Economy / Farming”, “Progression”, “Tournament”) with default weights.
    -   Allow users to adjust weights, but always show the formula and the component deltas.
-   Window vs window summaries (date ranges, rolling N runs) as the primary advice basis (preferred over single-run comparisons).

## Data sufficiency rules (make them consistent)

-   A single global minimum run threshold is not enough once advice spans multiple metrics; enforce “enough runs for every metric used”.
-   Always display sample size and date/window boundaries for each compared scope.
-   Treat mixed-tier comparisons as a first-class limitation and surface it explicitly.
-   Never fall back silently (empty/None → explicit “Insufficient data”).

## Output structure (make it composable)

-   Treat advice as a list of small `AdviceItem` cards:
    -   Title (1 line)
    -   Basis (inputs)
    -   Context (filters/snapshot labels)
    -   Limitations (why this may be misleading)
-   Sort advice items deterministically (stable order) to support golden tests and avoid UI churn.

## Testing acceptance criteria

-   Unit: forbidden-token language guardrail tests cover titles, basis, context, and limitations.
-   Unit: advice returns stable ordering for the same inputs.
-   Golden: fixture dataset produces a stable set of advice items for at least one snapshot vs current comparison and one goal-aware comparison.
-   Integration: UI disables advice modes when insufficient data and explains why.


<a id="org2e320c1"></a>

# TODO Comparison / Scenario View + reusable Snapshots

-   “Comparison / Scenario View and Snapshots” (TODO) and notes that snapshots are not yet reusable “anchors” across dashboards.

What appears missing (by the spec in the doc):

-   A shared snapshot/context selector that can drive multiple pages consistently (Charts + at least one other dashboard).
-   A clear definition of “reusable across dashboards” with an integration test that proves it.

Suggested acceptance criteria:

-   Two pages consume the same snapshot selector and show consistent scope changes.
-   Snapshot DTO round-trips without lossy transforms (save → load → identical config).


<a id="org9261a36"></a>

# TODO Open analysis/context feature gaps

These are framed in \`theTower<sub>stats</sub><sub>app.md</sub>\` as Phase 6 “context” work and may still be incomplete:

-   Preset filtering edge cases (no preset, preset with no matching runs).
-   Tier + Preset + Date range precedence rules with predictable empty-state behavior.
-   Rolling windows (“last N runs”, “last N days”).
-   Effective vs base value display everywhere parameters appear (tooltip/expandable is sufficient per the doc).

Suggested acceptance criteria:

-   A mandatory “context matrix” golden test that asserts shape/empties across contexts (the doc explicitly calls this out).
-   Explicit empty-state DTOs (typed empties) rather than silent fallbacks.


<a id="orgf649ce4"></a>

# TODO Test taxonomy and marker enforcement

\`theTower<sub>stats</sub><sub>app.md</sub>\` includes a TODO block to formalize:

-   \`unit\` vs \`integration\` markers (and optionally \`regression\`/\`golden\`),
-   CI enforcement for markers,
-   dev docs explaining the taxonomy,
-   separate CI jobs (fast unit vs full).

This is a process gap (not a feature) but will reduce long-term maintenance cost.
