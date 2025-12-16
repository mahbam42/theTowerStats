# **agents.md**

## **Purpose**

This document defines how agents (contributors, assistants, and automated helpers)
should work on **theTowerStats**.

**theTowerStats** is a stats-tracking and analysis application for **The Tower** mobile game.
Its purpose is to:

- ingest player battle history as raw text,
- preserve and normalize game data without destructive transforms,
- compute deterministic, testable metrics via a dedicated Analysis Engine,
- present results through charts and dashboards,
- support player interpretation without offering prescriptive strategy.

Agents must prioritize correctness, traceability, and testability over speed or
feature breadth.

## **Guiding Principles**

1. Keep every change **small, tested, and documented**.
2. Do not skip linting, testing, or pre-commit validation.
3. Write clear commit messages and add/update tests with every feature.
4. Structure work as explicit steps with a status (`pending`, `in_progress`, `complete`).
   There should always be **exactly one** `in_progress` step.

## **Mandatory Standards**

- Documentation Updates Required
  : Any functional change (model, view, importer, command, or UI behavior) must update project documentation located in /docs/ and indexed in mkdocs.yml.
- Permissions on New Commands
  : All new Django management commands must include appropriate permission checks and should integrate cleanly with the existing access-control patterns.
- Docstrings Required on New Code
  : All new functions, classes, methods, utilities, and management commands must include concise, descriptive docstrings using standard Django/Python conventions.
- Analysis Must Feed Visual Output
  : New analysis logic should be demonstrable via a chart or view unless explicitly scoped as backend-only.

    ### Docstrings should describe:
	- Purpose
	- Inputs/args
	- Return value or side effects
	- Any assumptions or required context

## **Development Workflow**

### **Environment Setup**
Agents must assume a local development environment using:

- Python (project-specified version)
- Django
- sqlite (default dev database)
- pytest, pytest-django
- ruff and mypy
### **Branch Workflow**

- Add Google-style docstrings to all new public modules, classes, and functions.
- Agents must NOT create, delete, or switch git branches.
- Agents must work on the currently checked-out branch only.
- Branch creation is handled manually by the human operator.

### **Testing Requirements**

Every PR must include:

- tests for every new feature or behavior,
- updated tests when modifying existing logic,
- golden tests for parsers, analysis calculations, or wiki-derived effects when applicable.

### **Linting, Type Checking and Testing**

All code must satisfy:

* **ruff** (style + lint),
* **mypy** (types).
* **pytest** (regression testing).

## **Commit Requirements**

Each commit must:

* include descriptive messages,
* reference issues when appropriate,
* never leave failing tests behind.

## Documentation Standards

### Documentation Types (Hard Separation)

This project maintains two distinct kinds of documentation. They must never be mixed.

A. **User Guide Documentation (Primary)**

Audience: Players and non-technical users
Purpose: Explain how to use the app, not how it is built

Includes:
- Battle History
- Charts
- Cards
- Ultimate Weapons
- Guardian Chips
- Bots
- General app navigation and workflows

Must NOT include:
- Internal architecture
- Model names
- Django concepts
- Analysis engine details
- File paths or implementation notes

B. **Developer / Progress Documentation (Secondary)**

Audience: Contributors and maintainers
Purpose: Explain how the app works internally and track progress

Includes:
- Phase roadmaps
- Architecture diagrams
- Models
- Analysis engine behavior
- Wiki scraping logic
- Testing standards

These docs live under a Development section and are explicitly not user-facing.

### User Guide Tone & Style Rules (Strict)

When writing User Guide documentation, enforce all of the following.
- Tone
  - Professional
  - Clear
  - Calm
  - Technically accurate but non-technical language
  - Assume the reader has *never seen* the code
- Avoid:
  - Slang
  - Casual phrasing
  - Developer shorthand
  - “Just”, “simply”, or “obviously”

### Required Structure for User Guides

Every User Guide page must follow this structure in order:

1. Overview
  - What this section is
  - What problem it helps the player solve
  - One short paragraph only

2. When to Use This
  - Bullet list of common player situations
  - No instructions yet

3. How to Use
  - Step-by-step instructions
  - Short numbered lists
  - One action per step
  - Use direct action verbs:
    - Select
    - View
    - Filter
    - Compare
    - Review

4. How to Read the Results
  - Explain charts, tables, or values
  - Focus on interpretation, not calculation
  - Clarify units and trends

5. Notes & Limitations
  - Use blockquotes
  - Call out important constraints or misunderstandings

    Example:

    > ⚠️ Note
    > Values shown here are calculated at the time you view the page and may change if your data changes.

