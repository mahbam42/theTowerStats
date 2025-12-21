"""Snapshot encoding/decoding helpers for ChartConfigDTO payloads."""

from __future__ import annotations

from datetime import date
from typing import Any, cast

from analysis.chart_config_dto import ChartConfigDTO, ChartContextDTO, ChartScopeDTO


def encode_chart_config_dto(config: ChartConfigDTO) -> dict[str, Any]:
    """Encode a ChartConfigDTO into a JSON-serializable dictionary.

    Args:
        config: ChartConfigDTO to encode.

    Returns:
        Dict payload safe for JSONField storage.
    """

    context = {
        "start_date": _encode_date(config.context.start_date),
        "end_date": _encode_date(config.context.end_date),
        "tier": config.context.tier,
        "preset_id": config.context.preset_id,
        "include_tournaments": bool(config.context.include_tournaments),
    }
    payload: dict[str, Any] = {
        "version": config.version,
        "metrics": list(config.metrics),
        "chart_type": config.chart_type,
        "group_by": config.group_by,
        "comparison": config.comparison,
        "smoothing": config.smoothing,
        "context": context,
    }
    if config.scopes is not None:
        payload["scopes"] = [
            {
                "label": scope.label,
                "run_id": scope.run_id,
                "start_date": _encode_date(scope.start_date),
                "end_date": _encode_date(scope.end_date),
            }
            for scope in config.scopes
        ]
    return payload


def decode_chart_config_dto(payload: dict[str, Any]) -> ChartConfigDTO:
    """Decode a ChartConfigDTO from a stored payload dictionary.

    Args:
        payload: JSONField payload previously produced by `encode_chart_config_dto`.

    Returns:
        ChartConfigDTO instance.

    Raises:
        ValueError: When required fields are missing or invalid.
    """

    metrics = tuple(str(x) for x in (payload.get("metrics") or ()))
    context_raw = cast(dict[str, Any], payload.get("context") or {})
    context = ChartContextDTO(
        start_date=_parse_date(context_raw.get("start_date")),
        end_date=_parse_date(context_raw.get("end_date")),
        tier=_parse_int(context_raw.get("tier")),
        preset_id=_parse_int(context_raw.get("preset_id")),
        include_tournaments=_parse_bool(context_raw.get("include_tournaments")),
    )
    scopes_raw = payload.get("scopes")
    scopes = None
    if isinstance(scopes_raw, list) and len(scopes_raw) == 2:
        a = cast(dict[str, Any], scopes_raw[0])
        b = cast(dict[str, Any], scopes_raw[1])
        scopes = (
            ChartScopeDTO(
                label=str(a.get("label") or "Scope A"),
                run_id=_parse_int(a.get("run_id")),
                start_date=_parse_date(a.get("start_date")),
                end_date=_parse_date(a.get("end_date")),
            ),
            ChartScopeDTO(
                label=str(b.get("label") or "Scope B"),
                run_id=_parse_int(b.get("run_id")),
                start_date=_parse_date(b.get("start_date")),
                end_date=_parse_date(b.get("end_date")),
            ),
        )
    return ChartConfigDTO(
        metrics=metrics,
        chart_type=str(payload.get("chart_type") or "line"),  # type: ignore[arg-type]
        group_by=str(payload.get("group_by") or "time"),  # type: ignore[arg-type]
        comparison=str(payload.get("comparison") or "none"),  # type: ignore[arg-type]
        smoothing=str(payload.get("smoothing") or "none"),  # type: ignore[arg-type]
        context=context,
        scopes=scopes,
        version=str(payload.get("version") or "phase7_chart_config_v1"),
    )


def _parse_date(value: object) -> date | None:
    """Best-effort date parsing for snapshot payloads."""

    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _encode_date(value: date | None) -> str | None:
    """Encode a date as an ISO string for JSON storage."""

    if value is None:
        return None
    return value.isoformat()


def _parse_int(value: object) -> int | None:
    """Best-effort int parsing for snapshot payloads."""

    if value is None or value == "":
        return None
    try:
        return int(str(value))
    except ValueError:
        return None


def _parse_bool(value: object) -> bool:
    """Best-effort bool parsing for snapshot payloads."""

    if isinstance(value, bool):
        return value
    if value is None:
        return False
    normalized = str(value).strip().casefold()
    return normalized in {"1", "true", "yes", "on"}
