"""Economy helpers for optional gem enforcement.

The project does not currently require gem tracking. These helpers support
future enforcement while keeping current features unblocked when a gem balance
is not stored yet.
"""

from __future__ import annotations

import re
from typing import Final

from django.core.exceptions import FieldDoesNotExist
from django.db import models

_GEM_FIELD_CANDIDATES: Final[tuple[str, ...]] = ("gems", "gem_balance")


def parse_cost_amount(*, cost_raw: str | None) -> int | None:
    """Parse a numeric amount from a raw cost string.

    Args:
        cost_raw: Raw cost string from wiki data (e.g. "50 Gems" or "1,250").

    Returns:
        Parsed integer amount when a number is present, otherwise None.
    """

    if not cost_raw:
        return None
    match = re.search(r"([0-9][0-9,]*)", cost_raw)
    if not match:
        return None
    try:
        return int(match.group(1).replace(",", ""))
    except ValueError:
        return None


def gem_balance_field_name(*, player: models.Model) -> str | None:
    """Return the Player model field name used for gem balance, when present.

    Args:
        player: A Django model instance representing the player.

    Returns:
        The name of a gem balance field when the model includes one (currently
        tries "gems" then "gem_balance"), otherwise None.
    """

    for candidate in _GEM_FIELD_CANDIDATES:
        try:
            player._meta.get_field(candidate)
        except FieldDoesNotExist:
            continue
        return candidate
    return None


def enforce_and_deduct_gems_if_tracked(
    *, player: models.Model, cost_raw: str | None
) -> tuple[bool | None, int | None]:
    """Optionally enforce and deduct gems for a purchase.

    This is a "soft dependency": if the Player model does not track gems yet,
    the function returns (None, parsed_cost) and the caller should proceed
    without blocking.

    Args:
        player: Player instance that may or may not include a gem balance field.
        cost_raw: Raw cost string. Only enforced when it parses to an integer.

    Returns:
        Tuple of (result, parsed_cost):
        - result is True when gems were deducted successfully
        - result is False when gem tracking exists but balance is insufficient
        - result is None when gem tracking is unavailable or the cost is unparseable
        parsed_cost is the parsed integer cost when available.
    """

    field_name = gem_balance_field_name(player=player)
    parsed_cost = parse_cost_amount(cost_raw=cost_raw)
    if field_name is None:
        return None, parsed_cost
    if parsed_cost is None:
        return None, None

    current_balance = getattr(player, field_name, None)
    if not isinstance(current_balance, int):
        return None, parsed_cost

    if current_balance < parsed_cost:
        return False, parsed_cost

    setattr(player, field_name, current_balance - parsed_cost)
    player.save(update_fields=[field_name])
    return True, parsed_cost
