"""Forms for core UI workflows.

Phase 1 requires:
- a paste/import form for raw Battle Report text,
- a date-range filter form for the first time-series chart.
"""

from __future__ import annotations

from datetime import date

import re

from django import forms

from analysis.event_windows import event_window_for_date
from analysis.chart_config_dto import ChartScopeDTO
from analysis.series_registry import DEFAULT_REGISTRY
from core.charting.configs import CHART_CONFIG_BY_ID, default_selected_chart_ids, list_selectable_chart_configs
from core.charting.builder import (
    ChartBuilderSelection,
    build_before_after_scopes,
    build_run_vs_run_scopes,
)
from definitions.models import BotDefinition, GuardianChipDefinition, UltimateWeaponDefinition
from gamedata.models import BattleReport
from player_state.models import GoalType, Player, Preset


class BattleReportImportForm(forms.Form):
    """Validate user-submitted raw Battle Report text."""

    _REQUIRED_HEADER_SEPARATOR = r"(?:[ \t]*:[ \t]*|[ \t]+)"
    _BATTLE_REPORT_HEADER_RE = r"(?im)^[^\S\n]*Battle Report[^\S\n]*$"

    raw_text = forms.CharField(
        label="Battle Report",
        widget=forms.Textarea(attrs={"rows": 12, "cols": 80}),
        help_text="Paste exactly one Battle Report from The Tower.",
    )
    preset_name = forms.CharField(
        required=False,
        label="Preset label (optional)",
        help_text="Optional context tag applied to this run (e.g. 'Farming build').",
    )
    is_tournament = forms.BooleanField(
        required=False,
        label="Tournament run",
        help_text="Enable when this run was a tournament round but the pasted report text does not indicate it.",
    )

    def clean_raw_text(self) -> str:
        """Validate that the input contains exactly one Battle Report.

        Returns:
            The raw Battle Report text as entered by the user.
        """

        raw_text = self.cleaned_data.get("raw_text") or ""
        validation_text = (
            raw_text.replace("\r\n", "\n")
            .replace("\r", "\n")
            .replace("\ufeff", "")
            .replace("\u200b", "")
        )
        report_headers = len(re.findall(self._BATTLE_REPORT_HEADER_RE, validation_text))
        if report_headers != 1:
            raise forms.ValidationError("Paste exactly one Battle Report (the header must appear once).")

        patterns = {
            "Battle Date": rf"(?im)^[^\S\n]*Battle Date{self._REQUIRED_HEADER_SEPARATOR}",
            "Tier": rf"(?im)^[^\S\n]*Tier{self._REQUIRED_HEADER_SEPARATOR}",
            "Wave": rf"(?im)^[^\S\n]*Wave{self._REQUIRED_HEADER_SEPARATOR}",
            "Real Time": rf"(?im)^[^\S\n]*Real Time{self._REQUIRED_HEADER_SEPARATOR}",
        }
        counts = {label: len(re.findall(pattern, validation_text)) for label, pattern in patterns.items()}
        required_once = ("Tier", "Wave", "Real Time")
        missing_required = [label for label in required_once if counts[label] != 1]
        if missing_required:
            labels = ", ".join(missing_required)
            raise forms.ValidationError(f"Paste exactly one Battle Report ({labels} must appear once).")

        duplicates = [label for label, count in counts.items() if count > 1]
        if duplicates:
            raise forms.ValidationError(f"Duplicate headers detected: {', '.join(duplicates)}.")
        return raw_text


