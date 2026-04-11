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


@dataclass(frozen=True, slots=True)
class MetricSelector:
    """Describe how a metric line should be matched inside a Battle Report.

    Args:
        label: Label text to match after normalization.
        section: Optional normalized section heading. Use ``None`` to require a
            top-level label outside any section.
        match_any_section: When True, match the label regardless of section.
    """

    label: str
    section: str | None = None
    match_any_section: bool = False


@dataclass(frozen=True, slots=True)
class ReportEntry:
    """Single parsed Battle Report label/value row."""

    section: str | None
    label: str
    value: str


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


def extract_numeric_value_from_selectors(
    raw_text: str,
    *,
    selectors: tuple[MetricSelector, ...],
    unit_type: UnitType,
) -> ExtractedNumber | None:
    """Extract and parse a numeric value from one of several label selectors.

    Args:
        raw_text: Raw Battle Report text.
        selectors: Ordered list of selector candidates.
        unit_type: Expected unit type for strict validation.

    Returns:
        ExtractedNumber when any selector matches and parses; otherwise None.
    """

    raw_value = extract_raw_value_from_selectors(raw_text, selectors=selectors)
    if raw_value is None:
        return None

    try:
        validated = parse_validated_quantity(raw_value, contract=UnitContract(unit_type=unit_type))
    except (UnitValidationError, ValueError):
        return None

    return ExtractedNumber(raw_value=validated.raw_value, value=float(validated.normalized_value))


def extract_raw_value_from_selectors(
    raw_text: str,
    *,
    selectors: tuple[MetricSelector, ...],
) -> str | None:
    """Return the raw value for the first matching selector.

    Args:
        raw_text: Raw Battle Report text.
        selectors: Ordered selector candidates.

    Returns:
        Raw string value when present; otherwise None.
    """

    flat_values = extract_label_values(raw_text)
    sectioned_values = extract_sectioned_label_values(raw_text)

    for selector in selectors:
        normalized_label = _normalize_label(selector.label)
        if selector.match_any_section:
            raw_value = flat_values.get(normalized_label)
            if raw_value is not None:
                return raw_value
            continue

        normalized_section = (
            None if selector.section is None else _normalize_label(selector.section)
        )
        raw_value = sectioned_values.get((normalized_section, normalized_label))
        if raw_value is not None:
            return raw_value
    return None


@lru_cache(maxsize=256)
def extract_sectioned_label_values(raw_text: str) -> dict[tuple[str | None, str], str]:
    """Extract normalized section+label/value pairs from raw Battle Report text.

    Args:
        raw_text: Raw Battle Report text.

    Returns:
        Mapping of ``(section, label)`` to raw value string. Top-level labels use
        ``None`` for the section.
    """

    extracted: dict[tuple[str | None, str], str] = {}
    for entry in _iter_report_entries(raw_text):
        section = None if entry.section is None else _normalize_label(entry.section)
        label = _normalize_label(entry.label)
        key = (section, label)
        if label and key not in extracted:
            extracted[key] = entry.value
    return extracted


def _iter_report_entries(raw_text: str) -> list[ReportEntry]:
    """Parse Battle Report text into section-aware label/value rows."""

    entries: list[ReportEntry] = []
    current_section: str | None = None

    for raw_line in (raw_text or "").splitlines():
        stripped = (raw_line or "").strip()
        if not stripped:
            continue

        match = _LABEL_VALUE_RE.match(raw_line)
        if match:
            label = (match.group("label") or "").strip()
            value = (match.group("value") or "").strip()
            if label:
                entries.append(ReportEntry(section=current_section, label=label, value=value))
            continue

        collapsed = re.sub(r"\s+", " ", stripped)
        if _normalize_label(collapsed) == "battle report":
            current_section = None
            continue
        current_section = collapsed
    return entries
