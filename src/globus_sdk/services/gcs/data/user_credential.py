from typing import Any, Dict, Optional

from globus_sdk import utils
from globus_sdk._types import UUIDLike


class UserCredentialDocument(utils.PayloadWrapper):
    """
    Convenience class for constructing a UserCredential document
    to use as the `data` parameter to `create_user_credential` and
    `update_user_credential`

    :param DATA_TYPE: Versioned document type.
    :type DATA_TYPE: str
    :param identity_id: UUID of the Globus identity this credential will
        provide access for
    :type identity_id: UUID or str, optional
    :param connector_id: UUID of the connector this credential is for
    :type connector_id: UUID or str, optional
    :param username: Username of the local account this credential will provide
        access to, format is connector specific
    :type username: str, optional
    :param display_name: Display name for this credential
    :type display_name: str, optional
    :param storage_gateway_id: UUID of the storage gateway this credential is for
    :type storage_gateway_id: UUID or str, optional
    :param policies: Connector specific policies for this credential
    :type policies: dict, optional
    :param additional_fields: Additional data for inclusion in the document
    :type additional_fields: dict, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "user_credential#1.0.0",
        identity_id: Optional[UUIDLike] = None,
        connector_id: Optional[UUIDLike] = None,
        username: Optional[str] = None,
        display_name: Optional[str] = None,
        storage_gateway_id: Optional[UUIDLike] = None,
        policies: Optional[Dict[str, Any]] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(
            DATA_TYPE=DATA_TYPE,
            identity_id=identity_id,
            connector_id=connector_id,
            username=username,
            display_name=display_name,
            storage_gateway_id=storage_gateway_id,
        )
        self._set_value("policies", policies, callback=dict)

        if additional_fields is not None:
            self.update(additional_fields)
