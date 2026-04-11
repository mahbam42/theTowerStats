"""Forms for core UI workflows.

Phase 1 requires:
- a paste/import form for raw Battle Report text,
- a date-range filter form for the first time-series chart.
"""

from __future__ import annotations

from datetime import date
import json
import re
from typing import Iterable

from django import forms

from analysis.event_windows import current_event_window
from analysis.chart_config_dto import ChartScopeDTO
from analysis.explore_registry import build_explore_metric_registry, list_explore_breakdowns, list_explore_metrics
from analysis.series_registry import DEFAULT_REGISTRY, allowed_chart_builder_aggregations
from core.charting.configs import default_selected_chart_ids, list_selectable_chart_configs
from core.charting.builder import (
    ChartBuilderSelection,
    build_before_after_scopes,
    build_run_vs_run_scopes,
)
from core.parsers.battle_report import _iter_label_value_lines
from core.tournament import parse_tier_or_tournament, tier_filter_value, tournament_filter_value
from definitions.models import BotDefinition, GuardianChipDefinition, PatchBoundary, UltimateWeaponDefinition
from gamedata.models import BattleReport, BattleReportProgress, TOURNAMENT_RANK_CHOICES
from player_state.models import ChartSnapshot, GoalType, Player, Preset


class BattleReportImportForm(forms.Form):
    """Validate user-submitted raw Battle Report text."""

    _BATTLE_REPORT_HEADER_RE = r"(?im)^[^\S\n]*Battle Report[^\S\n]*$"

    raw_text = forms.CharField(
        label="Battle Report",
        widget=forms.Textarea(attrs={"rows": 12, "cols": 80}),
        help_text="Paste exactly one Battle Report from The Tower.",
    )
    preset_name = forms.ChoiceField(
        required=False,
        label="Preset",
        help_text="Optional label applied to this run.",
        choices=(),
    )
    new_preset_name = forms.CharField(
        required=False,
        label="New preset name",
        help_text='Use when "Create new preset" is selected.',
    )
    is_tournament = forms.BooleanField(
        required=False,
        label="Tournament run",
        help_text="Enable when this run was a tournament round but the pasted report text does not indicate it.",
    )
    tournament_rank = forms.ChoiceField(
        required=False,
        choices=(("", "Select a rank"),) + TOURNAMENT_RANK_CHOICES,
        label="Tournament rank",
        help_text="Required when Tournament run is enabled.",
    )

    def __init__(self, *args: object, player: Player | None = None, **kwargs: object) -> None:
        """Initialize preset choices with the player's saved presets."""

        super().__init__(*args, **kwargs)
        self.fields["preset_name"].choices = self._preset_choices(player)

    def _preset_choices(self, player: Player | None) -> tuple[tuple[str, str], ...]:
        """Return preset dropdown choices for the provided player."""

        choices: list[tuple[str, str]] = [("", "No preset")]
        if player is not None:
            presets = Preset.objects.filter(player=player).order_by("name")
            choices.extend((preset.name, preset.name) for preset in presets)
        choices.append(("__new__", "Create new preset"))
        return tuple(choices)

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

        label_counts: dict[str, int] = {"Battle Date": 0, "Tier": 0, "Wave": 0, "Real Time": 0}
        for label, _ in _iter_label_value_lines(validation_text):
            normalized = label.strip().casefold()
            if normalized == "battle date":
                label_counts["Battle Date"] += 1
            elif normalized == "tier":
                label_counts["Tier"] += 1
            elif normalized == "wave":
                label_counts["Wave"] += 1
            elif normalized == "real time":
                label_counts["Real Time"] += 1

        required_once = ("Tier", "Wave", "Real Time")
        missing_required = [label for label in required_once if label_counts[label] != 1]
        if missing_required:
            labels = ", ".join(missing_required)
            raise forms.ValidationError(f"Paste exactly one Battle Report ({labels} must appear once).")

        duplicates = [label for label, count in label_counts.items() if count > 1]
        if duplicates:
            raise forms.ValidationError(f"Duplicate headers detected: {', '.join(duplicates)}.")
        return raw_text

    def clean(self) -> dict[str, object]:
        """Validate tournament metadata requirements and preset selection."""

        cleaned = super().clean()
        preset_choice = (cleaned.get("preset_name") or "").strip()
        new_preset_name = (cleaned.get("new_preset_name") or "").strip()
        if preset_choice == "__new__":
            if not new_preset_name:
                self.add_error("new_preset_name", "Enter a new preset name.")
            else:
                cleaned["preset_name"] = new_preset_name
        elif new_preset_name:
            cleaned["new_preset_name"] = ""

        is_tournament = bool(cleaned.get("is_tournament"))
        tournament_rank = (cleaned.get("tournament_rank") or "").strip()
        if is_tournament and not tournament_rank:
            self.add_error("tournament_rank", "Select a tournament rank.")
        if not is_tournament:
            cleaned["tournament_rank"] = ""
        return cleaned


