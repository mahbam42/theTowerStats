"""Tests for developer tooling scripts."""

from __future__ import annotations

from pathlib import Path


def test_checks_script_runs_expected_commands() -> None:
    """Ensure `scripts/checks` runs ruff, mypy, then pytest."""

    repo_root = Path(__file__).resolve().parents[1]
    checks_path = repo_root / "scripts" / "checks"

    content = checks_path.read_text(encoding="utf-8")

    expected_snippets = [
        'ruff_cmd="ruff"',
        'mypy_cmd="mypy"',
        'pytest_cmd="pytest"',
        '"$ruff_cmd" check',
        '"$mypy_cmd" .',
        '"$pytest_cmd" -v',
    ]
    for snippet in expected_snippets:
        assert snippet in content
