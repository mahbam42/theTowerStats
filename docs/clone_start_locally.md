# Clone and Start Locally

This guide is for contributors and self-hosters who want to run theTowerStats on a local machine.

## Prerequisites

- Python (project version)
- SQLite (default dev database)
- A local virtual environment (recommended)

## Steps

1. Clone the repository from GitHub.
2. Create and activate a virtual environment.
3. Install dependencies with `requirements.txt` (and `requirements-dev.txt` for linting/testing).
4. Run migrations with `python manage.py migrate`.
5. Start the dev server with `python manage.py runserver`.
6. Open the app at `http://127.0.0.1:8000/`.

## Notes

- Demo data is available after you sign in and enable demo mode from the landing page.
- Use `pytest`, `ruff`, and `mypy` for the full validation suite before opening a PR.
