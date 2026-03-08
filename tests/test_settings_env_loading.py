"""Unit tests for local ``.env`` loading in Django settings."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from types import ModuleType

import pytest

pytestmark = pytest.mark.unit


def _load_settings_module() -> ModuleType:
    """Load the settings module under a temporary module name.

    Returns:
        The loaded settings module object.
    """

    repo_root = Path(__file__).resolve().parents[1]
    settings_path = repo_root / "theTowerStats" / "settings.py"
    spec = importlib.util.spec_from_file_location("test_settings_env_loading", settings_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.regression
def test_settings_load_dotenv_without_overriding_existing_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ensure settings bootstrap local ``.env`` values for development.

    Args:
        tmp_path: Temporary directory fixture.
        monkeypatch: Pytest environment patch helper.

    Returns:
        None.
    """

    env_path = Path(__file__).resolve().parents[1] / ".env"
    original_text = env_path.read_text(encoding="utf-8") if env_path.exists() else None

    for key in ("DATABASE_URL", "EXTRA_ENV_VALUE"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("DJANGO_DEBUG", "1")
    monkeypatch.setenv("DJANGO_TEST_USE_SQLITE", "0")

    try:
        env_path.write_text(
            "\n".join(
                [
                    f"DATABASE_URL=sqlite:///{tmp_path / 'from-dotenv.sqlite3'}",
                    "EXTRA_ENV_VALUE=from-dotenv",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        module = _load_settings_module()

        assert os.environ["EXTRA_ENV_VALUE"] == "from-dotenv"
        assert module.DATABASES["default"]["NAME"] == str(tmp_path / "from-dotenv.sqlite3")

        monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'from-shell.sqlite3'}")
        monkeypatch.setenv("EXTRA_ENV_VALUE", "from-shell")
        module = _load_settings_module()

        assert os.environ["EXTRA_ENV_VALUE"] == "from-shell"
        assert module.DATABASES["default"]["NAME"] == str(tmp_path / "from-shell.sqlite3")
    finally:
        if original_text is None:
            env_path.unlink(missing_ok=True)
        else:
            env_path.write_text(original_text, encoding="utf-8")
