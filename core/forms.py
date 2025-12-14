"""Forms for core UI workflows.

Phase 1 requires:
- a paste/import form for raw Battle Report text,
- a date-range filter form for the first time-series chart.
"""

from __future__ import annotations

from django import forms


class BattleReportImportForm(forms.Form):
    """Validate user-submitted raw Battle Report text."""

    raw_text = forms.CharField(
        label="Battle Report",
        widget=forms.Textarea(attrs={"rows": 12, "cols": 80}),
        help_text="Paste the Battle Report text from The Tower.",
    )


class DateRangeFilterForm(forms.Form):
    """Validate optional date-range filters for chart views."""

    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Start date",
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="End date",
    )
