"""Demo mode helpers for safe, read-only exploration.

Demo mode allows an authenticated user to temporarily view a shared, seeded
dataset without affecting their own player-scoped data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import transaction
from django.http import HttpRequest

from definitions.models import BotDefinition, CardDefinition, GuardianChipDefinition, UltimateWeaponDefinition
from gamedata.models import BattleReport
from player_state.models import Player, PlayerBot, PlayerCard, PlayerGuardianChip, PlayerUltimateWeapon

from core.services import ingest_battle_report

DEMO_SESSION_KEY: Final[str] = "tts_demo_mode"
DEMO_USERNAME: Final[str] = "__demo__"
DEMO_DISPLAY_NAME: Final[str] = "Demo Player"


@dataclass(frozen=True, slots=True)
class DemoSeedResult:
    """Outcome for demo dataset seeding."""

    seeded: bool
    imported_reports: int


def demo_mode_enabled(request: HttpRequest) -> bool:
    """Return True when demo mode is enabled for the current session."""

    return bool(getattr(request, "session", {}).get(DEMO_SESSION_KEY, False))


def set_demo_mode(request: HttpRequest, *, enabled: bool) -> None:
    """Enable or disable demo mode in the current session.

    Args:
        request: Incoming request whose session will be updated.
        enabled: Desired demo mode state.
    """

    request.session[DEMO_SESSION_KEY] = bool(enabled)
    request.session.modified = True


def get_demo_player() -> Player:
    """Return the shared demo Player, creating and seeding it when missing.

    Returns:
        The demo Player instance.
    """

    UserModel = get_user_model()
    demo_user: AbstractUser
    demo_user, created = UserModel.objects.get_or_create(username=DEMO_USERNAME)
    if created:
        demo_user.set_unusable_password()
        demo_user.save(update_fields=["password"])

    demo_player, _ = Player.objects.get_or_create(
        user=demo_user,
        defaults={"display_name": DEMO_DISPLAY_NAME},
    )
    seed_demo_player(demo_player)
    return demo_player


def seed_demo_player(player: Player) -> DemoSeedResult:
    """Seed demo battle reports and dashboards if the demo dataset is empty.

    Seeding is intentionally minimal and idempotent. It does not overwrite
    existing demo data in-place.

    Args:
        player: Demo Player record to populate.

    Returns:
        DemoSeedResult describing whether seeding occurred.
    """

    if BattleReport.objects.filter(player=player).exists():
        return DemoSeedResult(seeded=False, imported_reports=0)

    demo_reports = _demo_battle_reports()
    with transaction.atomic():
        imported = 0
        for raw_text in demo_reports:
            _report, created = ingest_battle_report(raw_text, player=player, preset_name="Demo")
            imported += int(bool(created))

        _seed_demo_player_state(player)

    return DemoSeedResult(seeded=True, imported_reports=imported)


def _seed_demo_player_state(player: Player) -> None:
    """Seed basic player-state rows so read-only dashboards render in demo mode."""

    for definition in CardDefinition.objects.order_by("name"):
        PlayerCard.objects.get_or_create(
            player=player,
            card_slug=definition.slug,
            defaults={
                "card_definition": definition,
                "stars_unlocked": 1 if definition.rarity in ("Common", "Rare") else 0,
                "inventory_count": 0,
            },
        )

    for definition in UltimateWeaponDefinition.objects.order_by("name"):
        PlayerUltimateWeapon.objects.get_or_create(
            player=player,
            ultimate_weapon_slug=definition.slug,
            defaults={
                "ultimate_weapon_definition": definition,
                "unlocked": False,
            },
        )

    first_guardian = GuardianChipDefinition.objects.order_by("name").first()
    for definition in GuardianChipDefinition.objects.order_by("name"):
        PlayerGuardianChip.objects.get_or_create(
            player=player,
            guardian_chip_slug=definition.slug,
            defaults={
                "guardian_chip_definition": definition,
                "unlocked": bool(first_guardian and definition.slug == first_guardian.slug),
                "active": bool(first_guardian and definition.slug == first_guardian.slug),
            },
        )

    for definition in BotDefinition.objects.order_by("name"):
        PlayerBot.objects.get_or_create(
            player=player,
            bot_slug=definition.slug,
            defaults={
                "bot_definition": definition,
                "unlocked": False,
            },
        )


def _demo_battle_reports() -> tuple[str, ...]:
    """Return a small, deterministic set of demo Battle Report payloads."""

    base_lines = [
        "Game Time\t1h 10m 22s",
        "Real Time\t17m 35s",
        "Tier\t11",
        "Wave\t121",
        "Killed By\tBoss",
        "Coins earned\t1.24M",
        "Cash earned\t$1.00M",
        "Interest earned\t$220.24K",
        "Gem Blocks Tapped\t1",
        "Cells Earned\t0",
        "Reroll Shards Earned\t94",
        "",
    ]
    return (
        "\n".join(["Battle Report", "Battle Date\tDec 14, 2025 01:39", *base_lines]),
        "\n".join(["Battle Report", "Battle Date\tDec 15, 2025 01:41", *base_lines]),
        "\n".join(["Battle Report", "Battle Date\tDec 16, 2025 01:43", *base_lines]),
        "\n".join(
            [
                "Battle Report",
                "Battle Date\tDec 17, 2025 02:10",
                "Real Time\t22m 10s",
                "Tier\t10",
                "Wave\t150",
                "Killed By\tBoss",
                "Coins earned\t980.00K",
                "Cash earned\t$850.00K",
                "Interest earned\t$120.00K",
                "Gem Blocks Tapped\t2",
                "Cells Earned\t1",
                "Reroll Shards Earned\t110",
                "",
            ]
        ),
    )
