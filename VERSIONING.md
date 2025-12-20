# Versioning Policy

This project follows **Semantic Versioning 2.0.0**  
<https://semver.org/>

## Version Format

MAJOR.MINOR.PATCH

## General Rules

- MAJOR version increments indicate **breaking changes**
- MINOR version increments indicate **backward-compatible additions**
- PATCH version increments indicate **bug fixes only**

---

## Pre-1.0.0 Policy (0.y.z)

While MAJOR = 0:

- The public API is considered **unstable**
- Data models, schemas, and derived metrics may change freely
- Breaking changes DO NOT require a major version bump
- MINOR version increments represent meaningful progress
- PATCH versions are still used for bug fixes

Examples:

- 0.1.0 — First deploy
- 0.2.0 — New dashboards or metrics
- 0.2.1 — Bug fixes, validation fixes, doc corrections

Optional pre-release tags MAY be used:

- 0.1.0-alpha
- 0.3.0-beta.1

---

## Definition of 1.0.0

Version 1.0.0 is released when:

- All core data models are finalized and documented
- ParameterKey registry is canonical and enforced
- All dashboards consume derived metrics only
- Multi-player isolation and permissions are complete
- Advice outputs are deterministic and explainable
- User and Developer documentation reflect actual behavior

---

## Post-1.0.0 Rules

After 1.0.0:

- Breaking data model or dashboard changes → MAJOR bump
- New backward-compatible features → MINOR bump
- Bug fixes and internal refactors → PATCH bump

Breaking changes MUST be documented in:

- CHANGELOG
- Migration notes (if applicable)

---

## Enforcement Expectations

Automated agents and contributors MUST:

- Update versions according to this policy
- Avoid introducing breaking changes without a MAJOR bump
- Treat dashboards and advice outputs as public API after 1.0.0
