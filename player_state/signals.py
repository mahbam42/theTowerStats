"""Signals for Player lifecycle and authorization scaffolding."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.apps import apps
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from player_state.models import Player
from player_state.sync import sync_player_state_from_definitions

PLAYER_GROUP_NAME = "player"
ADMIN_GROUP_NAME = "admin"


@receiver(post_migrate)
def ensure_default_groups(sender, **kwargs) -> None:
    """Ensure the required default authorization groups exist.

    This runs on every `post_migrate` invocation so permissions can be attached
    as each app's models become available.
    """

    Group.objects.get_or_create(name=PLAYER_GROUP_NAME)
    Group.objects.get_or_create(name=ADMIN_GROUP_NAME)
    _ensure_default_group_permissions()


UserModel = get_user_model()


@receiver(post_save, sender=UserModel)
def ensure_player_for_user(sender, instance, created: bool, **kwargs) -> None:
    """Create or attach a Player record whenever a new User is created.

    The Player is derived from `instance` and never from user input.
    """

    if kwargs.get("raw", False):
        return

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


def _ensure_default_group_permissions() -> None:
    """Assign default model permissions to the built-in auth groups.

    Notes:
        The app uses per-player scoping in querysets and admin views; these
        permissions provide a coarse capability layer without introducing
        custom permission abstractions.
    """

    player_group, _ = Group.objects.get_or_create(name=PLAYER_GROUP_NAME)
    admin_group, _ = Group.objects.get_or_create(name=ADMIN_GROUP_NAME)

    player_perms = _collect_permissions(
        app_labels=("gamedata", "player_state"),
        actions=("add", "change", "view"),
    ) | _collect_permissions(
        app_labels=("definitions",),
        actions=("view",),
    )
    admin_perms = _collect_permissions(
        app_labels=("gamedata", "player_state", "definitions"),
        actions=("add", "change", "delete", "view"),
    )

    player_group.permissions.set(player_perms)
    admin_group.permissions.set(admin_perms)


def _collect_permissions(*, app_labels: tuple[str, ...], actions: tuple[str, ...]) -> set[Permission]:
    """Return a permission set for the given apps and actions.

    Args:
        app_labels: Django app labels to include.
        actions: Model permission action prefixes (e.g. "view", "change").

    Returns:
        Set of Permission rows that exist for the selected models/actions.
    """

    permissions: set[Permission] = set()
    for app_label in app_labels:
        try:
            config = apps.get_app_config(app_label)
        except LookupError:
            continue
        for model in config.get_models():
            opts = model._meta
            for action in actions:
                codename = f"{action}_{opts.model_name}"
                perm = Permission.objects.filter(content_type__app_label=app_label, codename=codename).first()
                if perm is not None:
                    permissions.add(perm)
    return permissions
