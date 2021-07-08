import hashlib
from base64 import b64encode
from collections.abc import MutableMapping
from typing import Any, Dict


def sha256_string(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def safe_b64encode(s):
    try:
        encoded = b64encode(s.encode("utf-8"))
    except UnicodeDecodeError:
        encoded = b64encode(s)

    return encoded.decode("utf-8")


def slash_join(a, b):
    """
    Join a and b with a single slash, regardless of whether they already
    contain a trailing/leading slash or neither.
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


def safe_stringify(value):
    """
    Converts incoming value to a unicode string. Convert bytes by decoding,
    anything else has __str__ called.
    Strings are checked to avoid duplications
    """
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)


class PayloadWrapper(MutableMapping):
    """
    A class for defining helper objects which wrap some kind of "payload" dict.
    Typical for helper objects which formulate a request payload, e.g. as JSON.
    """

    def __init__(self):
        self._payload: Dict[str, Any] = {}

    def __getitem__(self, key: str):
        return self._payload[key]

    def __setitem__(self, key: str, value: Any):
        self._payload[key] = value

    def __delitem__(self, key: str):
        del self._payload[key]

    def __iter__(self):
        return iter(self._payload)

    def __len__(self):
        return len(self._payload)

    def to_dict(self) -> Dict[str, Any]:
        return self._payload
