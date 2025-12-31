"""Integration tests for chart context form defaults."""

from __future__ import annotations

from datetime import date

import pytest

from core.forms import ChartContextForm

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_chart_context_form_defaults_to_per_run(player) -> None:
    """Chart context should default granularity to per-run when not provided."""

    form = ChartContextForm({}, player=player, today=date(2025, 12, 9))

    assert form.is_valid()
    assert form.cleaned_data["granularity"] == "per_run"
