# ParameterKey Registry

The `ParameterKey` enum defines the canonical parameter labels used across bots, guardian chips, and ultimate weapons. Keys are stable identifiers; display names and semantics come from each entity's parameter definition.

## Available keys

| Key | Description |
| --- | --- |
| `angle` | Degrees or radians used by directional effects. |
| `cash_bonus` | Flat cash bonus applied by an effect. |
| `chance` | Generic proc or trigger chance. |
| `coins_bonus` | Flat coins bonus applied by an effect. |
| `coins_multiplier` | Multiplier applied to coin rewards. |
| `cooldown` | Cooldown duration before an effect can trigger again. |
| `damage` | Base damage value. |
| `damage_multiplier` | Multiplier applied to a damage source. |
| `damage_percent` | Percentage-based damage modifier. |
| `damage_reduction` | Reduction applied to incoming damage. |
| `double_find_chance` | Chance to receive double rewards. |
| `duration` | Time an effect remains active. |
| `effect_wave` | Wave index on which an effect triggers. |
| `find_chance` | Chance to find a resource or reward. |
| `linger` | Time an effect persists after triggering. |
| `max_recovery` | Maximum recoverable value (e.g., health). |
| `multiplier` | Generic multiplier used by utility effects. |
| `percentage` | Generic percentage parameter. |
| `quantity` | Count of projectiles, targets, or effect instances. |
| `range` | Range or radius of an effect. |
| `recovery_amount` | Amount recovered by a healing or restore effect. |
| `size` | Size or area scaling factor. |
| `slow` | Slow percentage applied to targets. |
| `targets` | Number of targets affected. |

## Validation rules

* The registry lives in `definitions.models.ParameterKey`; only values in that enum are accepted.
* `core.upgradeables.validate_parameter_definitions` enforces that each entity declares only registered keys and the expected count per entity type.
* Utility helpers (for example, wiki rebuild and sync utilities) map raw headers to these keys and reject unknown labels to keep the registry canonical.

## Usage guidelines

* Treat keys as stable API surface: adding a key is additive; renaming/removing a key is a breaking change.
* Display names come from `display_name` on parameter definitions; do not overload the key string itself with presentation concerns.
* When introducing new parameterized content, add the key to the enum, document it here, and ensure validation covers the new usage.
