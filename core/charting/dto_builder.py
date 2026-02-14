"""Chart Builder compilation from UI forms into ChartConfigDTO."""

from __future__ import annotations

from analysis.chart_config_dto import ChartConfigDTO, ChartContextDTO
from core.forms import ChartBuilderForm, ChartContextForm


def build_chart_config_dto(*, context_form: ChartContextForm, builder_form: ChartBuilderForm) -> ChartConfigDTO:
    """Compile validated UI forms into a ChartConfigDTO.

    Args:
        context_form: Validated ChartContextForm (filters used to scope runs).
        builder_form: Validated ChartBuilderForm (schema-driven chart settings).

    Returns:
        ChartConfigDTO containing both the builder configuration and context filters.

    Raises:
        ValueError: If either form is invalid.
    """

    if not context_form.is_valid() or not builder_form.is_valid():
        raise ValueError("Both context_form and builder_form must be valid before building ChartConfigDTO.")

    preset = context_form.cleaned_data.get("preset")
    excluded_presets = tuple(context_form.cleaned_data.get("exclude_presets") or ())
    patch_boundaries = tuple(context_form.cleaned_data.get("patch_boundaries") or ())
    context = ChartContextDTO(
        start_date=context_form.cleaned_data.get("start_date"),
        end_date=context_form.cleaned_data.get("end_date"),
        tier=context_form.cleaned_data.get("tier"),
        tournament_filter=context_form.cleaned_data.get("tournament_filter"),
        preset_id=(preset.id if preset is not None else None),
        excluded_preset_ids=tuple(
            preset_row.id for preset_row in excluded_presets if getattr(preset_row, "id", None)
        ),
        include_tournaments=bool(context_form.cleaned_data.get("include_tournaments") or False),
        include_hidden=bool(context_form.cleaned_data.get("include_hidden") or False),
        patch_boundaries=tuple(boundary.boundary_date for boundary in patch_boundaries),
    )
    selection = builder_form.selection()
    return ChartConfigDTO(
        metrics=tuple(selection.metric_keys),
        chart_type=selection.chart_type,
        group_by=selection.group_by,
        comparison=selection.comparison,
        smoothing=selection.smoothing,
        aggregation=selection.aggregation,
        context=context,
        scopes=builder_form.scopes(),
        x_axis=selection.x_axis,
    )
