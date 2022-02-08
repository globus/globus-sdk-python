import logging

from .authorizers import (
    AccessTokenAuthorizer,
    BasicAuthorizer,
    ClientCredentialsAuthorizer,
    NullAuthorizer,
    RefreshTokenAuthorizer,
)
from .client import BaseClient
from .exc import (
    GlobusAPIError,
    GlobusConnectionError,
    GlobusConnectionTimeoutError,
    GlobusError,
    GlobusSDKUsageError,
    GlobusTimeoutError,
    NetworkError,
)
from .local_endpoint import GlobusConnectPersonalOwnerInfo, LocalGlobusConnectPersonal
from .response import GlobusHTTPResponse
from .services.auth import (
    AuthAPIError,
    AuthClient,
    ConfidentialAppAuthClient,
    IdentityMap,
    NativeAppAuthClient,
    OAuthDependentTokenResponse,
    OAuthTokenResponse,
)
from .services.gcs import (
    CollectionDocument,
    GCSAPIError,
    GCSClient,
    GCSRoleDocument,
    GuestCollectionDocument,
    MappedCollectionDocument,
)
from .services.groups import (
    BatchMembershipActions,
    GroupMemberVisibility,
    GroupPolicies,
    GroupRequiredSignupFields,
    GroupRole,
    GroupsAPIError,
    GroupsClient,
    GroupsManager,
    GroupVisibility,
)
from .services.search import SearchAPIError, SearchClient, SearchQuery
from .services.transfer import (
    DeleteData,
    TransferAPIError,
    TransferClient,
    TransferData,
)
from .version import __version__

__all__ = (
    "__version__",
    "BaseClient",
    "GlobusHTTPResponse",
    "GlobusError",
    "GlobusSDKUsageError",
    "GlobusAPIError",
    "AuthAPIError",
    "TransferAPIError",
    "SearchAPIError",
    "GroupsAPIError",
    "NetworkError",
    "GlobusConnectionError",
    "GlobusTimeoutError",
    "GlobusConnectionTimeoutError",
    "NullAuthorizer",
    "BasicAuthorizer",
    "AccessTokenAuthorizer",
    "RefreshTokenAuthorizer",
    "ClientCredentialsAuthorizer",
    "AuthClient",
    "NativeAppAuthClient",
    "ConfidentialAppAuthClient",
    "OAuthDependentTokenResponse",
    "OAuthTokenResponse",
    "IdentityMap",
    "TransferClient",
    "TransferData",
    "DeleteData",
    "SearchClient",
    "SearchQuery",
    "GroupsClient",
    "BatchMembershipActions",
    "GroupPolicies",
    "GroupMemberVisibility",
    "GroupRequiredSignupFields",
    "GroupRole",
    "GroupVisibility",
    "GroupsManager",
    "GCSClient",
    "GCSRoleDocument",
    "CollectionDocument",
    "GuestCollectionDocument",
    "MappedCollectionDocument",
    "GCSAPIError",
    "GlobusConnectPersonalOwnerInfo",
    "LocalGlobusConnectPersonal",
)


# configure logging for a library, per python best practices:
# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
logging.getLogger("globus_sdk").addHandler(logging.NullHandler())
