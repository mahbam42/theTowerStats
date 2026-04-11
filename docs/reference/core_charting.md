# Core Charting

Developer-facing API reference for the `core.charting` package.

## Notes

- Source breakdown chart configs feed both donut and horizontal bar rendering in the dashboard.
- `core.charting.render` is also responsible for tiny non-zero donut labels such as `<0.1%`.
- The browser-side chart modal can display a larger chart together with a table built from the same payload; keep payload labels stable so the chart and table stay aligned.

## Package

::: core.charting
    options:
      show_root_heading: true
      members: false

## Modules

::: core.charting.builder
    options:
      show_root_heading: true
      members: true

::: core.charting.configs
    options:
      show_root_heading: true
      members: true

::: core.charting.dto_builder
    options:
      show_root_heading: true
      members: true

::: core.charting.flagging
    options:
      show_root_heading: true
      members: true

::: core.charting.flags
    options:
      show_root_heading: true
      members: true

::: core.charting.render
    options:
      show_root_heading: true
      members: true

::: core.charting.schema
    options:
      show_root_heading: true
      members: true

::: core.charting.snapshot_codec
    options:
      show_root_heading: true
      members: true

::: core.charting.validator
    options:
      show_root_heading: true
      members: true
