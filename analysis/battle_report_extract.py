"""Battle Report value extraction for canonical Phase 6 metrics.

This module extracts additional observed values from raw Battle Report text.
It intentionally stays within the analysis layer:
- pure (no Django imports),
- deterministic and testable,
- defensive on unknown labels (missing labels return None unless a caller
  chooses a default).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from .quantity import UnitType
from .units import UnitContract, UnitValidationError, parse_validated_quantity


_LABEL_SEPARATOR = r"(?:[ \t]*:[ \t]*|\t+[ \t]*|[ \t]{2,})"
_LABEL_VALUE_RE = re.compile(
    rf"(?im)^[ \t]*(?P<label>.+?){_LABEL_SEPARATOR}(?P<value>.*?)[ \t]*$"
)


def _normalize_label(label: str) -> str:
    """Normalize labels for dictionary lookup.

    Args:
        label: Raw label text.

    Returns:
        Normalized label key suitable for dictionary matching.
    """

    collapsed = re.sub(r"\s+", " ", (label or "").strip())
    return collapsed.casefold()


@lru_cache(maxsize=256)
def extract_label_values(raw_text: str) -> dict[str, str]:
    """Extract normalized label/value pairs from raw Battle Report text.

    Args:
        raw_text: Raw Battle Report text.

    Returns:
        Mapping of normalized label -> raw value string.
    """

    extracted: dict[str, str] = {}
    for match in _LABEL_VALUE_RE.finditer(raw_text or ""):
        label = (match.group("label") or "").strip()
        if not label:
            continue
        value = (match.group("value") or "").strip()
        key = _normalize_label(label)
        if key and key not in extracted:
            extracted[key] = value
    return extracted


@dataclass(frozen=True, slots=True)
class ExtractedNumber:
    """Extracted numeric value from a Battle Report line.

    Args:
        raw_value: Raw value string from the report.
        value: Parsed numeric value as a float (unit-normalized).
    """

    raw_value: str
    value: float


def extract_numeric_value(
    raw_text: str,
    *,
    label: str,
    unit_type: UnitType,
) -> ExtractedNumber | None:
    """Extract and parse a numeric value for a specific Battle Report label.

    Args:
        raw_text: Raw Battle Report text.
        label: Exact label as shown in Battle Reports.
        unit_type: Expected unit type for strict validation.

    Returns:
        ExtractedNumber when the label is present and parseable; otherwise None.

    Notes:
        The parsing rules come from `analysis.quantity.parse_quantity`. This
        wrapper additionally enforces that the raw string cannot represent a
        different unit type (e.g. `15%` for a coins metric).
    """

    values = extract_label_values(raw_text)
    raw_value = values.get(_normalize_label(label))
    if raw_value is None:
        return None

    try:
        validated = parse_validated_quantity(raw_value, contract=UnitContract(unit_type=unit_type))
    except (UnitValidationError, ValueError):
        return None

    return ExtractedNumber(raw_value=validated.raw_value, value=float(validated.normalized_value))

