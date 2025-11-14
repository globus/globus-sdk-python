from __future__ import annotations

from globus_sdk.authorizers import GlobusAuthorizer

from .retry_config import RetryConfig


class RequestCallerInfo:
    """
    Data object that holds contextual information about the caller of a request.

    :param retry_config: The configuration of retry checks for the call
    :param resource_server: The resource server the request is being made to.
    :param authorizer: The authorizer object from the client making the request
    """

    def __init__(
        self,
        *,
        retry_config: RetryConfig,
        resource_server: str | None = None,
        authorizer: GlobusAuthorizer | None = None,
    ) -> None:
        self.resource_server = resource_server
        self.retry_config = retry_config
        self.authorizer = authorizer
