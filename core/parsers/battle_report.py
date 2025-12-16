"""Best-effort Battle Report parsing utilities.

Phase 1 intentionally extracted only a small subset of run metadata needed for
the first chart. Phase 3 extends the extracted subset to support Battle History
table columns while keeping the same guiding rules:

- Unknown labels are non-fatal.
- Raw report text is always preserved unchanged when persisted.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone

from analysis.quantity import UnitType, parse_quantity


@dataclass(frozen=True)
class RawBattleReportFields:
    """Raw field values extracted from a Battle Report.

    This dataclass stores the untrusted, raw string values extracted from the
    report. Normalization/parsing into typed values happens separately.

    Attributes:
        battle_date: Raw battle date string if present.
        tier: Raw tier string if present.
        wave: Raw wave string if present.
        real_time: Raw real time string if present.
        killed_by: Raw "Killed By" string if present.
        coins_earned: Raw coins earned string if present.
        cash_earned: Raw cash earned string if present.
        interest_earned: Raw interest earned string if present.
        gem_blocks_tapped: Raw gem blocks tapped string if present.
        cells_earned: Raw cells earned string if present.
        reroll_shards_earned: Raw reroll shards earned string if present.
    """

    battle_date: str | None
    tier: str | None
    wave: str | None
    real_time: str | None
    killed_by: str | None
    coins_earned: str | None
    cash_earned: str | None
    interest_earned: str | None
    gem_blocks_tapped: str | None
    cells_earned: str | None
    reroll_shards_earned: str | None


@dataclass(frozen=True)
class ParsedBattleReport:
    """Parsed output for Battle Report ingestion.

    Attributes:
        checksum: SHA-256 checksum of the normalized raw text.
        battle_date: Parsed battle datetime (UTC) if present.
        tier: Parsed tier value if present.
        wave: Parsed wave value if present.
        real_time_seconds: Parsed real time duration in seconds if present.
        killed_by: Parsed killed-by label if present.
        coins_earned: Parsed coins earned as an integer if present.
        coins_earned_raw: Raw coins earned string if present.
        cash_earned: Parsed cash earned as an integer if present.
        cash_earned_raw: Raw cash earned string if present.
        interest_earned: Parsed interest earned as an integer if present.
        interest_earned_raw: Raw interest earned string if present.
        gem_blocks_tapped: Parsed gem blocks tapped as an integer if present.
        cells_earned: Parsed cells earned as an integer if present.
        reroll_shards_earned: Parsed reroll shards earned as an integer if present.
    """

    checksum: str
    battle_date: datetime | None
    tier: int | None
    wave: int | None
    real_time_seconds: int | None
    killed_by: str | None
    coins_earned: int | None
    coins_earned_raw: str | None
    cash_earned: int | None
    cash_earned_raw: str | None
    interest_earned: int | None
    interest_earned_raw: str | None
    gem_blocks_tapped: int | None
    cells_earned: int | None
    reroll_shards_earned: int | None


_LABEL_SEPARATOR = r"(?:[ \t]*:[ \t]*|\t+[ \t]*|[ \t]{2,})"
_LABEL_VALUE_RE = re.compile(
    rf"(?im)^[ \t]*(?P<label>.+?){_LABEL_SEPARATOR}(?P<value>.*?)[ \t]*$"
)

_LABELS = {
    "battle date": "battle_date",
    "tier": "tier",
    "wave": "wave",
    "real time": "real_time",
    "killed by": "killed_by",
    "coins": "coins_earned",
    "coins earned": "coins_earned",
    "cash earned": "cash_earned",
    "interest earned": "interest_earned",
    "gem blocks tapped": "gem_blocks_tapped",
    "cells earned": "cells_earned",
    "reroll shards earned": "reroll_shards_earned",
}


def compute_battle_report_checksum(raw_text: str) -> str:
    """Compute a deterministic checksum for a Battle Report.

    Args:
        raw_text: Raw Battle Report text as pasted by the user.

    Returns:
        A hex-encoded SHA-256 checksum.

    Notes:
        The checksum is computed on a normalized form of the raw text to make
        pastes robust to common newline differences. The stored raw text is not
        modified.
    """

    normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n").strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def parse_battle_report(raw_text: str) -> ParsedBattleReport:
    """Parse a Battle Report into typed metadata.

    Args:
        raw_text: Raw Battle Report text as pasted by the user.

    Returns:
        ParsedBattleReport containing a checksum and any extracted metadata.
    """

    checksum = compute_battle_report_checksum(raw_text)
    raw_fields = _extract_raw_fields(raw_text)
    battle_date = _parse_battle_date(raw_fields.battle_date)
    tier = _parse_int(raw_fields.tier)
    wave = _parse_int(raw_fields.wave)
    real_time_seconds = _parse_real_time_seconds(raw_fields.real_time)
    killed_by = _parse_text(raw_fields.killed_by)
    coins_earned_raw = _parse_text(raw_fields.coins_earned)
    coins_earned = _parse_compact_int(coins_earned_raw, unit_type=UnitType.coins)
    cash_earned_raw = _parse_text(raw_fields.cash_earned)
    cash_earned = _parse_compact_int(cash_earned_raw, unit_type=UnitType.count)
    interest_earned_raw = _parse_text(raw_fields.interest_earned)
    interest_earned = _parse_compact_int(interest_earned_raw, unit_type=UnitType.count)
    gem_blocks_tapped = _parse_int(raw_fields.gem_blocks_tapped)
    cells_earned = _parse_int(raw_fields.cells_earned)
    reroll_shards_earned = _parse_int(raw_fields.reroll_shards_earned)

    return ParsedBattleReport(
        checksum=checksum,
        battle_date=battle_date,
        tier=tier,
        wave=wave,
        real_time_seconds=real_time_seconds,
        killed_by=killed_by,
        coins_earned=coins_earned,
        coins_earned_raw=coins_earned_raw,
        cash_earned=cash_earned,
        cash_earned_raw=cash_earned_raw,
        interest_earned=interest_earned,
        interest_earned_raw=interest_earned_raw,
        gem_blocks_tapped=gem_blocks_tapped,
        cells_earned=cells_earned,
        reroll_shards_earned=reroll_shards_earned,
    )


def _extract_raw_fields(raw_text: str) -> RawBattleReportFields:
    """Extract raw values from Battle Report text.

    Args:
        raw_text: Raw Battle Report text as pasted by the user.

    Returns:
        RawBattleReportFields with best-effort extracted strings. Unknown labels,
        missing sections, and malformed lines are treated as non-fatal.
    """

    extracted: dict[str, str] = {}
    for label, value in _iter_label_value_lines(raw_text):
        normalized_label = _normalize_label(label)
        field_name = _LABELS.get(normalized_label)
        if field_name is None:
            continue
        if field_name not in extracted:
            extracted[field_name] = value

    return RawBattleReportFields(
        battle_date=extracted.get("battle_date"),
        tier=extracted.get("tier"),
        wave=extracted.get("wave"),
        real_time=extracted.get("real_time"),
        killed_by=extracted.get("killed_by"),
        coins_earned=extracted.get("coins_earned"),
        cash_earned=extracted.get("cash_earned"),
        interest_earned=extracted.get("interest_earned"),
        gem_blocks_tapped=extracted.get("gem_blocks_tapped"),
        cells_earned=extracted.get("cells_earned"),
        reroll_shards_earned=extracted.get("reroll_shards_earned"),
    )


def _iter_label_value_lines(raw_text: str) -> list[tuple[str, str]]:
    """Return a best-effort list of (label, value) pairs from report text.

    Notes:
        Battle Reports contain a mix of sections and labels. This function
        tolerates extra whitespace, reordered sections, and previously unseen
        labels by extracting only lines that look like `Label: Value` or
        `Label<TAB>Value`.
    """

    matches = _LABEL_VALUE_RE.finditer(raw_text)
    extracted: list[tuple[str, str]] = []
    for match in matches:
        label = (match.group("label") or "").strip()
        if not label:
            continue
        value = (match.group("value") or "").strip()
        extracted.append((label, value))
    return extracted


def _normalize_label(label: str) -> str:
    """Normalize a Battle Report label for dictionary lookup."""

    collapsed = re.sub(r"\s+", " ", label.strip())
    return collapsed.casefold()


def _parse_int(value: str | None) -> int | None:
    """Parse a base-10 integer if possible."""

    if value is None:
        return None
    cleaned = value.strip().replace(",", "")
    if not cleaned:
        return None
    try:
        return int(cleaned)
    except ValueError:
        return None


def _parse_text(value: str | None) -> str | None:
    """Return a trimmed string, or None when empty."""

    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    return cleaned


def _parse_compact_int(value: str | None, *, unit_type: UnitType) -> int | None:
    """Parse compact Battle Report numbers (e.g. `7.67M`, `$55.90M`) into an int."""

    if value is None:
        return None
    parsed = parse_quantity(value, unit_type=unit_type)
    if parsed.normalized_value is None or parsed.normalized_value <= 0:
        return None
    try:
        return int(parsed.normalized_value)
    except (OverflowError, ValueError):
        return None


def _parse_battle_date(value: str | None) -> datetime | None:
    """Parse a battle date string into a timezone-aware UTC datetime."""

    if value is None:
        return None

    value = value.strip()
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y",
        "%m/%d/%y",
        "%b %d, %Y %H:%M",
        "%B %d, %Y %H:%M",
    ]
    for fmt in formats:
        try:
            parsed = datetime.strptime(value, fmt)
        except ValueError:
            continue

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    iso = _try_parse_iso_datetime(value)
    if iso is not None:
        return iso

    return None


def _try_parse_iso_datetime(value: str) -> datetime | None:
    """Try parsing ISO-8601 datetime strings (best-effort)."""

    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _parse_real_time_seconds(value: str | None) -> int | None:
    """Parse a real-time duration string into seconds."""

    if value is None:
        return None

    cleaned = value.strip()
    if not cleaned:
        return None

    hms = _parse_hms_seconds(cleaned)
    if hms is not None:
        return hms

    units = _parse_unit_duration_seconds(cleaned)
    if units is not None:
        return units

    digits = cleaned.replace(",", "")
    if digits.isdigit():
        return int(digits)

    return None


def _parse_hms_seconds(value: str) -> int | None:
    """Parse `HH:MM:SS` or `MM:SS` formatted durations."""

    parts = value.split(":")
    if len(parts) not in {2, 3}:
        return None
    if not all(p.strip().isdigit() for p in parts):
        return None

    numbers = [int(p) for p in parts]
    if len(numbers) == 2:
        minutes, seconds = numbers
        return minutes * 60 + seconds

    hours, minutes, seconds = numbers
    return hours * 3600 + minutes * 60 + seconds


def _parse_unit_duration_seconds(value: str) -> int | None:
    """Parse durations like `1h 2m 3s` or `45m 10s`."""

    matches = re.findall(r"(?i)(\d+)\s*([hms])", value)
    if not matches:
        return None

    total = 0
    for number, unit in matches:
        amount = int(number)
        unit_lower = unit.lower()
        if unit_lower == "h":
            total += amount * 3600
        elif unit_lower == "m":
            total += amount * 60
        elif unit_lower == "s":
            total += amount

    return total if total > 0 else None
