"""Shared metric category definitions.

MetricCategory is a semantic classification (not purely visual) used to ensure
new metrics are registered consistently and scoped predictably.
"""

from __future__ import annotations

from typing import Literal

MetricCategory = Literal["economy", "combat", "fetch", "utility"]

