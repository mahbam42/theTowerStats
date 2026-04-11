# Core Parsers

Developer-facing API reference for the `core.parsers` package.

## Notes

- Battle Report parsing must remain non-destructive: preserve reported values, tolerate unknown labels, and keep raw text available for later backfills.
- Newer section-based reports may be pasted with single-space separators instead of tabs; parser support should not assume wide spacing.
- Parser expansions should be paired with regression coverage and a `reparse_battle_reports` pass when stored derived metrics depend on the newly supported rows.

## Package

::: core.parsers
    options:
      show_root_heading: true
      members: false

## Modules

::: core.parsers.battle_report
    options:
      show_root_heading: true
      members: true
