"""Phase 8 Pillar 1 hard precondition validation tests."""

from __future__ import annotations

import pytest

from core.phase8_pillar1_validation import validate_phase8_pillar1_checklist


@pytest.mark.django_db
def test_phase8_pillar1_checklist_validator_passes() -> None:
    """Phase 8 Pillar 2 work is gated on Pillar 1 passing."""

    report = validate_phase8_pillar1_checklist(checklist_path="archive/prompt29.yml")
    assert report["final_status_pillar_1_complete"] is True
    assert report["all_complete"] is True