class ChartContextForm(forms.Form):
    """Validate contextual filters and chart overlay options."""

    charts = forms.MultipleChoiceField(
        required=False,
        choices=(),
        label="Charts",
        help_text="Select one or more charts to display.",
        widget=forms.SelectMultiple(attrs={"size": 8}),
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
    granularity = forms.ChoiceField(
        required=False,
        choices=(
            ("daily", "By date"),
            ("per_run", "By battle log"),
        ),
        label="Granularity",
        help_text="Controls whether charts show one point per date or one point per run.",
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
    include_tournaments = forms.BooleanField(
        required=False,
        label="Include tournaments",
        help_text="By default, tournament runs are excluded from analytics and charts.",
    )
    ultimate_weapon = forms.ModelChoiceField(
        required=False,
        queryset=UltimateWeaponDefinition.objects.none(),
        label="Ultimate Weapon",
        empty_label="(select)",
        help_text="Used by Ultimate Weapon-derived metrics.",
    )
    guardian_chip = forms.ModelChoiceField(
        required=False,
        queryset=GuardianChipDefinition.objects.none(),
        label="Guardian Chip",
        empty_label="(select)",
        help_text="Used by Guardian-derived metrics.",
    )
    bot = forms.ModelChoiceField(
        required=False,
        queryset=BotDefinition.objects.none(),
        label="Bot",
        empty_label="(select)",
        help_text="Used by Bot-derived metrics.",
    )
    wiki_as_of = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        label="Wiki revision (as of)",
        help_text="Optional: select wiki-derived parameters as-of this timestamp instead of latest.",
    )
    moving_average_window = forms.IntegerField(
        required=False,
        min_value=2,
        max_value=30,
        label="Moving average window",
        help_text="Optional simple moving average window size.",
    )
    window_kind = forms.ChoiceField(
        required=False,
        choices=(
            ("", "No rolling window"),
            ("last_runs", "Last N runs"),
            ("last_days", "Last N days"),
        ),
        label="Rolling window",
        help_text="Optional window applied after date/preset/tier filtering.",
    )
    window_n = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=365,
        label="Rolling window size",
        help_text="N for the selected rolling window.",
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

        player: Player | None = kwargs.pop("player", None)
        today: date | None = kwargs.pop("today", None)
        super().__init__(*args, **kwargs)
        self._today = today or date.today()
        if player is None:
            self.fields["preset"].queryset = Preset.objects.order_by("name")
        else:
            self.fields["preset"].queryset = Preset.objects.filter(player=player).order_by("name")
        self.fields["ultimate_weapon"].queryset = UltimateWeaponDefinition.objects.order_by("name")
        self.fields["guardian_chip"].queryset = GuardianChipDefinition.objects.order_by("name")
        self.fields["bot"].queryset = BotDefinition.objects.order_by("name")
        charts = list_selectable_chart_configs()
        category_labels = {
            "economy": "Economy",
            "damage": "Damage",
            "enemy_destruction": "Enemy Destruction",
            "efficiency": "Efficiency",
            "ultimate_weapons": "Ultimate Weapons",
            "guardians": "Guardians",
            "bots": "Bots",
            "comparison": "Comparisons",
            "derived": "Derived",
        }
        grouped: dict[str, list[tuple[str, str]]] = {}
        for chart in charts:
            group = category_labels.get(chart.category, str(chart.category))
            grouped.setdefault(group, []).append((chart.id, f"{chart.title} — {chart.chart_type}"))
        choices: list[tuple[str, list[tuple[str, str]]]] = []
        for group_name in (
            "Economy",
            "Damage",
            "Enemy Destruction",
            "Efficiency",
            "Ultimate Weapons",
            "Guardians",
            "Bots",
            "Comparisons",
            "Derived",
        ):
            if group_name in grouped:
                choices.append((group_name, grouped[group_name]))
        self.fields["charts"].choices = choices

    def clean(self) -> dict[str, object]:
        """Apply Event-window defaults and dashboard invariants."""

        cleaned = super().clean()
        if not cleaned.get("start_date") and not cleaned.get("end_date"):
            window = event_window_for_date(target=self._today, anchor=date(2025, 12, 9))
            cleaned["start_date"] = window.start
            cleaned["end_date"] = window.end
        if not cleaned.get("charts"):
            cleaned["charts"] = list(default_selected_chart_ids())
        if not cleaned.get("granularity"):
            selected = tuple(str(v) for v in (cleaned.get("charts") or ()))
            preferred = [
                CHART_CONFIG_BY_ID[chart_id].default_granularity
                for chart_id in selected
                if chart_id in CHART_CONFIG_BY_ID
            ]
            cleaned["granularity"] = "per_run" if "per_run" in preferred else "daily"
        window_kind = (cleaned.get("window_kind") or "").strip()
        window_n = cleaned.get("window_n")
        if window_kind and not window_n:
            self.add_error("window_n", "Provide a size for the selected rolling window.")
        return cleaned


class UpgradeableEntityProgressFilterForm(forms.Form):
    """Validate unlocked/locked filters for upgradeable-entity dashboards."""

    status = forms.ChoiceField(required=False, choices=(), label="Show")
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Optional: filter by name.",
    )

    def __init__(self, *args, entity_label_plural: str, **kwargs) -> None:
        """Initialize the filter form with an entity-scoped 'All …' label."""

        super().__init__(*args, **kwargs)
        self.fields["status"].choices = (
            ("", f"All {entity_label_plural}"),
            ("unlocked", "Unlocked only"),
            ("locked", "Locked only"),
        )


