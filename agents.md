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

* pass pre-commit,
* include descriptive messages,
* reference issues when appropriate,
* never leave failing tests behind.

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
