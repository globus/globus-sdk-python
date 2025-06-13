from __future__ import annotations

import typing as t

from globus_sdk._missing import MISSING, MissingType
from globus_sdk._payload import Payload
from globus_sdk._types import UUIDLike


class GCSRoleDocument(Payload):
    """
    Convenience class for constructing a Role document
    to use as the `data` parameter to `create_role`

    :param DATA_TYPE: Versioned document type.
    :param collection: Collection ID for the collection the role will apply to.
        This value is omitted when creating an endpoint
        role or when creating role definitions when creating collections.
    :param principal: Auth identity or group id URN. Should be in the format
        urn:globus:auth:[identity|group]:{uuid of identity or group}
    :param role: Role assigned to the principal. Known values are owner,
        administrator, access_manager, activity_manager, and activity_monitor
    """

    def __init__(
        self,
        DATA_TYPE: str = "role#1.0.0",
        collection: UUIDLike | MissingType = MISSING,
        principal: str | MissingType = MISSING,
        role: str | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self["DATA_TYPE"] = DATA_TYPE
        self["collection"] = collection
        self["principal"] = principal
        self["role"] = role
        self.update(additional_fields or {})
