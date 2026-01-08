"""Seed baseline Unit rows for wiki-derived and Battle Report values."""

from __future__ import annotations

from django.db import migrations


def seed_units(apps, schema_editor) -> None:
    """Insert or update baseline Unit rows used by the app."""

    Unit = apps.get_model("definitions", "Unit")
    units = [
        {"name": "coins", "symbol": "coins", "kind": "currency"},
        {"name": "cash", "symbol": "$", "kind": "currency"},
        {"name": "damage", "symbol": "dmg", "kind": "count"},
        {"name": "count", "symbol": "", "kind": "count"},
        {"name": "seconds", "symbol": "s", "kind": "seconds"},
        {"name": "percent", "symbol": "%", "kind": "percent"},
        {"name": "multiplier", "symbol": "x", "kind": "multiplier"},
    ]
    for unit in units:
        Unit.objects.update_or_create(name=unit["name"], defaults=unit)


class Migration(migrations.Migration):
    """Seed baseline Unit rows."""

    dependencies = [
        ("definitions", "0003_patchboundary"),
    ]

    operations = [
        migrations.RunPython(seed_units, reverse_code=migrations.RunPython.noop),
    ]
