"""Pure analysis package for theTowerStats.

This package contains deterministic, testable computations that operate on
in-memory inputs and return DTOs. It must not import Django or perform any
database I/O.
"""

from .engine import analyze_runs

__all__ = ["analyze_runs"]

