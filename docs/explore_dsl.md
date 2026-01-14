# Explore DSL

This page is **Developer Documentation**. It defines the Explore DSL grammar, placeholder behavior, and parsing expectations.

## Purpose

The Explore DSL allows player-authored queries to map into the Explore schema without exposing raw model fields. The editor is a thin layer over the existing Explore query schema and registry.

## Grammar Summary

The DSL is line-based. Lines are parsed in any order.

Required lines:
- `name "..."`
- `metric <metric_key> <sum|count>`

Optional lines:
- `scope date <start>..<end>`
- `scope tier <value>`
- `scope preset <id> "Label"`
- `scope snapshot <id> "Label"`
- `scope past_n_runs <value>`
- `scope tier >= <value> and not tournament`
- `scope date <start>..<end> not <YYYY-MM-DD>[, <YYYY-MM-DD>]`
- `scope preset <Preset Name>[, <Preset Name>]`
- `scope preset <Preset Name> not <Preset Name>`
- `filter tier in <v1, v2, ...>`
- `filter tier >= <value>`
- `filter tier <= <value>`
- `filter wave <min>..<max>`
- `filter wave >= <value>`
- `filter wave <= <value>`
- `filter death_cause = "Label"`
- `filter preset = <id>`
- `breakdown by <dimension>[, <dimension>]`
- `output <table|bar|donut|kpi>`

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
- `breakdown by` accepts comma-separated values and `then` as a separator.
- `and` and `&` are accepted as scope modifiers.
- `not tournament` can be appended to a scope line and is parsed as a tournament exclusion filter.
- `not` can also exclude specific dates on the date scope line and preset names on the preset scope line.
- `output` defaults to `table` when not supplied.
- `metric` supports `sum` and `count` only.
- Placeholders do not override prefilled defaults.

## Integration Notes

- Parsing produces an `ExploreQuery` that is validated against the Explore registry.
- Invalid lines produce parse errors and block execution.
- Autocomplete is client-side and sourced from the static registry; richer suggestions are deferred to Future Work.
