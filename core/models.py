"""Legacy model module for the `core` app.

The project is transitioning to a layered architecture:
- `definitions` for wiki-derived, rebuildable definitions,
- `player_state` for unlock/progress state,
- `gamedata` for runtime battle reports and run* metrics.

The `core` app retains views/forms/services, but no longer defines database
models directly.
"""

