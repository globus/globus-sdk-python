from __future__ import annotations

from globus_sdk._types import ScopeCollectionType
from globus_sdk.exc import GlobusSDKUsageError
from globus_sdk.exc.warnings import warn_deprecated
from globus_sdk.scopes import AuthScopes, MutableScope, TransferScopes

_DEFAULT_REQUESTED_SCOPES = (
    AuthScopes.openid,
    AuthScopes.profile,
    AuthScopes.email,
    TransferScopes.all,
)


def stringify_requested_scopes(requested_scopes: ScopeCollectionType | None) -> str:
    if requested_scopes is None:
        warn_deprecated(
            "`requested_scopes` was not specified or was given as `None`. "
            "A default set of scopes will be used, but this behavior is deprecated. "
            "Specify an explicit set of scopes instead.",
            stacklevel=3,
        )
        requested_scopes = _DEFAULT_REQUESTED_SCOPES

    requested_scopes_string: str = MutableScope.scopes2str(requested_scopes)
    if requested_scopes_string == "":
        raise GlobusSDKUsageError(
            "requested_scopes cannot be the empty string or empty collection"
        )
    return requested_scopes_string
