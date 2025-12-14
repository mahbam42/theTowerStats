"""WSGI config for theTowerStats.

This exposes the WSGI callable as a module-level variable named `application`.
"""

from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "theTowerStats.settings")

application = get_wsgi_application()