class UltimateWeaponProgressFilterForm(UpgradeableEntityProgressFilterForm):
    """Validate filters for the Ultimate Weapons Progress dashboard."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the form with Ultimate Weapon labels."""

        super().__init__(*args, entity_label_plural="ultimate weapons", **kwargs)


class BattleHistoryFilterForm(forms.Form):
    """Validate filter controls for the Battle History dashboard."""

    tier = forms.IntegerField(required=False, min_value=1, label="Tier")
    killed_by = forms.CharField(required=False, label="Killed by")
    goal = forms.CharField(required=False, label="Goal")
    include_tournaments = forms.BooleanField(
        required=False,
        label="Include tournaments",
        help_text="By default, tournament runs are excluded from the table and diagnostics.",
    )
    preset = forms.ModelChoiceField(
        required=False,
        queryset=Preset.objects.none(),
        label="Preset",
        empty_label="All presets",
    )
    sort = forms.ChoiceField(
        required=False,
        choices=(
            ("-run_progress__battle_date", "Battle date (newest)"),
            ("run_progress__battle_date", "Battle date (oldest)"),
            ("-run_progress__tier", "Tier (high → low)"),
            ("run_progress__tier", "Tier (low → high)"),
            ("-run_progress__wave", "Wave (high → low)"),
            ("run_progress__wave", "Wave (low → high)"),
            ("run_progress__killed_by", "Killed by (A → Z)"),
            ("-run_progress__killed_by", "Killed by (Z → A)"),
            ("-run_progress__coins_earned", "Coins earned (high → low)"),
            ("run_progress__coins_earned", "Coins earned (low → high)"),
            ("-run_progress__cash_earned", "Cash earned (high → low)"),
            ("run_progress__cash_earned", "Cash earned (low → high)"),
            ("-run_progress__interest_earned", "Interest earned (high → low)"),
            ("run_progress__interest_earned", "Interest earned (low → high)"),
            ("-run_progress__cells_earned", "Cells earned (high → low)"),
            ("run_progress__cells_earned", "Cells earned (low → high)"),
            ("-run_progress__reroll_shards_earned", "Reroll shards (high → low)"),
            ("run_progress__reroll_shards_earned", "Reroll shards (low → high)"),
            ("-run_progress__gem_blocks_tapped", "Gem blocks (high → low)"),
            ("run_progress__gem_blocks_tapped", "Gem blocks (low → high)"),
            ("-coins_per_hour", "Coins/hour (high → low)"),
            ("coins_per_hour", "Coins/hour (low → high)"),
            ("run_progress__preset__name", "Preset (A → Z)"),
            ("-run_progress__preset__name", "Preset (Z → A)"),
            ("-parsed_at", "Imported (newest)"),
        ),
        label="Sort",
    )

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the filter form with a preset queryset."""

        player: Player | None = kwargs.pop("player", None)
        super().__init__(*args, **kwargs)
        if player is None:
            self.fields["preset"].queryset = Preset.objects.order_by("name")
        else:
            self.fields["preset"].queryset = Preset.objects.filter(player=player).order_by("name")


class BattleHistoryPresetUpdateForm(forms.Form):
    """Validate preset updates for a single Battle Report row."""

    action = forms.CharField(widget=forms.HiddenInput())
    next = forms.CharField(required=False, widget=forms.HiddenInput())
    progress_id = forms.IntegerField(widget=forms.HiddenInput())
    preset = forms.ModelChoiceField(
        required=False,
        queryset=Preset.objects.none(),
        label="Preset",
        empty_label="No preset",
    )

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the form with a player-scoped preset queryset."""

        player: Player = kwargs.pop("player")
        super().__init__(*args, **kwargs)
        self.fields["preset"].queryset = Preset.objects.filter(player=player).order_by("name")


