from __future__ import annotations

import hashlib
import platform


def sha256_string(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def get_nice_hostname() -> str | None:
    """
    Get the current hostname, with the following added behavior:

    - if it ends in '.local', strip that suffix, as this is a frequent macOS behavior
      'DereksCoolMacbook.local' -> 'DereksCoolMacbook'

    - if the hostname is undiscoverable, return None
    """
    name = platform.node()
    if name.endswith(".local"):
        return name[: -len(".local")]
    return name or None


def slash_join(a: str, b: str | None) -> str:
    """
    Join a and b with a single slash, regardless of whether they already
    contain a trailing/leading slash or neither.

    :param a: the first path component
    :param b: the second path component
    """
    if not b:  # "" or None, don't append a slash
        return a
    if a.endswith("/"):
        if b.startswith("/"):
            return a[:-1] + b
        return a + b
    if b.startswith("/"):
        return a + b
    return a + "/" + b
