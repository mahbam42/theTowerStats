## Design Principles (Developer)

### Purpose

Build a tool that helps players **observe and reason about their own performance** without prescribing actions or enforcing a meta.

The app must prioritize trust, clarity, and explainability over cleverness or novelty.

### Core Principles

#### 1. Data Is Sacred

* Raw Battle Reports are the source of truth
* No inferred values, synthesized totals, or silent corrections
* Missing or ambiguous data must surface explicitly

If the game didn’t report it, the app doesn’t invent it.

#### 2. Context Defines Scope, Not Meaning

* Filters (tier, preset, date range, tournament) limit *which data* is included
* They must never change *what a metric means*
* Same metric + same raw data must always produce the same result

Context handling must be deterministic and testable.

#### 3. Derive, Don’t Persist

* Derived metrics are computed, not stored
* Re-running analysis with the same inputs must yield identical outputs
* Wiki or balance changes must not invalidate historical runs

Version everything that can drift.

#### 4. Explainability Over Optimization

* Every chart, summary, or advice output must be traceable
* Outputs must be explainable using:

  * Included runs
  * Applied filters
  * Visible formulas or transformations

If an output cannot be explained clearly, it does not belong in the app.

#### 5. Advice Is Descriptive, Never Prescriptive

* No imperative language (“should”, “best”, “optimal”)
* No hidden weighting or inferred intent
* All advice must reference the comparison or snapshot it was derived from

If conclusions require assumptions that can’t be surfaced, degrade gracefully to:

> “Insufficient data to draw a conclusion.”

#### 6. Safety Through Constraints

* Limit valid chart combinations explicitly
* Prefer validation and rejection over permissive behavior
* Typed DTOs are the contract between analysis and UI

Invalid states should be unrepresentable.

#### 7. Player Trust Is the Primary Metric

* A player should be able to audit what they’re seeing
* Empty states must be explicit, not silent
* Surprising results should be explainable without external knowledge

If users don’t trust the output, the app has failed — even if the math is correct.

#### 8. No Rankings, No Status Pressure

* No leaderboards
* No player-to-player comparison
* Any aggregated or global analysis must be:

  * Descriptive
  * Opt-in
  * Non-identifying

This app contextualizes runs; it does not evaluate players.

### Non-Goals (Explicit)

The app is not trying to:

* Solve the game
* Predict optimal play
* Simulate future outcomes
* Enforce balance opinions
* Replace player judgment

Those are separate problems with different ethical and design constraints.

### Litmus Test

Before adding a feature, ask:

> “Does this help the player understand *their own data* more clearly — without telling them what to do?”

If the answer is not an unambiguous “yes,” don’t build it.