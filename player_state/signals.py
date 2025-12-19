"""Signals for Player lifecycle and authorization scaffolding."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from player_state.models import Player
from player_state.sync import sync_player_state_from_definitions

PLAYER_GROUP_NAME = "player"
ADMIN_GROUP_NAME = "admin"


@receiver(post_migrate)
def ensure_default_groups(sender, **kwargs) -> None:
    """Ensure the required default authorization groups exist."""

    if getattr(sender, "name", None) != "player_state":
        return
    Group.objects.get_or_create(name=PLAYER_GROUP_NAME)
    Group.objects.get_or_create(name=ADMIN_GROUP_NAME)


UserModel = get_user_model()


@receiver(post_save, sender=UserModel)
def ensure_player_for_user(sender, instance, created: bool, **kwargs) -> None:
    """Create or attach a Player record whenever a new User is created.

    The Player is derived from `instance` and never from user input.
    """

    if not created:
        return

    group, _ = Group.objects.get_or_create(name=PLAYER_GROUP_NAME)
    instance.groups.add(group)

    if Player.objects.filter(user=instance).exists():
        return

    orphan = Player.objects.filter(user__isnull=True).order_by("id").first()
    if orphan is not None:
        orphan.user = instance
        orphan.display_name = instance.username
        orphan.save(update_fields=["user", "display_name"])
        sync_player_state_from_definitions(player=orphan, write=True)
        return

    player = Player.objects.create(user=instance, display_name=instance.username)
    sync_player_state_from_definitions(player=player, write=True)

