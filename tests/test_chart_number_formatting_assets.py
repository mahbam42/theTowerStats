"""Regression tests for frontend chart number formatting assets."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.regression]


def test_frontend_compact_number_formatters_support_high_order_suffixes() -> None:
    """Frontend chart formatters include compact suffixes through O-scale."""

    app_js = Path("core/static/core/app.js").read_text(encoding="utf-8")
    dashboard_template = Path("core/templates/core/dashboard.html").read_text(encoding="utf-8")

    for suffix in ('suffix: "s"', 'suffix: "S"', 'suffix: "o"', 'suffix: "O"'):
        assert suffix in app_js
        assert suffix in dashboard_template
