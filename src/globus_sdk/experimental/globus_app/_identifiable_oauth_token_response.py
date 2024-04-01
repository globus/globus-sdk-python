import typing as t

from globus_sdk import OAuthTokenResponse

from ..._types import UUIDLike
from .errors import MissingIdentityError


class IdentifiedOAuthTokenResponse(OAuthTokenResponse):
    """
    A subclass of OAuthTokenResponse with attached identity information.
    """

    def __init__(self, identity_id: UUIDLike, *args: t.Any, **kwargs: t.Any):
        super().__init__(*args, **kwargs)
        self.identity_id = identity_id
        self.by_resource_server["auth.globus.org"]["identity_id"] = identity_id


def expand_id_token(response: OAuthTokenResponse) -> IdentifiedOAuthTokenResponse:
    """
    Given a token response, return an IdentifiedOAuthTokenResponse object which
        extracts the identity information from the token response into the auth
        token.

    Any token response passed to this function must have come from an auth flow which
        included the "openid" scope. This is because the id_token is only included in
        the token response when the "openid" scope is requested.

    :param response: The token response to extract identity information from
    :raises: MissingIdentityError if the token response does not contain an id_token
    """
    if (
        "auth.globus.org" not in response.by_resource_server
        or "id_token" not in response.data
    ):
        raise MissingIdentityError(
            "Token grant response doesn't contain an id_token. This normally occurs if "
            "the auth flow didn't include 'openid' alongside other scopes."
        )

    decoded_token = response.decode_id_token()
    identity_id = decoded_token["sub"]

    return IdentifiedOAuthTokenResponse(identity_id, response)
