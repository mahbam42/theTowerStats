# Project Structure

This repository is intentionally split into:

- `analysis/`: a pure Python analysis engine (no Django imports, no DB writes)
- `theTowerStats/`: the Django project configuration (settings/urls/wsgi/asgi)
- `core/`: the first Django app (models/views will land here in later phases)

## Quickstart (Local)

```bash
python manage.py migrate
python manage.py runserver
pytest
```

