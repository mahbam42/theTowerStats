# Project Structure

This page is **Developer Documentation**. It describes how the repository is organized for contributors.

This repository is intentionally split into:

- `analysis/`: pure Python analysis engine (no Django imports, no DB writes)
- `theTowerStats/`: Django project configuration (settings/urls/wsgi/asgi)
- `core/`: Django app for views, forms, services, and management commands
- `definitions/`: Django app for wiki-derived canonical definitions (cards, ultimate weapons, guardian chips, bots)
- `gamedata/`: Django app for imported Battle Reports and run metadata
- `player_state/`: Django app for per-player progress tracking (cards, slots, upgrade progress, presets, snapshots)
- `tests/`: pytest test suite (unit + integration markers)
- `docs/`: MkDocs documentation (User Guide + Developer docs)
- `scripts/`: local tooling (validation, formatting, checks)
- `archive/`: historical prompts and planning notes (not shipped behavior)

## Quickstart (Local)

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
./scripts/checks
```