6. (Optional) Advanced Usage
  - Only include if the feature truly has advanced behavior
  - Still no code, no internals

4. Formatting Rules
  - Use hierarchical headings only (##, ###, ####)
  - Headings must be consistent and descriptive
(Optimized for auto-generated Tables of Contents)
  - Prefer:
    + Bullet lists
    + Numbered steps
  - Avoid:
    + Code blocks
    + CLI examples
    + Inline code formatting unless absolutely necessary
  - Icons and callouts are encouraged for:
    + Notes
    + Warnings
    + Cautions

### Enforcement Rules for Codex

When Codex is instructed to write or modify documentation, it must:

- Explicitly identify whether the doc is:
  - User Guide, or
  - Developer Documentation

- Follow the correct structure for that type
- Reject mixed-purpose documentation
- Prefer clarity over completeness

- If unsure:
  - Default to User Guide tone
  -  Exclude internal details

### Validation Checklist (For Review)

A User Guide page is acceptable only if:
- A non-technical user can understand it without explanation
- No internal model or class names are mentioned
- The document reads as instructions, not a design doc
- Headings alone form a usable Table of Contents

## **Execution Pattern (For AI Agents)**

### **Task Structure**

Every task must be divided into sequential steps with statuses:

| Step | Description                | Status  |
| ---- | -------------------------  | ------- |
| 1    | Identify module to modify  | pending |
| 2    | Implement logic            | pending |
| 3    | Write tests                | pending |
| 4    | Add docs                   | pending |
| 5    | Run lint & type checks     | pending |
| 6    | Run offline + full tests   | pending |
| 7    | Offer short Commit Message | pending |

Rules:

- Exactly one step may be `in_progress` at a time.
- Steps must be completed in order.
- Completed steps must be marked `complete`.

### **Agent Behavioral Rules**

Agents must:
- keep changes small and incremental,
- update tests and documentation with functional changes,
- avoid scope creep beyond the assigned task.

Agents must not:
- bypass linting, typing, or tests,
- commit directly to `main`,
- introduce undocumented public APIs.

## **Deliverables Required in Every PR**

A valid pull request must include:

1. **Code** — typed, documented, structured.
2. **Tests** — new and updated as required.
3. **Docs** — updates to public API docs and `docs/` materials.
4. **Changelog entry** (if requested by maintainers).
5. **Clear PR description** listing:

   * purpose,
   * approach,
   * touched files,
   * limitations,
   * follow-up tasks.

## **Validation Checklist**

Before opening a PR:

* [ ] All public code has Google-style docstrings
* [ ] New features have tests
* [ ] Updated behavior has updated tests
* [ ] Docs updated
* [ ] PR description is complete

## **Project-Specific Rules **theTowerStats****

## **Agent Test Suite**

This suite ensures agents follow the rules.
It can be run manually, or embedded into future automation.

## **Pre-Work Tests**
Before starting work on **theTowerStats**, agents must confirm:

- Analysis code in `analysis/`:
  - does not import Django models,
  - does not perform database writes,
  - returns DTOs only.

- Parsers:
  - treat unknown labels as non-fatal,
  - preserve raw input values,
  - avoid destructive normalization.

- Wiki-derived data:
  - is treated as immutable per revision,
  - is never overwritten in place,
  - includes source and parse metadata.
* **Environment Ready**

## **Code Quality Tests**

* **Docstring Enforcement**

  * [ ] Every new function/class/module has a Google-style docstring
  * [ ] Public APIs have parameter + return doc sections

* **Type Enforcement**

  * [ ] All functions have type hints
  * [ ] `mypy` passes

* **Lint Enforcement**

  * [ ] `ruff` passes
  * [ ] Code autoformatted where possible

## **Testing Suite Enforcement**

* Test Coverage Expectations:

  * [ ] Markdown conversion tested
  * [ ] Directory walk tested
  * [ ] mkdocs.yml parsing tested
  * [ ] Page hierarchy creation tested

## **Documentation Tests**

* [ ] New APIs are documented in `docs/`
* [ ] Example usage added where appropriate
* [ ] mkdocs.yml integration documented
* [ ] Markdown feature coverage documented (supported elements listed)

## **PR Readiness Tests**

* [ ] PR description includes purpose, approach, files, limitations
* [ ] Branch up to date with `main`
* [ ] No debug prints or temporary code
* [ ] Small, review-ready commits

## **Agent Behavior Compliance**

* [ ] Steps tracked with `pending / in_progress / complete`
* [ ] Exactly one step in `in_progress`
* [ ] No steps skipped
* [ ] No assumptions made without checking the codebase
* [ ] Work done incrementally
