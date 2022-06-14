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
            policies=policies,
            additional_fields=additional_fields,
        )
        if additional_fields is not None:
            self.update(additional_fields)
