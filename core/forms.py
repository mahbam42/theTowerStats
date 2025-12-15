"""Forms for core UI workflows.

Phase 1 requires:
- a paste/import form for raw Battle Report text,
- a date-range filter form for the first time-series chart.
"""

from __future__ import annotations

from django import forms

from analysis.metrics import list_metric_definitions
from gamedata.models import BattleReport
from player_state.models import Preset


class BattleReportImportForm(forms.Form):
    """Validate user-submitted raw Battle Report text."""

    raw_text = forms.CharField(
        label="Battle Report",
        widget=forms.Textarea(attrs={"rows": 12, "cols": 80}),
        help_text="Paste the Battle Report text from The Tower.",
    )
    preset_name = forms.CharField(
        required=False,
        label="Preset label (optional)",
        help_text="Optional context tag applied to this run (e.g. 'Farming build').",
    )


class ChartContextForm(forms.Form):
    """Validate contextual filters and chart overlay options."""

    metric = forms.ChoiceField(
        required=False,
        choices=(),
        label="Metric",
        help_text="Choose an observed or derived metric to chart.",
    )
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
    tier = forms.IntegerField(
        required=False,
        min_value=1,
        label="Tier",
        help_text="Optional exact tier filter.",
    )
    preset = forms.ModelChoiceField(
        required=False,
        queryset=Preset.objects.none(),
        label="Preset",
        empty_label="All presets",
    )
    overlay_group = forms.ChoiceField(
        required=False,
        choices=(
            ("none", "None"),
            ("tier", "Tier"),
            ("preset", "Preset"),
        ),
        label="Overlay",
        help_text="Overlay multiple datasets grouped by tier or preset.",
    )
    moving_average_window = forms.IntegerField(
        required=False,
        min_value=2,
        max_value=30,
        label="Moving average window",
        help_text="Optional simple moving average window size.",
    )
    ev_trials = forms.IntegerField(
        required=False,
        min_value=10,
        max_value=200_000,
        label="EV trials (simulated)",
        help_text="Optional Monte Carlo trials for simulated EV metrics.",
    )
    ev_seed = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=2**31 - 1,
        label="EV seed (simulated)",
        help_text="Optional RNG seed for simulated EV metrics.",
    )

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the form with dynamic preset choices."""

        super().__init__(*args, **kwargs)
        self.fields["preset"].queryset = Preset.objects.order_by("name")
        metrics = list_metric_definitions()
        self.fields["metric"].choices = [
            (m.key, f"{m.label} ({m.kind})") for m in metrics
        ]


class GameDataChoiceField(forms.ModelChoiceField):
    """A ModelChoiceField with a human-readable label for imported runs."""

    def label_from_instance(self, obj) -> str:  # type: ignore[override]
        """Render the choice label using run metadata when available."""

        progress = getattr(obj, "run_progress", None)
        battle_date = getattr(progress, "battle_date", None)
        tier = getattr(progress, "tier", None)
        date_label = getattr(battle_date, "date", lambda: None)()
        tier_label = f"T{tier}" if tier is not None else "T?"
        if date_label is None:
            return f"{tier_label} • imported {obj.parsed_at.date().isoformat()} • {obj.checksum[:10]}…"
        return f"{tier_label} • {date_label.isoformat()} • {obj.checksum[:10]}…"


class ComparisonForm(forms.Form):
    """Validate run vs run and window vs window comparisons."""

    run_a = GameDataChoiceField(required=False, queryset=BattleReport.objects.none(), label="Run A")
    run_b = GameDataChoiceField(required=False, queryset=BattleReport.objects.none(), label="Run B")

    window_a_start = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Window A start",
    )
    window_a_end = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Window A end",
    )
    window_b_start = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Window B start",
    )
    window_b_end = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Window B end",
    )

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the form with a run queryset.

        A `runs_queryset` keyword argument may be provided to limit selectable
        runs (for example, to a filtered context).
        """

        runs_queryset = kwargs.pop("runs_queryset", None)
        super().__init__(*args, **kwargs)
        if runs_queryset is None:
            runs_queryset = BattleReport.objects.select_related("run_progress").order_by(
                "-run_progress__battle_date", "-parsed_at"
            )

        self.fields["run_a"].queryset = runs_queryset
        self.fields["run_b"].queryset = runs_queryset
