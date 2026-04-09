from __future__ import annotations

import logging
import typing as t
import uuid

from globus_sdk._missing import MISSING, MissingType
from globus_sdk._payload import GlobusPayload

log = logging.getLogger(__name__)


class BookmarkCreateDocument(GlobusPayload):
    """
    Convenience class for constructing a bookmark document to use as the
    ``data`` parameter to
    :meth:`~globus_sdk.TransferClientV2.create_bookmark`.
    """

    def __init__(
        self,
        collection: uuid.UUID | str,
        name: str,
        path: str,
        *,
        pinned: bool | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        log.debug("Creating a new BookmarkCreateDocument object")

        relationships = {
            "collection": {
                "data": {
                    "type": "Collection",
                    "id": collection,
                }
            }
        }

        attributes = {
            "name": name,
            "path": path,
            "pinned": pinned,
        }

        if additional_fields is not None:
            attributes.update(additional_fields)

        self["data"] = {
            "type": "Bookmark",
            "attributes": attributes,
            "relationships": relationships,
        }


class BookmarkUpdateDocument(GlobusPayload):
    """
    Convenience class for constructing a bookmark document to use as the
    ``data`` parameter to
    :meth:`~globus_sdk.TransferClientV2.update_bookmark>`.
    """

    def __init__(
        self,
        name: str,
        path: str,
        *,
        pinned: bool | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        log.debug("Creating a new BookmarkUpdateDocument")

        attributes = {
            "name": name,
            "path": path,
            "pinned": pinned,
        }

        if additional_fields is not None:
            attributes.update(additional_fields)

        self["data"] = {
            "type": "Bookmark",
            "attributes": attributes,
        }
