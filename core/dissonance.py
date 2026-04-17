"""Helpers for Dissonance run classification and progression tracking."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
import math

from gamedata.models import DISSONANCE_TYPE_KEYS, PlayerDissonanceTierBoost
from player_state.models import Player


DEFAULT_DISSONANCE_LEVEL = 1


def default_dissonance_levels() -> dict[str, int]:
    """Return the default per-type Dissonance level mapping.

    Returns:
        Dict keyed by Dissonance type with the baseline level for types that
        have not yet been unlocked by the player.
    """

    return {key: DEFAULT_DISSONANCE_LEVEL for key in DISSONANCE_TYPE_KEYS}


def level_snapshot_for_tier(*, player: Player, tier: int | None) -> dict[str, int]:
    """Return the stored Dissonance levels for a player's tier.

    Args:
        player: Owning player.
        tier: Tier to inspect.

    Returns:
        Dict keyed by Dissonance type. Missing tiers return the default level
        mapping with level `1` for every type.
    """

    levels = default_dissonance_levels()
    if tier is None:
        return levels
    boosts = PlayerDissonanceTierBoost.objects.filter(player=player, tier=tier)
    for boost in boosts:
        levels[str(boost.dissonance_type)] = int(boost.current_level)
    return levels


def effective_multiplier(*, multiplier_level: int | float | Decimal | None, wave: int | None) -> Decimal:
    """Calculate the effective Dissonance multiplier for a wave.

    Args:
        multiplier_level: Current unlocked Dissonance level for the type.
        wave: Wave reached on the run.

    Returns:
        Decimal multiplier rounded to four decimal places.
    """

    level = Decimal(str(multiplier_level or DEFAULT_DISSONANCE_LEVEL))
    wave_value = Decimal(str(max(int(wave or 0), 0)))
    if level <= 1 or wave_value <= 0:
        return Decimal("1.0000")
    ratio = float(wave_value / Decimal("5000"))
    computed = Decimal("1") + (level - Decimal("1")) * Decimal(str(math.pow(ratio, 1.75)))
    return computed.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def record_dissonance_unlock(
    *,
    player: Player,
    tier: int | None,
    dissonance_type: str | None,
    wave: int | None,
) -> PlayerDissonanceTierBoost | None:
    """Advance and persist Dissonance progression for a completed run.

    Args:
        player: Owning player.
        tier: Tier the Dissonance run was completed on.
        dissonance_type: Dissonance type selected for the run.
        wave: Wave reached by the run.

    Returns:
        Updated PlayerDissonanceTierBoost row, or None when the input does not
        describe a trackable Dissonance run.
    """

    if tier is None or not dissonance_type:
        return None
    boost, created = PlayerDissonanceTierBoost.objects.get_or_create(
        player=player,
        tier=tier,
        dissonance_type=dissonance_type,
        defaults={
            "current_level": DEFAULT_DISSONANCE_LEVEL,
            "highest_effective_multiplier": Decimal("1.0000"),
            "top_effective_multipliers": [],
        },
    )
    if created:
        boost.current_level = DEFAULT_DISSONANCE_LEVEL + 1
    else:
        boost.current_level = max(int(boost.current_level), DEFAULT_DISSONANCE_LEVEL) + 1
    multiplier = effective_multiplier(multiplier_level=boost.current_level, wave=wave)
    history = [
        float(value)
        for value in boost.top_effective_multipliers
        if isinstance(value, (int, float))
    ]
    history.append(float(multiplier))
    history = sorted(history, reverse=True)[:3]
    boost.top_effective_multipliers = history
    if multiplier > boost.highest_effective_multiplier:
        boost.highest_effective_multiplier = multiplier
    boost.save()
    return boost


def tier_bonus_rows(*, player: Player) -> list[dict[str, object]]:
    """Return tier/grouped Dissonance bonus rows for Battle History UI.

    Args:
        player: Owning player.

    Returns:
        List of dictionaries sorted by tier and Dissonance type for modal/table
        rendering.
    """

    boosts = PlayerDissonanceTierBoost.objects.filter(player=player).order_by("tier", "dissonance_type")
    rows: list[dict[str, object]] = []
    for boost in boosts:
        type_label = dict(boost._meta.get_field("dissonance_type").choices).get(
            str(boost.dissonance_type),
            str(boost.dissonance_type),
        )
        rows.append(
            {
                "tier": int(boost.tier),
                "dissonance_type": str(boost.dissonance_type),
                "dissonance_type_label": type_label,
                "current_level": int(boost.current_level),
                "highest_effective_multiplier": float(boost.highest_effective_multiplier),
                "top_effective_multipliers": tuple(boost.top_effective_multipliers),
            }
        )
    return rows