class PatchBoundaryMultipleChoiceField(forms.ModelMultipleChoiceField):
    """A ModelMultipleChoiceField with patch label + date formatting."""

    def label_from_instance(self, obj) -> str:  # type: ignore[override]
        """Render the choice label using patch label and boundary date."""

        label = (obj.label or "").strip()
        date_label = obj.boundary_date.isoformat()
        if label:
            return f"{label} ({date_label})"
        return date_label


class ChartContextForm(forms.Form):
    """Validate contextual filters and chart overlay options."""

    charts = forms.MultipleChoiceField(
        required=False,
        choices=(),
        label="Charts",
        help_text="Select one or more charts to display.",
        widget=forms.SelectMultiple(attrs={"size": 12}),
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
    patch_boundaries = PatchBoundaryMultipleChoiceField(
        required=False,
        queryset=PatchBoundary.objects.none(),
        label="Patch boundary",
        widget=forms.SelectMultiple(attrs={"size": 4}),
        help_text="Optional patch boundary window filter.",
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
    tier = forms.ChoiceField(
        required=False,
        choices=(),
        label="Tier",
        help_text="Optional tier or tournament filter.",
    )
    preset = forms.ModelChoiceField(
        required=False,
        queryset=Preset.objects.none(),
        label="Preset",
        empty_label="All presets",
    )
    exclude_presets = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Preset.objects.none(),
        label="Exclude presets",
        help_text="Optional: remove runs with these presets from charts.",
        widget=forms.SelectMultiple(attrs={"size": 4}),
    )
    context_snapshot = forms.ModelChoiceField(
        required=False,
        queryset=ChartSnapshot.objects.none(),
        label="Snapshot",
        empty_label="No snapshot filter",
        help_text="Optional snapshot filter applied alongside other context controls.",
    )
    past_runs = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=365,
        label="Past N runs",
        help_text="Optional filter for the most recent N runs in scope.",
    )
    include_tournaments = forms.BooleanField(
        required=False,
        label="Include tournaments",
        help_text="By default, tournament runs are excluded from analytics and charts.",
    )
    include_hidden = forms.BooleanField(
        required=False,
        label="Include hidden reports",
        help_text="Hidden Battle Reports are excluded from charts by default.",
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
        self._tournament_filter: str | None = None
        if player is None:
            self.fields["preset"].queryset = Preset.objects.order_by("name")
            self.fields["exclude_presets"].queryset = Preset.objects.order_by("name")
        else:
            self.fields["preset"].queryset = Preset.objects.filter(player=player).order_by("name")
            self.fields["exclude_presets"].queryset = (
                Preset.objects.filter(player=player).order_by("name")
            )
        self.fields["ultimate_weapon"].queryset = UltimateWeaponDefinition.objects.order_by("name")
        self.fields["guardian_chip"].queryset = GuardianChipDefinition.objects.order_by("name")
        self.fields["bot"].queryset = BotDefinition.objects.order_by("name")
        self.fields["patch_boundaries"].queryset = PatchBoundary.objects.order_by("boundary_date")
        if player is None:
            self.fields["context_snapshot"].queryset = ChartSnapshot.objects.none()
        else:
            self.fields["context_snapshot"].queryset = (
                ChartSnapshot.objects.filter(player=player, target="charts").order_by("name")
            )
        tier_queryset = BattleReportProgress.objects.filter(tier__isnull=False)
        if player is not None:
            tier_queryset = tier_queryset.filter(player=player)
        recorded_tiers = (
            tier_queryset.order_by("tier").values_list("tier", flat=True).distinct()
        )
        tier_choices: list[tuple[str, str]] = [("", "All tiers")]
        tier_choices.extend(
            (tier_filter_value(int(tier)), f"Tier {int(tier)}") for tier in recorded_tiers
        )
        tier_choices.append((tournament_filter_value(None), "Tournament (all)"))
        tier_choices.extend(
            (tournament_filter_value(key), f"Tournament: {label}")
            for key, label in TOURNAMENT_RANK_CHOICES
        )
        self.fields["tier"].choices = tier_choices
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
            description = (chart.description or f"Chart showing {chart.title}.").strip()
            grouped.setdefault(group, []).append(
                (chart.id, f"{chart.title} — {chart.chart_type} — {description}")
            )
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
        self.fields["charts"].widget.attrs["title"] = "Select one or more charts to display."
        self.fields["include_tournaments"].widget.attrs["title"] = (
            "Include tournament runs in charts and derived metrics."
        )
        self.fields["include_hidden"].widget.attrs["title"] = (
            "Include Battle Reports marked as hidden."
        )
        self.fields["window_kind"].widget.attrs["title"] = (
            "Limit the chart scope to the most recent runs or days after other filters."
        )
        self.fields["window_n"].widget.attrs["title"] = (
            "Number of runs or days used by the rolling window."
        )
        self.fields["ultimate_weapon"].widget.attrs["title"] = (
            "Filter to runs where the selected ultimate weapon appears."
        )
        self.fields["guardian_chip"].widget.attrs["title"] = (
            "Filter to runs where the selected guardian chip appears."
        )
        self.fields["bot"].widget.attrs["title"] = "Filter to runs where the selected bot appears."
        self.fields["moving_average_window"].widget.attrs["title"] = (
            "Smooth charts by averaging over this many points."
        )
        self.fields["granularity"].widget.attrs["title"] = (
            "Choose whether charts show one point per date or per run."
        )

    def clean_tier(self) -> int | None:
        """Parse tier selections into tier or tournament filters."""

        value = self.cleaned_data.get("tier")
        tier_value, tournament_filter = parse_tier_or_tournament(str(value or ""))
        if value and tier_value is None and tournament_filter is None:
            raise forms.ValidationError("Select a valid tier.")
        self._tournament_filter = tournament_filter
        return tier_value

    def clean(self) -> dict[str, object]:
        """Apply Event-window defaults and dashboard invariants."""

        cleaned = super().clean()
        tournament_filter = self._tournament_filter
        if tournament_filter:
            cleaned["tournament_filter"] = tournament_filter
            cleaned["include_tournaments"] = True
        else:
            cleaned["tournament_filter"] = None
        if not cleaned.get("start_date") and not cleaned.get("end_date"):
            window = current_event_window(target=self._today)
            cleaned["start_date"] = window.start
            cleaned["end_date"] = window.end
        if not cleaned.get("charts"):
            cleaned["charts"] = list(default_selected_chart_ids())
        if not cleaned.get("granularity"):
            cleaned["granularity"] = "per_run"
        past_runs = cleaned.get("past_runs")
        if past_runs:
            cleaned["window_kind"] = "last_runs"
            cleaned["window_n"] = past_runs
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
    snapshot = forms.ModelChoiceField(
        required=False,
        queryset=ChartSnapshot.objects.none(),
        label="Snapshot",
        empty_label="All snapshots",
    )
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
            ("-run_progress__is_tournament", "Tournament (Yes → No)"),
            ("run_progress__is_tournament", "Tournament (No → Yes)"),
            ("-is_hidden", "Hidden (Yes → No)"),
            ("is_hidden", "Hidden (No → Yes)"),
            ("-run_progress__wave", "Wave (high → low)"),
            ("run_progress__wave", "Wave (low → high)"),
            ("-run_progress__real_time_seconds", "Real time (high → low)"),
            ("run_progress__real_time_seconds", "Real time (low → high)"),
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
            ("-derived_metrics__values__recovery_packages", "Recovery packages (high → low)"),
            ("derived_metrics__values__recovery_packages", "Recovery packages (low → high)"),
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
        if player is None:
            self.fields["snapshot"].queryset = ChartSnapshot.objects.none()
        else:
            self.fields["snapshot"].queryset = (
                ChartSnapshot.objects.filter(player=player, target="charts").order_by("name")
            )


class LifetimeStatsFilterForm(forms.Form):
    """Validate date-range selections for Lifetime Stats."""

    RANGE_CHOICES = (
        ("all", "All time"),
        ("event", "Current event window"),
        ("custom", "Custom date range"),
    )

    range_mode = forms.ChoiceField(
        required=False,
        choices=RANGE_CHOICES,
        label="Range",
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

    def __init__(self, *args: object, today: date | None = None, **kwargs: object) -> None:
        """Store the current date for Event window defaults."""

        super().__init__(*args, **kwargs)
        self._today = today or date.today()

    def clean(self) -> dict[str, object]:
        """Apply Event window defaults and custom range validation."""

        cleaned = super().clean()
        mode = (cleaned.get("range_mode") or "all").strip().casefold()
        cleaned["range_mode"] = mode
        if mode == "event":
            window = current_event_window(target=self._today)
            cleaned["start_date"] = window.start
            cleaned["end_date"] = window.end
            return cleaned
        if mode == "custom":
            start = cleaned.get("start_date")
            end = cleaned.get("end_date")
            if not start or not end:
                self.add_error("start_date", "Provide both start and end dates.")
                self.add_error("end_date", "Provide both start and end dates.")
            return cleaned
        cleaned["start_date"] = None
        cleaned["end_date"] = None
        return cleaned


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
        wave = getattr(progress, "wave", None)
        date_label = getattr(battle_date, "date", lambda: None)()
        time_label = getattr(battle_date, "strftime", lambda _fmt: None)("%H:%M:%S")
        tier_label = f"T{tier}" if tier is not None else "T?"
        wave_label = f"W{wave}" if wave is not None else "W?"
        if date_label is None:
            date_label = obj.parsed_at.date()
        if time_label is None:
            time_label = obj.parsed_at.strftime("%H:%M:%S")
        return f"{tier_label} • {wave_label} • {date_label.isoformat()} {time_label}"


class GameDataMultipleChoiceField(forms.ModelMultipleChoiceField):
    """A ModelMultipleChoiceField with a human-readable label for imported runs."""

    def label_from_instance(self, obj) -> str:  # type: ignore[override]
        """Render the choice label using run metadata when available."""

        progress = getattr(obj, "run_progress", None)
        battle_date = getattr(progress, "battle_date", None)
        tier = getattr(progress, "tier", None)
        wave = getattr(progress, "wave", None)
        date_label = getattr(battle_date, "date", lambda: None)()
        time_label = getattr(battle_date, "strftime", lambda _fmt: None)("%H:%M:%S")
        tier_label = f"T{tier}" if tier is not None else "T?"
        wave_label = f"W{wave}" if wave is not None else "W?"
        if date_label is None:
            date_label = obj.parsed_at.date()
        if time_label is None:
            time_label = obj.parsed_at.strftime("%H:%M:%S")
        return f"{tier_label} • {wave_label} • {date_label.isoformat()} {time_label}"


class GameSpeedCalculatorForm(forms.Form):
    """Validate inputs for the Game Speed calculator."""

    GAME_SPEED_CHOICES = (
        ("1", "1x"),
        ("2", "2x"),
        ("2.5", "2.5x"),
        ("3", "3x"),
        ("3.5", "3.5x"),
        ("4", "4x"),
        ("4.5", "4.5x"),
        ("5", "5x"),
        ("6.3", "6.3x"),
    )

    run = GameDataChoiceField(
        required=True,
        queryset=BattleReport.objects.none(),
        label="Run",
        empty_label=None,
    )
    game_speed = forms.ChoiceField(
        required=True,
        choices=GAME_SPEED_CHOICES,
        label="Game speed",
    )
    wave_accelerator_active = forms.BooleanField(
        required=False,
        label="Wave Accelerator active",
    )

    def __init__(self, *args: object, runs: Iterable[BattleReport] | None = None, **kwargs: object) -> None:
        """Initialize run choices with the supplied queryset."""

        super().__init__(*args, **kwargs)
        if runs is not None:
            self.fields["run"].queryset = runs


class LabsSpeedupCalculatorForm(forms.Form):
    """Validate inputs for the Labs Speed Up calculator."""

    LAB_GOAL_CHOICES = (
        ("goal_12d", "12 days"),
        ("goal_30d", "30 days"),
        ("goal_89d", "89d 19h 33m 20s"),
    )

    labs_unlocked = forms.IntegerField(
        required=True,
        min_value=1,
        max_value=5,
        label="Labs unlocked",
    )
    progress_days = forms.IntegerField(required=False, min_value=0, label="Current days")
    progress_hours = forms.IntegerField(required=False, min_value=0, max_value=23, label="Current hours")
    progress_minutes = forms.IntegerField(required=False, min_value=0, max_value=59, label="Current minutes")
    progress_seconds = forms.IntegerField(required=False, min_value=0, max_value=59, label="Current seconds")
    goal = forms.ChoiceField(
        required=True,
        choices=LAB_GOAL_CHOICES,
        label="Goal",
    )

    def clean(self) -> dict[str, object]:
        """Normalize missing progress parts to zero."""

        cleaned = super().clean()
        cleaned["progress_days"] = int(cleaned.get("progress_days") or 0)
        cleaned["progress_hours"] = int(cleaned.get("progress_hours") or 0)
        cleaned["progress_minutes"] = int(cleaned.get("progress_minutes") or 0)
        cleaned["progress_seconds"] = int(cleaned.get("progress_seconds") or 0)
        return cleaned


class ComparisonForm(forms.Form):
    """Validate run comparisons across multiple comparison modes.

    The Compare workflow supports:
    - multi-run scope A vs scope B (preferred),
    - window vs window,
    - run vs run (fallback, advice-disabled).
    """

    SUMMARY_FOCUS_CHOICES = (
        ("economy", "Economy"),
        ("damage", "Damage"),
        ("enemy_destruction", "Enemy Destruction"),
        ("efficiency", "Efficiency"),
    )

    scope_a_runs = GameDataMultipleChoiceField(
        required=False,
        queryset=BattleReport.objects.none(),
        label="Scope A runs",
        widget=forms.SelectMultiple(attrs={"size": 8}),
    )
    scope_b_runs = GameDataMultipleChoiceField(
        required=False,
        queryset=BattleReport.objects.none(),
        label="Scope B runs",
        widget=forms.SelectMultiple(attrs={"size": 8}),
    )
    scope_average = forms.BooleanField(
        required=False,
        initial=False,
        label="Average each scope",
    )

    summary_focus = forms.ChoiceField(
        required=False,
        initial="economy",
        choices=SUMMARY_FOCUS_CHOICES,
        label="Summary focus",
    )

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

        self.fields["scope_a_runs"].queryset = runs_queryset
        self.fields["scope_b_runs"].queryset = runs_queryset
        self.fields["run_a"].queryset = runs_queryset
        self.fields["run_b"].queryset = runs_queryset

    def clean_summary_focus(self) -> str:
        """Default the summary focus to Economy when unspecified."""

        focus = (self.cleaned_data.get("summary_focus") or "").strip()
        return focus or "economy"

    def clean_scope_average(self) -> bool:
        """Default the scope average toggle to False when unspecified."""

        return bool(self.cleaned_data.get("scope_average") or False)


class BattleHistoryColumnPreferenceForm(forms.Form):
    """Validate Battle History column visibility selections."""

    columns = forms.MultipleChoiceField(
        required=False,
        choices=(),
        widget=forms.CheckboxSelectMultiple,
        label="Visible columns",
    )

    def __init__(self, *args, column_choices: tuple[tuple[str, str], ...], **kwargs) -> None:
        """Initialize with the available column choices."""

        super().__init__(*args, **kwargs)
        self.fields["columns"].choices = column_choices

    def clean_columns(self) -> tuple[str, ...]:
        """Require at least one visible column."""

        selected = tuple(self.cleaned_data.get("columns") or ())
        if not selected:
            raise forms.ValidationError("Select at least one column.")
        return selected


class ChartFavoritesForm(forms.Form):
    """Validate ordered favorite chart selections."""

    favorite_chart_ids = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, available_chart_ids: set[str], **kwargs) -> None:
        """Initialize with the available chart ids."""

        super().__init__(*args, **kwargs)
        self._available_chart_ids = available_chart_ids

    def clean_favorite_chart_ids(self) -> tuple[str, ...]:
        """Return a de-duplicated ordered list of chart ids."""

        raw = self.cleaned_data.get("favorite_chart_ids") or "[]"
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise forms.ValidationError("Invalid favorites payload.") from exc
        if not isinstance(parsed, list):
            raise forms.ValidationError("Favorites must be an ordered list.")
        cleaned: list[str] = []
        for entry in parsed:
            key = str(entry)
            if key not in self._available_chart_ids:
                raise forms.ValidationError(f"Unknown chart id: {key}.")
            if key in cleaned:
                continue
            cleaned.append(key)
        return tuple(cleaned)


class ChartBuilderSavedConfigForm(forms.Form):
    """Validate metadata for saved Chart Builder configurations."""

    saved_id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    name = forms.CharField(required=True, max_length=120, label="Saved chart name")

    def clean_name(self) -> str:
        """Require a non-empty saved chart name."""

        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise forms.ValidationError("Saved chart name is required.")
        return name


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
        help_text="Select metrics for the chart. Time-based charts require matching units and category.",
    )
    chart_type = forms.ChoiceField(
        required=True,
        choices=(("line", "Line"), ("area", "Area"), ("bar", "Bar"), ("scatter", "Scatter"), ("donut", "Donut")),
        label="Chart type",
    )
    x_axis = forms.ChoiceField(
        required=True,
        choices=(("time", "Time"), ("metric", "Metric vs metric")),
        label="X axis",
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
    aggregation = forms.ChoiceField(
        required=False,
        choices=(("sum", "Sum"), ("avg", "Average")),
        label="Aggregation",
        help_text="Optional override for how values are aggregated.",
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
        self.fields["x_axis"].initial = "time"

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
        x_axis = str(cleaned.get("x_axis") or "time")
        group_by = str(cleaned.get("group_by") or "time")
        comparison = str(cleaned.get("comparison") or "none")
        smoothing = str(cleaned.get("smoothing") or "none")
        aggregation = str(cleaned.get("aggregation") or "")

        if chart_type == "donut" and len(metric_keys) < 2:
            self.add_error("metric_keys", "Donut charts require at least two metrics.")

        if chart_type == "donut" and group_by != "time":
            self.add_error("group_by", "Donut charts do not support grouping.")

        if chart_type == "donut" and comparison != "none":
            self.add_error("comparison", "Donut charts do not support comparisons.")

        if chart_type == "scatter" and x_axis != "metric":
            self.add_error("x_axis", "Scatter charts require metric-vs-metric plotting.")

        if x_axis == "metric":
            if chart_type == "donut":
                self.add_error("x_axis", "Metric-vs-metric plotting does not support donut charts.")
            if len(metric_keys) != 2:
                self.add_error("metric_keys", "Metric-vs-metric plotting requires exactly two metrics.")
            if group_by != "time":
                self.add_error("group_by", "Metric-vs-metric plotting does not support grouping.")
            if comparison != "none":
                self.add_error("comparison", "Metric-vs-metric plotting does not support comparisons.")
            if smoothing != "none":
                self.add_error("smoothing", "Metric-vs-metric plotting does not support smoothing.")

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

        allowed_aggregations = self._chart_builder_aggregation_options(metric_keys)
        if aggregation:
            if aggregation not in allowed_aggregations:
                self.add_error("aggregation", "Aggregation is not supported for the selected metrics.")
        elif allowed_aggregations:
            cleaned["aggregation"] = allowed_aggregations[0]

        return cleaned

    def _chart_builder_aggregation_options(self, metric_keys: tuple[str, ...]) -> tuple[str, ...]:
        """Return allowed aggregations for the selected metric keys."""

        options: set[str] | None = None
        for key in metric_keys:
            spec = DEFAULT_REGISTRY.get(key)
            if spec is None:
                continue
            allowed = {str(item) for item in allowed_chart_builder_aggregations(spec)}
            options = allowed if options is None else options & allowed
        if not options:
            return ()
        return tuple(agg for agg in ("sum", "avg") if agg in options)

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
        x_axis = str(self.cleaned_data.get("x_axis") or "time")
        group_by = str(self.cleaned_data.get("group_by") or "time")
        comparison = str(self.cleaned_data.get("comparison") or "none")
        smoothing = str(self.cleaned_data.get("smoothing") or "none")
        aggregation = self.cleaned_data.get("aggregation")
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
            x_axis=x_axis,  # type: ignore[arg-type]
            scope_a=scope_a,
            scope_b=scope_b,
            aggregation=str(aggregation) if aggregation else None,  # type: ignore[arg-type]
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


class ExploreQueryForm(forms.Form):
    """Validate Explore query builder selections."""

    query_id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    name = forms.CharField(required=True, max_length=120, label="Query name")

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
    patch_boundaries = PatchBoundaryMultipleChoiceField(
        required=False,
        queryset=PatchBoundary.objects.none(),
        label="Patch boundaries",
        widget=forms.SelectMultiple(attrs={"size": 4}),
    )
    tier_values = forms.MultipleChoiceField(
        required=False,
        choices=(),
        label="Tier (multi-select)",
        widget=forms.SelectMultiple(attrs={"size": 6}),
    )
    tier_min = forms.IntegerField(required=False, min_value=1, label="Tier minimum")
    tier_max = forms.IntegerField(required=False, min_value=1, label="Tier maximum")
    wave_min = forms.IntegerField(required=False, min_value=1, label="Wave minimum")
    wave_max = forms.IntegerField(required=False, min_value=1, label="Wave maximum")
    death_cause = forms.ChoiceField(required=False, choices=(), label="Death cause")

    preset = forms.ModelChoiceField(
        required=False,
        queryset=Preset.objects.none(),
        label="Preset",
        empty_label="All presets",
    )
    snapshot = forms.ModelChoiceField(
        required=False,
        queryset=ChartSnapshot.objects.none(),
        label="Preset run (snapshot)",
        empty_label="No snapshot",
    )
    past_n_runs = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=365,
        label="Past N runs",
    )
    include_hidden = forms.BooleanField(
        required=False,
        label="Include hidden reports",
    )

    primary_breakdown = forms.ChoiceField(required=False, choices=(), label="Primary breakdown")
    secondary_breakdown = forms.ChoiceField(required=False, choices=(), label="Secondary breakdown")
    metric_key = forms.ChoiceField(required=True, choices=(), label="Metric")
    aggregation = forms.ChoiceField(
        required=True,
        choices=(("sum", "Sum"), ("count", "Count"), ("avg", "Average")),
        label="Aggregation",
    )
    percent_of_total = forms.BooleanField(
        required=False,
        label="Percent of total",
    )
    visualization = forms.ChoiceField(
        required=True,
        choices=(
            ("table", "Table"),
            ("bar", "Bar chart"),
            ("donut", "Donut chart"),
            ("kpi", "KPI card"),
        ),
        label="Output",
    )

    def __init__(self, *args, **kwargs) -> None:
        """Initialize Explore query choices from player data."""

        player: Player | None = kwargs.pop("player", None)
        super().__init__(*args, **kwargs)

        if player is None:
            self.fields["preset"].queryset = Preset.objects.order_by("name")
            self.fields["snapshot"].queryset = ChartSnapshot.objects.order_by("name")
            tier_queryset = BattleReportProgress.objects.filter(tier__isnull=False)
        else:
            self.fields["preset"].queryset = Preset.objects.filter(player=player).order_by("name")
            self.fields["snapshot"].queryset = ChartSnapshot.objects.filter(
                player=player, target="charts"
            ).order_by("name")
            tier_queryset = BattleReportProgress.objects.filter(player=player, tier__isnull=False)
        self.fields["patch_boundaries"].queryset = PatchBoundary.objects.order_by("boundary_date")

        recorded_tiers = (
            tier_queryset.order_by("tier").values_list("tier", flat=True).distinct()
        )
        tier_choices: list[tuple[str, str]] = []
        tier_choices.extend((str(int(tier)), f"Tier {int(tier)}") for tier in recorded_tiers)
        self.fields["tier_values"].choices = tier_choices

        death_queryset = BattleReportProgress.objects.filter(killed_by__isnull=False)
        if player is not None:
            death_queryset = death_queryset.filter(player=player)
        death_causes = sorted(
            {
                str(value).strip()
                for value in death_queryset.values_list("killed_by", flat=True).distinct()
                if value
            }
        )
        death_choices: list[tuple[str, str]] = [("", "Any cause")]
        death_choices.extend((cause, cause) for cause in death_causes)
        death_choices.append(("__missing__", "Not recorded"))
        self.fields["death_cause"].choices = death_choices

        explore_metrics = list_explore_metrics(build_explore_metric_registry())
        self.fields["metric_key"].choices = [
            (metric.key, f"{metric.label} ({metric.unit})") for metric in explore_metrics
        ]

        breakdowns = list_explore_breakdowns()
        breakdown_choices: list[tuple[str, str]] = [("", "No breakdown")]
        breakdown_choices.extend((entry.key, entry.label) for entry in breakdowns)
        self.fields["primary_breakdown"].choices = breakdown_choices
        self.fields["secondary_breakdown"].choices = breakdown_choices

    def clean(self) -> dict[str, object]:
        """Validate Explore query builder invariants."""

        cleaned = super().clean()
        primary = str(cleaned.get("primary_breakdown") or "")
        secondary = str(cleaned.get("secondary_breakdown") or "")
        visualization = str(cleaned.get("visualization") or "table")

        if primary and secondary and primary == secondary:
            self.add_error("secondary_breakdown", "Secondary breakdown must be different.")

        if visualization != "kpi" and not primary:
            self.add_error("primary_breakdown", "Select a primary breakdown.")

        if visualization == "donut" and secondary:
            self.add_error("secondary_breakdown", "Donut charts support one breakdown only.")

        percent_of_total = bool(cleaned.get("percent_of_total"))
        aggregation = str(cleaned.get("aggregation") or "sum")
        if percent_of_total and aggregation not in {"sum", "count"}:
            self.add_error("aggregation", "Percent-of-total requires sum or count aggregation.")
        if percent_of_total and visualization == "kpi":
            self.add_error("visualization", "Percent-of-total requires a breakdown output.")

        return cleaned


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
