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
    context = ChartContextDTO(
        start_date=context_form.cleaned_data.get("start_date"),
        end_date=context_form.cleaned_data.get("end_date"),
        tier=context_form.cleaned_data.get("tier"),
        preset_id=(preset.id if preset is not None else None),
        include_tournaments=bool(context_form.cleaned_data.get("include_tournaments") or False),
    )
    selection = builder_form.selection()
    return ChartConfigDTO(
        metrics=tuple(selection.metric_keys),
        chart_type=selection.chart_type,
        group_by=selection.group_by,
        comparison=selection.comparison,
        smoothing=selection.smoothing,
        context=context,
        scopes=builder_form.scopes(),
    )
