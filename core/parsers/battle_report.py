"""Minimal Battle Report parsing utilities.

Phase 1 intentionally extracts only a small subset of run metadata needed for
the first chart:

- Battle Date
- Tier
- Wave
- Real Time

All other labels are ignored (unknown labels are non-fatal). The raw text is
preserved unchanged when persisted.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class ParsedBattleReport:
    """Parsed output for Phase 1 Battle Report ingestion.

    Attributes:
        checksum: SHA-256 checksum of the normalized raw text.
        battle_date: Parsed battle datetime (UTC) if present.
        tier: Parsed tier value if present.
        wave: Parsed wave value if present.
        real_time_seconds: Parsed real time duration in seconds if present.
    """

    checksum: str
    battle_date: datetime | None
    tier: int | None
    wave: int | None
    real_time_seconds: int | None


_LABEL_SEPARATOR = r"(?:[ \t]*:[ \t]*|\t+[ \t]*|[ \t]{2,})"
_BATTLE_DATE_RE = re.compile(rf"(?im)^[ \t]*Battle Date{_LABEL_SEPARATOR}(.+?)[ \t]*$")
_TIER_RE = re.compile(rf"(?im)^[ \t]*Tier{_LABEL_SEPARATOR}(\d+)[ \t]*$")
_WAVE_RE = re.compile(rf"(?im)^[ \t]*Wave{_LABEL_SEPARATOR}(\d+)[ \t]*$")
_REAL_TIME_RE = re.compile(rf"(?im)^[ \t]*Real Time{_LABEL_SEPARATOR}(.+?)[ \t]*$")


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
    """Parse the Phase 1 subset of Battle Report metadata.

    Args:
        raw_text: Raw Battle Report text as pasted by the user.

    Returns:
        ParsedBattleReport containing a checksum and any extracted metadata.
    """

    checksum = compute_battle_report_checksum(raw_text)
    battle_date = _parse_battle_date(_first_match_group(_BATTLE_DATE_RE, raw_text))
    tier = _parse_int(_first_match_group(_TIER_RE, raw_text))
    wave = _parse_int(_first_match_group(_WAVE_RE, raw_text))
    real_time_seconds = _parse_real_time_seconds(
        _first_match_group(_REAL_TIME_RE, raw_text)
    )

    return ParsedBattleReport(
        checksum=checksum,
        battle_date=battle_date,
        tier=tier,
        wave=wave,
        real_time_seconds=real_time_seconds,
    )


def _first_match_group(pattern: re.Pattern[str], text: str) -> str | None:
    """Return the first capture group for a pattern, if present."""

    match = pattern.search(text)
    return match.group(1) if match else None


def _parse_int(value: str | None) -> int | None:
    """Parse a base-10 integer if possible."""

    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
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
