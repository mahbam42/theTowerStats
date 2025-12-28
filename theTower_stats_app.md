
# Table of Contents

1.  [First-run onboarding](#orge0ff992):UX:
2.  [Revise Dashboard Docs to be Per Feature](#org1396562):UX:
3.  [Confidence cues](#org06eee3d):UX:
4.  [“Why am I seeing this?” panels](#orgab46d7c):UX:enhancement:
5.  [Error Recovery UX](#orgd60abe6):UX:enhancement:


<a id="orge0ff992"></a>

# TODO First-run onboarding     :UX:

One-page “What this app does / doesn’t do”

A single sample chart + explanation

## Problem

New users do not have enough context to trust what they are seeing (scope, limitations, and non-goals), and they have no “first success” moment that confirms the app is working.

## Goal

Provide a short, one-time onboarding flow that:

- Sets expectations (“observe and interpret your own data”, not recommendations).
- Creates an immediate, low-effort success moment (a sample chart + plain-language explanation).
- Makes import feel safe and recoverable (clear paths for “try demo data” and “import my reports”).

## Non-goals

- No strategy or prescriptive guidance.
- No account creation requirements.
- No hidden analysis; the onboarding should not introduce “special” calculations.

## UX requirements

- Entry points:
  - On first visit (no imported runs), show onboarding by default.
  - Provide a persistent way to re-open onboarding (e.g., Help → “What is this app?”).
- Page structure (single page, scrollable):
  - “What this app is” + “What this app is not” (match `docs/philosophy.md` tone and commitments).
  - A single sample chart with a short explanation of:
    - What data is included/excluded (demo data label).
    - What the headline metric means (units, time window).
    - A reminder that context changes scope, not meaning.
  - Two primary actions:
    1) Try demo data
    2) Import Battle Reports
  - One secondary action:
    - Skip for now (leads to an explicit empty-state dashboard, not a confusing blank page).
- Trust cues (explicit, consistent):
  - Show “Demo data” labeling whenever demo mode is active.
  - Show “Runs in scope: 0” messaging when the user has not imported anything.

## Copy constraints

- Prefer descriptive phrasing (“This view includes…”, “Based on selected runs…”) and avoid directive phrasing (“You should…”).
- When data is missing, state the limitation directly instead of implying meaning.

## Acceptance criteria

- A brand-new user can reach a meaningful chart within 1–2 clicks via demo data.
- The onboarding clearly communicates the app’s purpose and non-goals without referencing internal architecture.
- Users can always reach import from onboarding and can always recover if they skip.

## Docs impact (when implemented)

- User Guide: add a short “First-run onboarding” section under an appropriate page (likely `docs/user_guide.md` or `docs/index.md`) and ensure it matches the User Guide structure rules.


<a id="org1396562"></a>

# TODO Revise Dashboard Docs to be Per Feature     :UX:

The docs are getting big and have long numbered lists of possible actions/steps. The information would be better structured if it was broken down by feature on each dashboard.

-   Charts:
    -   General
    -   Context
    -   Compare
    -   Analysis
    -   Chart Builder

## Problem

Long, mixed-purpose documentation makes it difficult for users to find answers. Large “do-everything” pages also make it hard to keep doc content consistent with UI behavior.

## Goal

Restructure user-facing dashboard documentation into smaller, feature-focused sections that:

- Match how users think (“Compare”, “Filter”, “Read results”) rather than how the dashboard is implemented.
- Reduce long, dense action lists by grouping related workflows.
- Make limitations and scope rules easy to discover (“what is included/excluded”).

## Non-goals

- No developer/architecture content in User Guide pages.
- No duplication of the Philosophy pages; link when needed.

## Proposed doc structure (Charts dashboard example)

Create feature sections that each follow the required User Guide structure:

- Charts — General (what charts are, when to use, how to read)
- Charts — Context (filters, scope, and “context changes scope, not meaning”)
- Charts — Compare (what compare does, run/window selection, reading deltas)
- Charts — Analysis (what derived metrics represent, how to interpret trends)
- Charts — Chart Builder (how to assemble a chart, what combinations are allowed)

## Acceptance criteria

- Each feature section is skimmable and answer-oriented (headings alone form a usable TOC).
- “Notes & Limitations” exist in each feature section and include the most common misunderstandings.
- No page includes internal model names, Django concepts, or file paths.

## Docs impact (when implemented)

- Update the relevant files under `docs/` and ensure any new pages are indexed in `mkdocs.yml`.


<a id="org06eee3d"></a>

# TODO Confidence cues     :UX:

Small “Data completeness” or “Runs in scope” callouts

Explicit “This view excludes tournament runs” style notes

## Problem

Without explicit scope and completeness indicators, users can misinterpret charts and summaries (especially when filters or data gaps change what is included).

## Goal

Add lightweight, consistent “confidence cues” that help users audit:

- What data is in scope (run counts, date ranges, filters).
- What is excluded (tournament vs normal, missing tiers, ignored presets).
- How complete the data is (e.g., partial imports, parse warnings).

## Non-goals

- No numeric “confidence score” that implies correctness.
- No hidden inference about why data is missing.

## UX requirements

- Provide a small, consistent “Scope & completeness” callout component used across dashboards.
- Minimum fields (when available):
  - Runs in scope (N)
  - Date span covered
  - Key exclusions (e.g., “Tournament runs excluded”)
  - Parse/import warnings count (if tracked)
- Cues must be explicit when a view is empty:
  - “No runs match your current filters” vs “No runs imported yet”
- Cues must not require users to scroll to understand why a result looks “off”.

## Acceptance criteria

- Every chart/summary view has a visible “Runs in scope” indicator.
- Any major exclusion (tournament filtering, preset filtering, snapshot constraints) is surfaced in the same place, in plain language.
- Empty states always distinguish “no data exists” from “filters excluded everything”.


<a id="orgab46d7c"></a>

# TODO “Why am I seeing this?” panels     :UX:enhancement:

A collapsible explanation under charts:

-   What data is included

-   What is excluded

-   How aggregation works (plain language)

Especially powerful for:

-   Derived metrics

-   Advice summaries

-   Snapshot comparisons

## Problem

When a chart or summary looks surprising, users have no immediate, in-context way to understand scope, aggregation, and exclusions. This undermines trust and increases support burden.

## Goal

Add a collapsible “Why am I seeing this?” panel under charts/summaries that explains, in plain language:

- What data is included
- What is excluded
- How values are aggregated (at a high level, without hidden math)
- What limitations apply (thin samples, mixed tiers, missing fields)

## Non-goals

- No dense technical explanations or internal naming.
- No new analysis logic; this is visibility into existing behavior.

## UX requirements

- Panel is collapsed by default to avoid clutter; it should be easy to discover.
- The content is deterministic and generated from the actual request context:
  - Filters applied
  - Run counts
  - Snapshot vs current mode (if applicable)
  - Compare scope definitions (A vs B)
- Provide a consistent template across dashboards so users learn where to look.

## Copy constraints

- Prefer clear, audit-friendly statements (“Included runs: …”, “Excluded: …”).
- Avoid implying intent or recommendations.
- When the view is derived from multiple runs, always mention the aggregation level (per-run vs combined) in plain language.

## Acceptance criteria

- Every chart that can be filtered or compared has a panel that accurately reflects its current scope.
- Users can answer “what was included?” and “what was excluded?” without leaving the page.


<a id="orgd60abe6"></a>

# TODO Error Recovery UX     :UX:enhancement:

“What to do if parsing fails”

Clear “nothing here yet” empty states everywhere

## Problem

When parsing or data loading fails (or yields partial results), users do not know what happened, whether data was saved, or how to recover. Empty pages also fail to distinguish “no data” from “error”.

## Goal

Make error handling and empty states explicit, recoverable, and trust-preserving:

- Users always know whether import succeeded, partially succeeded, or failed.
- Users get actionable next steps that do not require developer knowledge.
- Views degrade gracefully with clear “nothing here yet” messaging.

## Non-goals

- No silent retries that mask errors.
- No destructive “cleanup” that discards raw input without user intent.

## UX requirements

- Import failures:
  - Show a clear summary of what failed and what (if anything) was imported.
  - Provide actions:
    - View details (human-readable)
    - Copy/download an error report (for support/debugging)
    - Retry import
- Partial imports:
  - Surface parse warnings as non-fatal when possible (unknown labels should not block import).
  - Make it clear which parts of a run are missing or unparsed.
- Empty states:
  - For each dashboard, provide an explicit empty state with:
    - What this page shows
    - Why it is empty (no imports vs filters vs errors)
    - One primary action to resolve (import, clear filters, switch context)

## Acceptance criteria

- No dashboard renders as “blank” without an explanation and a next action.
- Import errors never leave the user unsure whether their data was saved.
- Unknown labels are treated as non-fatal wherever possible and surfaced as warnings.
