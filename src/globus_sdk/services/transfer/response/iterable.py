from globus_sdk.response import GlobusHTTPResponse


class IterableTransferResponse(GlobusHTTPResponse):
    """
    Response class for non-paged list oriented resources. Allows top level
    fields to be accessed normally via standard item access, and also
    provides a convenient way to iterate over the sub-item list in the
    ``DATA`` key:

    >>> print("Path:", r["path"])
    >>> # Equivalent to: for item in r["DATA"]
    >>> for item in r:
    >>>     print(item["name"], item["type"])
    """

    def __iter__(self):
        return iter(self["DATA"])
