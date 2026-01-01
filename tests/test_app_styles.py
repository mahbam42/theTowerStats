"""Unit tests for core app styling overrides."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def test_headings_use_theme_text_color() -> None:
    """Ensure heading styles override Foundation defaults with theme text color."""

    css_path = Path(__file__).resolve().parent.parent / "core/static/core/app.css"
    css_contents = css_path.read_text(encoding="utf-8")
    assert "h1, .h1," in css_contents
    assert "color: var(--tts-color-text);" in css_contents
