from __future__ import annotations

from globus_sdk.authorizers import GlobusAuthorizer

from .retry import RetryCheckCollection


class RequestCallerInfo:
    """
    Data object that holds contextual information about the caller of a request.

    :param retry_checks: The configured retry checks for the call
    :param authorizer: The authorizer object from the client making the request
    """

    def __init__(
        self,
        *,
        retry_checks: RetryCheckCollection,
        authorizer: GlobusAuthorizer | None = None,
    ) -> None:
        self.authorizer = authorizer
        self.retry_checks = retry_checks
