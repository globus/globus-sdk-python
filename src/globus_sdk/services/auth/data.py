from globus_sdk._internal.type_definitions import UUIDLike
from globus_sdk._payload import GlobusPayload


class DependentScopeSpec(GlobusPayload):
    """
    Utility class for creating dependent scope values as parameters to
    :meth:`AuthClient.create_scope <globus_sdk.AuthClient.create_scope>`
    and
    :meth:`AuthClient.update_scope <globus_sdk.AuthClient.update_scope>`.

    :param scope: The ID of the dependent scope
    :param optional: Whether or not the user can decline this specific scope without
        declining the whole consent.
    :param requires_refresh_token: Whether or not the dependency requires a refresh
        token.
    """

    def __init__(
        self,
        scope: UUIDLike,
        optional: bool,
        requires_refresh_token: bool,
    ) -> None:
        super().__init__()
        self["scope"] = str(scope)
        self["optional"] = optional
        self["requires_refresh_token"] = requires_refresh_token
