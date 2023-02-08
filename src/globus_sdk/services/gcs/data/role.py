from __future__ import annotations

import typing as t

from globus_sdk import utils
from globus_sdk._types import UUIDLike


class GCSRoleDocument(utils.PayloadWrapper):
    """
    Convenience class for constructing a Role document
    to use as the `data` parameter to `create_role`

    :param DATA_TYPE: Versioned document type.
    :type DATA_TYPE: str
    :param collection: Collection ID for the collection the role will apply to.
        This value is omitted when creating an endpoint
        role or when creating role definitions when creating collections.
    :type collection: str or UUID, optional
    :param principal: Auth identity or group id URN. Should be in the format
        urn:globus:auth:[identity|group]:{uuid of identity or group}
    :type principal: str, optional
    :param role: Role assigned to the principal. Known values are owner,
        administrator, access_manager, activity_manager, and activity_monitor
    :type role: str, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "role#1.0.0",
        collection: UUIDLike | None = None,
        principal: str | None = None,
        role: str | None = None,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(
            DATA_TYPE=DATA_TYPE,
            collection=collection,
            principal=principal,
            role=role,
        )
        if additional_fields is not None:
            self.update(additional_fields)
