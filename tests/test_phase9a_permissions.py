"""Phase 9A regression tests for auth group permissions."""

from __future__ import annotations

import pytest
from django.contrib.auth.models import Group

from player_state.signals import _ensure_default_group_permissions


@pytest.mark.django_db
def test_default_groups_receive_expected_model_permissions() -> None:
    """Default groups receive baseline permissions for the app's models."""

    _ensure_default_group_permissions()

    player_group = Group.objects.get(name="player")
    admin_group = Group.objects.get(name="admin")

    assert player_group.permissions.filter(codename="view_battlereport").exists()
    assert player_group.permissions.filter(codename="change_playerultimateweapon").exists()
    assert player_group.permissions.filter(codename="view_ultimateweapondefinition").exists()
    assert not player_group.permissions.filter(codename="delete_battlereport").exists()

    assert admin_group.permissions.filter(codename="delete_battlereport").exists()
    assert admin_group.permissions.filter(codename="change_ultimateweapondefinition").exists()
