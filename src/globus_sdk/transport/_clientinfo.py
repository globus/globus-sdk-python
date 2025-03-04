"""
This module models a read-write object representation of the
X-Globus-Client-Info header.

The spec for X-Globus-Client-Info is documented, in brief, in the GlobusClientInfo class
docstring.
"""

from __future__ import annotations

import typing as t

from globus_sdk import exc
from globus_sdk.version import __version__

_RESERVED_CHARS = ";,="


class GlobusClientInfo:
    """
    An implementation of X-Globus-Client-Info as an object. This header encodes a
    mapping of multiple products to versions and potentially other information.

    Values can be added to a clientinfo object via the ``add()`` method.

    The object always initializes itself to start with

        product=python-sdk,version=...

    using the current package version information.

    .. rubric:: ``X-Globus-Client-Info`` Specification

    Header Name: ``X-Globus-Client-Info``

    Header Value:

    - A semicolon (``;``) separated list of client information.

    - Client information is a comma-separated list of ``=`` delimited key-value pairs.
      Well-known values for client-information are:

      - ``product``: A unique identifier of the product.
      - ``version``: Relevant version information for the product.

    - Based on the above, the characters ``;,=`` should be considered reserved and
      should NOT be included in client information values to ensure proper parsing.

    .. rubric:: Example Headers

    .. code-block:: none

        X-Globus-Client-Info: product=python-sdk,version=3.32.1
        X-Globus-Client-Info: product=python-sdk,version=3.32.1;product=cli,version=4.0.0a1

    .. note::

        The ``GlobusClientInfo`` object is not guaranteed to reject all invalid usages.
        For example, ``product`` is required to be unique per header, and users are
        expected to enforce this in their usage.

    :param update_callback: A callback function to be invoked each time the content of
        the GlobusClientInfo changes via ``add()`` or ``clear()``.
    """  # noqa: E501

    def __init__(
        self, *, update_callback: t.Callable[[GlobusClientInfo], None] | None = None
    ) -> None:
        self.infos: list[str] = []

        # set `update_callback` to `None` at first so that `add()` can run without
        # triggering it during `__init__`
        self.update_callback = None
        self.add({"product": "python-sdk", "version": __version__})
        self.update_callback = update_callback

    def __bool__(self) -> bool:
        """Check if there are any values present."""
        return bool(self.infos)

    def format(self) -> str:
        """Format as a header value."""
        return ";".join(self.infos)

    def add(self, value: str | dict[str, str]) -> None:
        """
        Add an item to the clientinfo. The item is either already formatted
        as a string, or is a dict containing values to format.

        :param value: The element to add to the client-info. If it is a dict,
            it may not contain reserved characters in any keys or values. If it is a
            string, it cannot contain the ``;`` separator.
        """
        if not isinstance(value, str):
            value = ",".join(_format_items(value))
        elif ";" in value:
            raise exc.GlobusSDKUsageError(
                "GlobusClientInfo.add() cannot be used to add multiple items in "
                "an already-joined string. Add items separately instead. "
                f"Bad usage: '{value}'"
            )
        self.infos.append(value)

        if self.update_callback is not None:
            self.update_callback(self)

    def clear(self) -> None:
        """Empty the list of info strings and trigger the update callback."""
        self.infos = []
        if self.update_callback is not None:
            self.update_callback(self)


def _format_items(info: dict[str, str]) -> t.Iterable[str]:
    """Format the items in a dict, yielding the contents as an iterable."""
    for key, value in info.items():
        _check_reserved_chars(key, value)
        yield f"{key}={value}"


def _check_reserved_chars(key: str, value: str) -> None:
    """Check a key-value pair to see if it uses reserved chars."""
    if any(c in x for c in _RESERVED_CHARS for x in (key, value)):
        raise exc.GlobusSDKUsageError(
            "X-Globus-Client-Info reserved characters cannot be used in keys or "
            f"values. Bad usage: '{key}: {value}'"
        )
