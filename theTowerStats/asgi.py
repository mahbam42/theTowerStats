"""ASGI config for theTowerStats.

This exposes the ASGI callable as a module-level variable named `application`.
"""

from __future__ import annotations

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "theTowerStats.settings")

application = get_asgi_application()

