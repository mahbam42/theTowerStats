"""Global search helpers for navigation and player-scoped entities."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode

from django.http import HttpRequest
from django.urls import reverse

from core.demo import demo_mode_enabled, get_demo_player
from player_state.models import ChartSnapshot, Player, Preset


@dataclass(frozen=True, slots=True)
class SearchItem:
    """A single search result row.

    Attributes:
        kind: Result category identifier (e.g. "nav", "preset", "snapshot", "docs").
        title: Primary display label.
        subtitle: Optional secondary label.
        url: Absolute or site-relative URL for navigation.
        score: Match score used for ordering (higher is better).
    """

    kind: str
    title: str
    subtitle: str | None
    url: str
    score: int

    def as_json(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""

        payload: dict[str, object] = {
            "kind": self.kind,
            "title": self.title,
            "url": self.url,
        }
        if self.subtitle:
            payload["subtitle"] = self.subtitle
        return payload


def request_player(*, request: HttpRequest) -> Player | None:
    """Return the request Player if authenticated, respecting demo mode.

    Args:
        request: Incoming request.

    Returns:
        The resolved Player when authenticated, otherwise None.
    """

    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return None
    if demo_mode_enabled(request):
        return get_demo_player()
    player, _ = Player.objects.get_or_create(
        user=request.user,
        defaults={"display_name": getattr(request.user, "username", "Player")},
    )
    return player


def _normalize(text: str) -> str:
    """Normalize a string for lightweight fuzzy matching."""

    return " ".join(text.strip().lower().split())


def fuzzy_score(*, query: str, candidate: str) -> int | None:
    """Return a lightweight fuzzy match score for ordering results.

    The scoring favors:
    - prefix matches,
    - substring matches close to the start,
    - in-order subsequence matches (characters appear in order).

    Args:
        query: Raw user query.
        candidate: Candidate label to score.

    Returns:
        Score integer when match exists, otherwise None.
    """

    q = _normalize(query)
    c = _normalize(candidate)
    if not q or not c:
        return None

    if q == c:
        return 10_000

    start = c.find(q)
    if start == 0:
        return 9_000 - (len(c) - len(q))
    if start > 0:
        return 7_000 - start - (len(c) - len(q))

    # Subsequence match (in-order characters).
    q_idx = 0
    gaps = 0
    last_match = -1
    for idx, ch in enumerate(c):
        if q_idx >= len(q):
            break
        if ch == q[q_idx]:
            if last_match >= 0:
                gaps += max(0, idx - last_match - 1)
            last_match = idx
            q_idx += 1
    if q_idx != len(q):
        return None

    return 4_000 - gaps - (len(c) - len(q))


def _nav_items() -> list[tuple[str, str, str | None, str]]:
    """Return static navigation targets: (title, url, subtitle, kind)."""

    return [
        ("Battle History", reverse("core:battle_history"), "Import and browse runs", "nav"),
        ("Charts", reverse("core:dashboard"), "Dashboard and filters", "nav"),
        ("Cards", reverse("core:cards"), "Progress dashboard", "nav"),
        ("Ultimate Weapons", reverse("core:ultimate_weapon_progress"), "Progress dashboard", "nav"),
        ("Guardian Chips", reverse("core:guardian_progress"), "Progress dashboard", "nav"),
        ("Bots", reverse("core:bots_progress"), "Progress dashboard", "nav"),
    ]


def _docs_search_item(*, query: str) -> SearchItem:
    """Return a docs search link item for the current query."""

    docs_base = "https://mahbam42.github.io/theTowerStats/"
    url = f"{docs_base}?{urlencode({'q': query})}"
    return SearchItem(
        kind="docs",
        title=f"Search docs for “{query}”",
        subtitle="Opens documentation site search",
        url=url,
        score=1_000,
    )


def build_search_items(*, request: HttpRequest, query: str, limit: int = 10) -> list[SearchItem]:
    """Build ordered search items for a query.

    Args:
        request: Incoming request.
        query: Raw user query.
        limit: Maximum number of items to return.

    Returns:
        Ordered list of search results.
    """

    q = query.strip()
    if not q:
        return []

    items: list[SearchItem] = []

    for title, url, subtitle, kind in _nav_items():
        score = fuzzy_score(query=q, candidate=title)
        if score is None:
            continue
        items.append(SearchItem(kind=kind, title=title, subtitle=subtitle, url=url, score=score))

    player = request_player(request=request)
    if player is not None:
        presets = list(Preset.objects.filter(player=player).only("id", "name").order_by("name")[:200])
        for preset in presets:
            score = fuzzy_score(query=q, candidate=preset.name)
            if score is None:
                continue
            url = f"{reverse('core:dashboard')}?{urlencode({'preset': preset.id})}"
            items.append(
                SearchItem(
                    kind="preset",
                    title=f"Preset: {preset.name}",
                    subtitle="Charts filter",
                    url=url,
                    score=score + 200,
                )
            )

        snapshots = list(
            ChartSnapshot.objects.filter(player=player).only("id", "name", "target").order_by("-created_at")[:200]
        )
        for snapshot in snapshots:
            score = fuzzy_score(query=q, candidate=snapshot.name)
            if score is None:
                continue
            if snapshot.target == "ultimate_weapons":
                url = f"{reverse('core:ultimate_weapon_progress')}?{urlencode({'uw_snapshot_id': snapshot.id})}"
                subtitle = "Ultimate Weapons snapshot"
            else:
                url = f"{reverse('core:dashboard')}?{urlencode({'snapshot_id': snapshot.id})}"
                subtitle = "Chart snapshot"
            items.append(
                SearchItem(
                    kind="snapshot",
                    title=f"Snapshot: {snapshot.name}",
                    subtitle=subtitle,
                    url=url,
                    score=score + 100,
                )
            )

    if len(q) >= 2:
        items.append(_docs_search_item(query=q))

    items.sort(key=lambda item: (-item.score, item.kind, item.title.lower()))
    return items[:limit]

