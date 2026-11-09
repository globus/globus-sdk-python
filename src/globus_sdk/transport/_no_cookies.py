from __future__ import annotations

import http.cookiejar
import typing as t

if t.TYPE_CHECKING:
    import urllib.request

# NOTE: this module imports `http.cookiejar` at import time, so it must only be
# imported lazily (e.g., when a `RequestsTransport` is constructed), in the same way
# that `requests` is.


class NoCookiesPolicy(http.cookiejar.CookiePolicy):
    """
    A cookie policy which rejects every cookie, both when a response sets one
    and when a request would send one.

    The SDK never intends to send cookies, but `requests` still stores any
    ``Set-Cookie`` in the session's cookie jar and merges that jar into redirect
    hops. Using this policy on the session's jar keeps a cookie set by one
    response from being sent on a later, unrelated request.
    """

    # These class variables are not defined by the `CookiePolicy` class contract.
    # However, a `CookiePolicy` subclass, `DefaultCookiePolicy`, defines them,
    # and the standard library's `CookieJar` accesses them as attributes.
    # They exist here to prevent attribute errors, though they have no effect.
    netscape = False
    rfc2965 = False
    hide_cookie2 = False

    def set_ok(
        self, cookie: http.cookiejar.Cookie, request: urllib.request.Request
    ) -> bool:
        return False

    def return_ok(
        self, cookie: http.cookiejar.Cookie, request: urllib.request.Request
    ) -> bool:
        return False

    def domain_return_ok(self, domain: str, request: urllib.request.Request) -> bool:
        return False

    def path_return_ok(self, path: str, request: urllib.request.Request) -> bool:
        return False