class CardsFilterForm(forms.Form):
    """Validate preset filters for the Cards dashboard."""

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Optional: filter by card name.",
    )
    maxed = forms.ChoiceField(
        required=False,
        choices=(
            ("", "All cards"),
            ("maxed", "Maxed only"),
            ("unmaxed", "Unmaxed only"),
        ),
        label="Maxed filter",
        help_text="Optional: filter to cards that are fully maxed or not maxed yet.",
    )
    presets = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Preset.objects.none(),
        label="Presets",
        widget=forms.SelectMultiple(attrs={"size": 6}),
        help_text="Optional: show only cards tagged with these presets.",
    )
    sort = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the filter form with a player-scoped preset queryset."""

        player: Player = kwargs.pop("player")
        super().__init__(*args, **kwargs)
        self.fields["presets"].queryset = Preset.objects.filter(player=player).order_by("name")

    def clean_q(self) -> str:
        """Normalize the optional search query."""

        return (self.cleaned_data.get("q") or "").strip()


class CardInventoryUpdateForm(forms.Form):
    """Validate inline updates for a card inventory count."""

    action = forms.CharField(widget=forms.HiddenInput())
    next = forms.CharField(required=False, widget=forms.HiddenInput())
    card_id = forms.IntegerField(widget=forms.HiddenInput())
    inventory_count = forms.IntegerField(required=True, min_value=0, label="Inventory")


class CardPresetUpdateForm(forms.Form):
    """Validate inline updates for card preset assignments."""

    action = forms.CharField(widget=forms.HiddenInput())
    next = forms.CharField(required=False, widget=forms.HiddenInput())
    card_id = forms.IntegerField(widget=forms.HiddenInput())
    presets = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Preset.objects.none(),
        label="Presets",
        widget=forms.SelectMultiple(attrs={"size": 4}),
    )
    new_preset_name = forms.CharField(required=False, label="New preset")

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the update form with a player-scoped preset queryset."""

        player: Player = kwargs.pop("player")
        super().__init__(*args, **kwargs)
        self.fields["presets"].queryset = Preset.objects.filter(player=player).order_by("name")

    def clean_new_preset_name(self) -> str:
        """Normalize the optional new preset name."""

        return (self.cleaned_data.get("new_preset_name") or "").strip()


