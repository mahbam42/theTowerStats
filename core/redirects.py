"""Safe redirect helpers.

Direct redirects based on user-supplied values are security-sensitive. This
module centralizes redirect target validation using Django's
`url_has_allowed_host_and_scheme`.
"""

from __future__ import annotations

from collections.abc import Iterable

from django.conf import settings
from django.core.exceptions import DisallowedHost
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme


def safe_redirect(
    request: HttpRequest,
    *,
    candidates: Iterable[str | None],
    fallback: str,
) -> HttpResponseRedirect:
    """Redirect to the first safe URL from a candidate list.

    Args:
        request: Incoming request used for host + scheme validation.
        candidates: Candidate redirect URLs (typically derived from `next` or a
            referer header). The first safe value is used.
        fallback: Safe default URL to use when no candidates are safe.

    Returns:
        An HttpResponseRedirect to a safe URL.
    """

    allowed_hosts = set(settings.ALLOWED_HOSTS)
    try:
        allowed_hosts.add(request.get_host())
    except DisallowedHost:
        pass

    require_https = request.is_secure()
    for candidate in candidates:
        value = (candidate or "").strip()
        if not value:
            continue
        if url_has_allowed_host_and_scheme(
            url=value,
            allowed_hosts=allowed_hosts,
            require_https=require_https,
        ):
            return redirect(value)
    return redirect(fallback)

