# Changelog

This project follows Semantic Versioning.

## [0.6.2] (in progress)

- Battle History: show coins per real hour in the table and modal when reported.
- Battle History: fall back to import timestamps for missing battle dates and label imported dates in the UI.
- Battle History modal: use player-scoped run numbers.
- Charts: add tier/preset compare selectors, scope averaging toggle, and scope size warnings.
- Bots: mute Amplify Bot runs used; infer bot runs used from Battle Report bot metrics.
- Guardian Chips: infer runs used for trackable chips from Battle Report metrics; mute Ally runs used.
- Commands: extend `reparse_battle_reports` to backfill bot usage, support patch windows, and reapply battle date fallback.
- Docs: update compare, battle history, battle report modal, bots, guardian chips, goals, and management command guidance.

## [0.6.1]

- Bots: normalize rebuild headers (including non-breaking spaces) and accept level 0 rows when present.
- Bots: populate Runs used from battle report bot lines.
- Guardians: remove unexpected parameter definitions during rebuild to prevent dashboard skips.
- Ultimate Weapons: map generic cost headers (Cost, Cost__2, Cost__3) during rebuilds.
- Cards: normalize effect headers when deriving card effects.
- Docs: note header normalization for wiki rebuilds and clarify bot runs usage.

## [0.6.0]

- Charts: fix run numbering so chart labels match Battle History ordering.
- Charts: abbreviate large values in axes and tooltips using compact suffixes.
- Cards: show correct level 0 values in the card library.
- Bots: fix baseline totals in progress dashboards.
- UI: improve dark-theme styling for callouts and help text.
- Tooling: add `rebuild_wiki_definitions --diffs` preview for wiki changes.
- Docs: align preset labels, cite wiki sources, and fix formatting.
- Ops: add Google Analytics tag.
- Roadmap: update phase planning notes.

## [0.5.1] 

- UI: add dark theme styling across dashboards, navigation, tables, and callouts.
- UI: reorder dashboard layouts on mobile so main content loads first, with compact tables on small screens.
- Charts: default granularity to By battle log and reorganize dashboard controls with chart descriptions/tooltips.
- Charts: move “Include tournaments” into the primary context controls.
- Charts: compare run selectors display tier, wave, date, and time.
- Charts: add fullscreen chart modal and Battle Report modal links from chart tooltips.
- Charts: add run duration vs coins earned scatter and coins earned over time area charts.
- Charts: add free upgrades stacked chart; show total upgrades in the tooltip.
- Charts: add guided walkthrough entry point for demo mode and first login.
- Tests: expand chart builder coverage and align demo CSV export test expectations.
- Fix per-run label rendering and flagging; clarify chart labels in docs
- Docs: add Admin Panel documentation.
- Docs: add master prompts 41 and 42 to archive.
- Docs: revise Charts user guide and update development workflow notes.
- Landing page: make Getting Started the default homepage with a demo chart preview and docs links.
- Demo data: refresh sample Battle Reports with early, mid, and late-game runs.
- Roadmap: update phase planning notes.

## [0.4.0]

- Notes: Summary of the most recent development work.
- Getting started: add a landing page to explain scope and how to begin using the app.
- Charts: add scope explainers and support multi-run Compare views with summary-focused outputs.
- Charts: handle missing Battle Date by falling back to import timestamp for charting.
- Analysis: persist Battle Report derived metrics to support residual coin/cash charts and consistent chart series.
- Ops: require an explicit target for `sync_player_state` to reduce accidental cross-scope updates.
- Battle History: move coins/hour sorting into analysis and tighten player-scoped parameter updates.
- Bug fix: tolerate Guardian chip rebuild failures caused by JSON key reordering.
- Docs: add product philosophy and developer design principles pages; expand user guide chart explanations.
- Tests: add coverage for getting started, navigation, sync command behavior, and derived-metrics persistence.

## [0.3.0]

- Notes: Adds new dashboards, charts/metrics, and documentation updates.
- Cards dashboard: select multiple cards and apply presets in bulk (assign or create preset tags).
- Cards dashboard: replace placeholder descriptions with the current level value (bolded) when available (placeholders allowed at level 0).
- Cards dashboard: rename the Level column to Next Level and add a brief Presets explainer.
- Charts dashboard: add chart taxonomy domains (Economy, Damage, Enemy Destruction, Efficiency) with validation guardrails (no cross-currency cash vs coins, no cross-domain metrics except explicit comparative charts).
- Charts dashboard: add coins/cash source breakdown charts (including “Coins From Ultimate Weapons” and “Cash by Source”) and document cash as in-run purchasing power (non-persistent).
- Charts dashboard: add damage charts (damage by source, percent contribution, and comparative damage vs enemies destroyed; orb effectiveness).
- Charts dashboard: add enemy destruction charts and derive totals by summing per-type rows (ignores Battle Report “Total Enemies” and “Total Elites” due to asymmetry).
- Charts dashboard: donut charts include percent labels; comparative charts support multiple y-axes when units differ.
- Charts dashboard: default chart window to the current Event window and add Event window navigation controls.
- Charts dashboard: add per-run chart granularity toggle.
- Charts dashboard: add stacked and bar chart variants for damage breakdowns.
- Goals dashboard: add goal targets dashboard and goal widgets for upgradeable entities, including cost and delta calculations.
- Battle Report import: add manual tournament toggle to tag runs when the copied text does not indicate a tournament round.
- Developer docs: add mkdocstrings pages for analysis, charting, and parsers.
- Bug fix: tolerate Guardian chip upgrade table cost header drift during `rebuild_wiki_definitions`.

## [0.2.2]

- Notes: Adds new charts/metrics and UI refinements.
- Cards dashboard: select multiple cards and apply presets in bulk (assign or create preset tags).
- Cards dashboard: replace placeholder descriptions with the current level value (bolded) when available (placeholders allowed at level 0).
- Cards dashboard: rename the Level column to Next Level and add a brief Presets explainer.
- Charts dashboard: add chart taxonomy domains (Economy, Damage, Enemy Destruction, Efficiency) with validation guardrails (no cross-currency cash vs coins, no cross-domain metrics except explicit comparative charts).
- Charts dashboard: add coins/cash source breakdown charts (including “Coins From Ultimate Weapons” and “Cash by Source”) and document cash as in-run purchasing power (non-persistent).
- Charts dashboard: add damage charts (damage by source, percent contribution, and comparative damage vs enemies destroyed; orb effectiveness).
- Charts dashboard: add enemy destruction charts and derive totals by summing per-type rows (ignores Battle Report “Total Enemies” and “Total Elites” due to asymmetry).
- Charts dashboard: donut charts include percent labels; comparative charts support multiple y-axes when units differ.
- Bug fix: tolerate Guardian chip upgrade table cost header drift during `rebuild_wiki_definitions`.

## [0.1.0]

- Developer documentation: [Phase 8](docs/phase8.md), [Phase 9](docs/phase9.md)
- Battle Report import with deduplication and safe handling of unknown labels
- Charts with filters, snapshots, and exports (CSV, PNG)
- Read-only progress dashboards for cards, ultimate weapons, guardian chips, and bots
- Per-account data isolation and optional demo dataset