class CardPresetBulkUpdateForm(forms.Form):
    """Validate bulk preset assignments for multiple cards.

    This form is used by the Cards dashboard bulk edit controls. It is intended
    to add preset tags to a set of selected cards without removing existing
    tags.
    """

    action = forms.CharField(widget=forms.HiddenInput())
    next = forms.CharField(required=False, widget=forms.HiddenInput())
    card_ids = forms.TypedMultipleChoiceField(
        required=True,
        coerce=int,
        choices=(),
        widget=forms.MultipleHiddenInput(),
    )
    presets = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Preset.objects.none(),
        label="Presets",
        widget=forms.SelectMultiple(attrs={"size": 4}),
    )
    new_preset_name = forms.CharField(required=False, label="New preset")

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the bulk form with player-scoped choices and presets."""

        player: Player = kwargs.pop("player")
        super().__init__(*args, **kwargs)
        self.fields["presets"].queryset = Preset.objects.filter(player=player).order_by("name")
        self.fields["card_ids"].choices = tuple(
            (card_id, str(card_id))
            for card_id in player.cards.order_by("id").values_list("id", flat=True)
        )

    def clean_new_preset_name(self) -> str:
        """Normalize the optional new preset name."""

        return (self.cleaned_data.get("new_preset_name") or "").strip()


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


class ChartBuilderForm(forms.Form):
    """Validate constrained Chart Builder selections.

    The Chart Builder produces a runtime ChartConfig (not persisted) that is
    validated and rendered using the same pipeline as built-in charts.
    """

    metric_keys = forms.MultipleChoiceField(
        required=True,
        choices=(),
        label="Metrics",
        widget=forms.SelectMultiple(attrs={"size": 10}),
        help_text="Select one or more metrics. Metrics must share units and category.",
    )
    chart_type = forms.ChoiceField(
        required=True,
        choices=(("line", "Line"), ("bar", "Bar"), ("donut", "Donut")),
        label="Chart type",
    )
    group_by = forms.ChoiceField(
        required=True,
        choices=(("time", "Time"), ("tier", "Tier"), ("preset", "Preset")),
        label="Group by",
    )
    comparison = forms.ChoiceField(
        required=True,
        choices=(("none", "None"), ("before_after", "Before/After (two windows)"), ("run_vs_run", "Run vs Run")),
        label="Comparison",
    )
    smoothing = forms.ChoiceField(
        required=True,
        choices=(("none", "None"), ("rolling_avg", "Rolling average")),
        label="Smoothing",
    )

    run_a = GameDataChoiceField(required=False, queryset=BattleReport.objects.none(), label="Run A")
    run_b = GameDataChoiceField(required=False, queryset=BattleReport.objects.none(), label="Run B")

    window_a_start = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Window A start")
    window_a_end = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Window A end")
    window_b_start = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Window B start")
    window_b_end = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Window B end")

    def __init__(self, *args, **kwargs) -> None:
        """Initialize choices from the MetricSeries registry and run queryset."""

        runs_queryset = kwargs.pop("runs_queryset", None)
        super().__init__(*args, **kwargs)

        self.fields["metric_keys"].choices = [
            (spec.key, f"{spec.label} ({spec.unit})") for spec in DEFAULT_REGISTRY.list()
        ]

        if runs_queryset is None:
            runs_queryset = BattleReport.objects.select_related("run_progress").order_by(
                "-run_progress__battle_date", "-parsed_at"
            )
        self.fields["run_a"].queryset = runs_queryset
        self.fields["run_b"].queryset = runs_queryset

    def clean(self) -> dict[str, object]:
        """Enforce the constrained Chart Builder contract."""

        cleaned = super().clean()

        metric_keys = tuple(cleaned.get("metric_keys") or ())
        chart_type = str(cleaned.get("chart_type") or "line")
        group_by = str(cleaned.get("group_by") or "time")
        comparison = str(cleaned.get("comparison") or "none")
        smoothing = str(cleaned.get("smoothing") or "none")

        if chart_type == "donut" and len(metric_keys) < 2:
            self.add_error("metric_keys", "Donut charts require at least two metrics.")

        if chart_type == "donut" and group_by != "time":
            self.add_error("group_by", "Donut charts do not support grouping.")

        if chart_type == "donut" and comparison != "none":
            self.add_error("comparison", "Donut charts do not support comparisons.")

        if comparison != "none" and group_by != "time":
            self.add_error("group_by", "Two-scope comparisons require group_by=Time.")

        if smoothing == "rolling_avg":
            unsupported = []
            for key in metric_keys:
                spec = DEFAULT_REGISTRY.get(key)
                if spec is None:
                    continue
                if "moving_average" not in spec.allowed_transforms:
                    unsupported.append(key)
            if unsupported:
                self.add_error(
                    "smoothing",
                    f"Rolling average is not supported for: {', '.join(sorted(unsupported))}.",
                )

        if comparison == "run_vs_run":
            if cleaned.get("run_a") is None or cleaned.get("run_b") is None:
                self.add_error("run_a", "Select two runs for run vs run.")
                self.add_error("run_b", "Select two runs for run vs run.")

        if comparison == "before_after":
            required = ("window_a_start", "window_a_end", "window_b_start", "window_b_end")
            missing = [key for key in required if not cleaned.get(key)]
            if missing:
                for key in missing:
                    self.add_error(key, "Required for before/after comparisons.")

        return cleaned

    def selection(self) -> ChartBuilderSelection:
        """Return a typed selection for building a runtime ChartConfig.

        Returns:
            ChartBuilderSelection derived from validated form values.

        Raises:
            ValueError: If the form is invalid.
        """

        if not self.is_valid():
            raise ValueError("ChartBuilderForm must be valid before building selections.")

        metric_keys = tuple(self.cleaned_data.get("metric_keys") or ())
        chart_type = str(self.cleaned_data.get("chart_type") or "line")
        group_by = str(self.cleaned_data.get("group_by") or "time")
        comparison = str(self.cleaned_data.get("comparison") or "none")
        smoothing = str(self.cleaned_data.get("smoothing") or "none")
        scope_a = None
        scope_b = None
        if comparison == "run_vs_run":
            run_a = self.cleaned_data.get("run_a")
            run_b = self.cleaned_data.get("run_b")
            if run_a is not None and run_b is not None:
                scope_a, scope_b = build_run_vs_run_scopes(run_a_id=int(run_a.id), run_b_id=int(run_b.id))
        if comparison == "before_after":
            a_start = self.cleaned_data.get("window_a_start")
            a_end = self.cleaned_data.get("window_a_end")
            b_start = self.cleaned_data.get("window_b_start")
            b_end = self.cleaned_data.get("window_b_end")
            if a_start and a_end and b_start and b_end:
                scope_a, scope_b = build_before_after_scopes(
                    window_a_start=a_start,
                    window_a_end=a_end,
                    window_b_start=b_start,
                    window_b_end=b_end,
                )

        return ChartBuilderSelection(
            metric_keys=metric_keys,
            chart_type=chart_type,  # type: ignore[arg-type]
            group_by=group_by,  # type: ignore[arg-type]
            comparison=comparison,  # type: ignore[arg-type]
            smoothing=smoothing,  # type: ignore[arg-type]
            scope_a=scope_a,
            scope_b=scope_b,
        )

    def scopes(self) -> tuple[ChartScopeDTO, ChartScopeDTO] | None:
        """Return two-scope DTOs for before/after and run-vs-run comparisons.

        Returns:
            A tuple of (scope_a, scope_b) when comparison is enabled, otherwise None.

        Raises:
            ValueError: When the form is invalid.
        """

        selection = self.selection()
        if selection.comparison == "none":
            return None
        if selection.scope_a is None or selection.scope_b is None:
            return None
        return (
            ChartScopeDTO(
                label=selection.scope_a.label,
                run_id=selection.scope_a.run_id,
                start_date=selection.scope_a.start_date,
                end_date=selection.scope_a.end_date,
            ),
            ChartScopeDTO(
                label=selection.scope_b.label,
                run_id=selection.scope_b.run_id,
                start_date=selection.scope_b.start_date,
                end_date=selection.scope_b.end_date,
            ),
        )


class GoalsFilterForm(forms.Form):
    """Validate filter controls for the Goals dashboard."""

    goal_type = forms.ChoiceField(
        required=False,
        choices=(("", "All"), *GoalType.choices),
        label="Category",
    )
    show_completed = forms.BooleanField(
        required=False,
        label="Show completed",
        help_text="Completed goals are hidden by default.",
    )


class GoalTargetUpdateForm(forms.Form):
    """Validate create/update requests for an individual goal target."""

    goal_type = forms.ChoiceField(choices=GoalType.choices)
    goal_key = forms.CharField(max_length=240)
    target_level = forms.IntegerField(min_value=1)
    label = forms.CharField(max_length=120, required=False)
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))

    def __init__(self, *args, max_level: int | None = None, **kwargs) -> None:
        """Initialize with an optional max level for validation."""

        super().__init__(*args, **kwargs)
        self._max_level = max_level

    def clean_target_level(self) -> int | None:
        """Validate target level against the optional max level constraint."""

        raw = self.cleaned_data.get("target_level")
        if raw is None:
            return None
        if self._max_level is not None and raw > self._max_level:
            raise forms.ValidationError(f"Target level cannot exceed max level {self._max_level}.")
        return int(raw)
