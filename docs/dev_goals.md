## Goals Dashboard (Developer Notes)

### Purpose

The Goals Dashboard stores player-selected target levels for upgradeable parameters and computes the remaining currency required to reach each target.

### Data Sources

- Current level sources:
  - Player bot parameters
  - Player guardian chip parameters
  - Player ultimate weapon parameters
- Cost and max-level sources:
  - Bot parameter levels
  - Guardian chip parameter levels
  - Ultimate weapon parameter levels

### Persistence

- `player_state.models.GoalTarget` stores:
  - goal scope (`GoalType`)
  - stable `goal_key`
  - `target_level`
  - optional `label` and `notes`
  - assumption bookkeeping for missing current levels

Goal keys are generated as `{goal_type}:{entity_slug}:{parameter_key}` to stay stable across rebuildable definition rows.

### Cost Computation

- `analysis/goals.py` provides pure functions that:
  - parse cost strings
  - compute per-level costs from current to target
  - return a breakdown DTO suitable for templates

Views assemble the level-table cost mapping and pass it into the analysis helpers.

### UI Integration

- `/goals/` provides the main Goals dashboard.
- Bots, Guardian Chips, and Ultimate Weapons dashboards render a small goals widget (top remaining costs) using a shared component.

### Safety and Guardrails

- All POST writes respect demo-mode restrictions.
- Redirects use the centralized safe redirect helper.

### Tests

- Unit: goal cost breakdown computations.
- Integration: goals dashboard create/clear, completed-goal visibility, and widget rendering.

