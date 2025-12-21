"""Phase 10 regression tests for the Charts controls refactor."""

from __future__ import annotations

from django.urls import reverse


def test_phase10_charts_controls_render_as_layers(auth_client) -> None:
    """Ensure Charts renders the layered control surface (context, builder, advanced)."""

    response = auth_client.get(reverse("core:dashboard"))
    assert response.status_code == 200

    content = response.content.decode("utf-8")
    assert 'class="charts-layout"' in content
    assert 'id="chart-context-form"' in content
    assert 'id="open-chart-builder"' in content
    assert 'id="chart-builder-modal"' in content
    assert 'id="builder-step-2"' in content
    assert 'id="builder-step-3"' in content
    assert 'id="builder-step-4"' in content
