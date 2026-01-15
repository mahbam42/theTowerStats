# Explore DSL

This page is **Developer Documentation**. It defines the Explore DSL grammar, placeholder behavior, and parsing expectations.

## Purpose

The Explore DSL allows player-authored queries to map into the Explore schema without exposing raw model fields. The editor is a thin layer over the existing Explore query schema and registry.

## Grammar Summary (Glossary)

The DSL is line-based. Lines are parsed in any order.

| Line | Purpose | Example |
| --- | --- | --- |
| `name` | Names the query (required). | `name "Weekly runs"` |
| `metric` | Selects the metric and aggregation (required). | `metric coins_earned sum` |
| `metric` | Computes an average for the selected metric. | `metric coins_per_hour avg` |
| `scope date` | Sets a date range. | `scope date 2025-01-01..2025-01-31` |
| `scope date all` | Clears the date scope. | `scope date all` |
| `scope tier` | Sets a tier value. | `scope tier 8` |
| `scope tier all` | Clears the tier scope. | `scope tier all` |
| `scope preset` | Targets presets by id or name. | `scope preset 12 "Farm"` |
| `scope snapshot` | Targets a snapshot by id. | `scope snapshot 4 "Phase 9"` |
| `scope past_n_runs` | Limits to the most recent runs. | `scope past_n_runs 20` |
| `scope ... not tournament` | Excludes tournament runs. | `scope tier >= 7 not tournament` |
| `scope date ... not` | Excludes specific dates. | `scope date 2025-01-01..2025-01-31 not 2025-01-15` |
| `scope preset ... not` | Excludes preset names. | `scope preset farm not speed run` |
| `scope <field> *` | Clears a scope value. | `scope snapshot *` |
| `filter tier in` | Filters tiers by list. | `filter tier in 6, 7, 8` |
| `filter tier >=` | Filters tier lower bound. | `filter tier >= 9` |
| `filter tier <=` | Filters tier upper bound. | `filter tier <= 10` |
| `filter wave <min>..<max>` | Filters wave range. | `filter wave 800..1200` |
| `filter wave >=` | Filters wave lower bound. | `filter wave >= 600` |
| `filter wave <=` | Filters wave upper bound. | `filter wave <= 1200` |
| `filter death_cause =` | Filters by death cause. | `filter death_cause = "Fast"` |
| `filter preset =` | Filters by preset id. | `filter preset = 5` |
| `breakdown by` | Groups results by dimensions. | `breakdown by run, tier` |
| `output` | Selects a chart or KPI output. | `output bar` |

## Placeholders

Placeholders use bracketed tokens to signal formatting requirements and are treated as unset values during parsing:

- `[date:YYYY-MM-DD]`
- `[tier:—]`
- `[preset:—]`
- `[snapshot:—]`
- `[runs:—]`

When placeholders are present or a scope line is omitted, parsing falls back to the current prefilled scope from the request context.

## Parsing Rules

- Lines beginning with `#` are ignored as comments.
- The first `name` line wins; missing names yield a validation error.
- `breakdown by` accepts comma-separated values plus `then` or `and` as separators.
- `and` and `&` are accepted as scope modifiers.
- `not tournament` can be appended to a scope line and is parsed as a tournament exclusion filter.
- `not` can also exclude specific dates on the date scope line and preset names on the preset scope line.
- `output` defaults to `table` when not supplied.
- `metric` supports `sum`, `count`, and `avg`; when omitted, aggregation defaults to `sum`.
- Explore v1 supports a single metric per query.
- Placeholders do not override prefilled defaults.
- `all` or `*` clears a prefilled scope value and keeps the scope open.

## Integration Notes

- Parsing produces an `ExploreQuery` that is validated against the Explore registry.
- Invalid lines produce parse errors and block execution.
- Autocomplete is client-side and sourced from the static registry; richer suggestions are deferred to Future Work.
