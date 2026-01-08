# Contributing to The Tower Stats

Thank you for contributing to The Tower Stats. This project prioritizes correctness, traceability, and player trust.
Before starting, read `docs/philosophy.md`, `docs/design_philosophy.md`, and `agents.md`.

## Contribution Principles

- Keep every change small, tested, and documented.
- Preserve raw game data; do not normalize destructively.
- Use descriptive, non-prescriptive language in user-facing text.
- Prefer deterministic, testable outputs over clever heuristics.

## Required Workflow

- Follow the guidance in `agents.md` for every contribution.
- If you use a chatbot or automated assistant, it must follow `agents.md` without exception.
- Add or update tests for every behavior change.
- Update documentation in `docs/` for any functional change and ensure `mkdocs.yml` stays accurate.
- Do not change version numbers or `CHANGELOG.md` unless explicitly asked.

## Engineering Standards

- Add concise Google-style docstrings to new public functions, classes, and modules.
- Enforce safe redirects via the centralized helper; never redirect to user-supplied URLs directly.
- New management commands must include permission checks.
- Analysis code must remain pure: no Django imports, no database writes.

## Local Checks

Run the full validation suite before opening a PR:

```bash
./scripts/checks
```

## Pull Requests

Every PR should describe:

- purpose
- approach
- touched files
- limitations
- follow-up tasks
