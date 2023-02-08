from __future__ import annotations

import base64
import shlex
import uuid


class _B32DecodeError(ValueError):
    """custom exception type"""


def _b32decode(v: str) -> str:
    # should start with "u_"
    if not v.startswith("u_"):
        raise _B32DecodeError("should start with 'u_'")
    v = v[2:]
    # wrong length
    if len(v) != 26:
        raise _B32DecodeError("wrong length")

    # append padding and uppercase so that b32decode will work
    v = v.upper() + (6 * "=")

    # try to decode
    try:
        return str(uuid.UUID(bytes=base64.b32decode(v)))
    # if it fails, then it can't be a b32-encoded identity
    except ValueError as err:
        raise _B32DecodeError("decode and load as UUID failed") from err


def _parse_dn_username(s: str) -> tuple[str, bool]:
    try:
        user, is_id = _b32decode(s), True
    except _B32DecodeError:
        user, is_id = f"{s}@globusid.org", False
    return (user, is_id)


class GlobusConnectPersonalOwnerInfo:
    """
    Information about the owner of the local Globus Connect Personal endpoint.

    Users should never create these objects directly, but instead rely upon
    :meth:`LocalGlobusConnectPersonal.get_owner_info()`.

    The info object contains ether ``id`` or ``username``.
    Parsing an info object from local data cannot guarantee that the ``id`` or
    ``username`` value will be found. Whichever one is present will be set and the
    other attribute will be ``None``.

    :ivar id: The Globus Auth ID of the endpoint owner
    :vartype id: str or None
    :ivar username: The Globus Auth Username of the endpoint owner
    :vartype username: str or None
    :param config_dn: A DN value from GCP configuration, which will be parsed into
        username or ID
    :type config_dn: str
    """

    _GRIDMAP_DN_START = '"/C=US/O=Globus Consortium/OU=Globus Connect User/CN='

    username: str | None
    id: str | None

    def __init__(self, *, config_dn: str) -> None:
        lineinfo = shlex.split(config_dn)
        if len(lineinfo) != 2:
            raise ValueError("Malformed DN: not right length")
        dn, _local_username = lineinfo
        username_or_id = dn.split("=", 4)[-1]

        user, is_id = _parse_dn_username(username_or_id)

        if is_id:
            self.username = None
            self.id = user
        else:
            self.username = user
            self.id = None

    def __str__(self) -> str:
        return (
            "GlobusConnectPersonalOwnerInfo("
            + (
                f"username={self.username}"
                if self.username is not None
                else f"id={self.id}"
            )
            + ")"
        )

    # private methods for SDK usage only
    @classmethod
    def _from_file(cls, filename: str) -> GlobusConnectPersonalOwnerInfo:
        with open(filename, encoding="utf-8") as fp:
            for line in fp:
                if line.startswith(cls._GRIDMAP_DN_START):
                    return cls(config_dn=line.strip())
        raise ValueError("Could not find GCP DN in data stream")
