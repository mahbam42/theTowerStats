"""Deployment readiness tests for production settings."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def _repo_root() -> Path:
    """Return the repository root directory."""

    return Path(__file__).resolve().parent.parent


def _run_manage_check_deploy(*, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    """Run `manage.py check --deploy` in a subprocess.

    Args:
        env: Environment variables to merge into the current environment.

    Returns:
        Completed process result with captured output.
    """

    merged_env = os.environ.copy()
    merged_env.update(env)
    merged_env.setdefault("DJANGO_SETTINGS_MODULE", "theTowerStats.settings")
    return subprocess.run(
        [
            sys.executable,
            "manage.py",
            "check",
            "--deploy",
            "--fail-level",
            "WARNING",
        ],
        cwd=_repo_root(),
        env=merged_env,
        check=False,
        capture_output=True,
        text=True,
    )


def test_base_template_uses_local_static_assets(auth_client) -> None:
    """Render a typical page and ensure local static assets are referenced."""

    response = auth_client.get("/")
    assert response.status_code == 200
    assert "/static/core/app.css" in response.content.decode("utf-8")
    assert "/static/core/app.js" in response.content.decode("utf-8")


def test_manage_check_deploy_passes_with_required_env(tmp_path: Path) -> None:
    """Verify production settings satisfy Django's deployment checks."""

    result = _run_manage_check_deploy(
        env={
            "DJANGO_DEBUG": "0",
            "DJANGO_SECRET_KEY": "tests-only-secret-key-please-replace-with-a-long-random-value-0123456789",
            "DJANGO_ALLOWED_HOSTS": "example.com",
            "DJANGO_CSRF_TRUSTED_ORIGINS": "https://example.com",
            "DATABASE_URL": f"sqlite:///{tmp_path / 'db.sqlite3'}",
        }
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr


def test_manage_check_deploy_requires_secret_key(tmp_path: Path) -> None:
    """Ensure production settings refuse to boot without a non-default secret key."""

    result = _run_manage_check_deploy(
        env={
            "DJANGO_DEBUG": "0",
            "DJANGO_ALLOWED_HOSTS": "example.com",
            "DJANGO_CSRF_TRUSTED_ORIGINS": "https://example.com",
            "DATABASE_URL": f"sqlite:///{tmp_path / 'db.sqlite3'}",
        }
    )
    assert result.returncode != 0
    assert "DJANGO_SECRET_KEY is required" in result.stderr


def test_manage_check_deploy_allows_platform_domain_without_allowed_hosts(tmp_path: Path) -> None:
    """Accept a platform-provided public domain when explicit hosts are not set."""

    result = _run_manage_check_deploy(
        env={
            "DJANGO_DEBUG": "0",
            "DJANGO_SECRET_KEY": "tests-only-secret-key-please-replace-with-a-long-random-value-0123456789",
            "RAILWAY_PUBLIC_DOMAIN": "example.up.railway.app",
            "DATABASE_URL": f"sqlite:///{tmp_path / 'db.sqlite3'}",
        }
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr


def test_manage_check_deploy_requires_allowed_hosts_or_platform_domain(tmp_path: Path) -> None:
    """Fail fast in production when no host allowlist is configured."""

    result = _run_manage_check_deploy(
        env={
            "DJANGO_DEBUG": "0",
            "DJANGO_SECRET_KEY": "tests-only-secret-key-please-replace-with-a-long-random-value-0123456789",
            "DATABASE_URL": f"sqlite:///{tmp_path / 'db.sqlite3'}",
        }
    )
    assert result.returncode != 0
    assert "DJANGO_ALLOWED_HOSTS is required in production" in result.stderr
