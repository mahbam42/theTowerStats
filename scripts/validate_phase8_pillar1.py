#!/usr/bin/env python3
"""Validate the Phase 8 Pillar 1 checklist.

This is a developer-facing gate script for Phase 8 Pillar 2 work. It loads the
Phase 8 Pillar 1 YAML checklist and runs a set of programmatic checks.
"""

from __future__ import annotations

import argparse
import json
import os

import django

from core.phase8_pillar1_validation import validate_phase8_pillar1_checklist


def main() -> int:
    """Run the checklist validator and print a JSON report."""

    parser = argparse.ArgumentParser(description="Validate Phase 8 Pillar 1 checklist.")
    parser.add_argument("--checklist", default="archive/prompt29.yml", help="Path to the YAML checklist file.")
    args = parser.parse_args()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "theTowerStats.settings")
    django.setup()

    report = validate_phase8_pillar1_checklist(checklist_path=args.checklist)
    print(json.dumps(report, indent=2, sort_keys=True))

    if not report["final_status_pillar_1_complete"]:
        return 2
    if not report["all_complete"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
