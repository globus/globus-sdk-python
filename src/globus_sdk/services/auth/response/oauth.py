from __future__ import annotations

import datetime
import json
import logging
import textwrap
import time
import typing as t

import jwt
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from globus_sdk import exc
from globus_sdk.response import GlobusHTTPResponse

from .._common import SupportsJWKMethods

logger = logging.getLogger(__name__)


def _convert_token_info_dict(
    source_dict: GlobusHTTPResponse,
) -> dict[str, t.Any]:
    """
    Extract a set of fields into a new dict for indexing by resource server.
    Allow for these fields to be `None` when absent:
        - "refresh_token"
        - "token_type"
    """
    expires_in = source_dict.get("expires_in", 0)

    return {
        "scope": source_dict["scope"],
        "access_token": source_dict["access_token"],
        "refresh_token": source_dict.get("refresh_token"),
        "token_type": source_dict.get("token_type"),
        "expires_at_seconds": int(time.time() + expires_in),
        "resource_server": source_dict["resource_server"],
    }


class _ByScopesGetter:
    """
    A fancy dict-like object for looking up token data by scope name.
    Allows usage like

    >>> tokens = OAuthTokenResponse(...)
    >>> tok = tokens.by_scopes['openid profile']['access_token']
    """

    def __init__(self, scope_map: dict[str, t.Any]) -> None:
        self.scope_map = scope_map

    def __str__(self) -> str:
        return json.dumps(self.scope_map)

    def __iter__(self) -> t.Iterator[str]:
        """iteration gets you every individual scope"""
        return iter(self.scope_map.keys())

    def __getitem__(self, scopename: str) -> dict[str, str | int]:
        if not isinstance(scopename, str):
            raise KeyError(f'by_scopes cannot contain non-string value "{scopename}"')

        # split on spaces
        scopes = scopename.split()
        # collect every matching token in a set to dedup
        # but collect actual results (dicts) in a list
        rs_names = set()
        toks = []
        for scope in scopes:
            try:
                rs_names.add(self.scope_map[scope]["resource_server"])
                toks.append(self.scope_map[scope])
            except KeyError as err:
                raise KeyError(
                    (
                        'Scope specifier "{}" contains scope "{}" '
                        "which was not found"
                    ).format(scopename, scope)
                ) from err
        # if there isn't exactly 1 token, it's an error
        if len(rs_names) != 1:
            raise KeyError(
                'Scope specifier "{}" did not match exactly one token!'.format(
                    scopename
                )
            )
        # pop the only element in the set
        return t.cast(t.Dict[str, t.Union[str, int]], toks.pop())

    def __contains__(self, item: str) -> bool:
        """
        contains is driven by checking against getitem
        that way, the definitions are always "in sync" if we update them in
        the future
        """
        try:
            self.__getitem__(item)
            return True
        except KeyError:
            pass

        return False


class OAuthTokenResponse(GlobusHTTPResponse):
    """
    Class for responses from the OAuth2 code for tokens exchange used in
    3-legged OAuth flows.
    """

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self._init_rs_dict()
        self._init_scopes_getter()

    def _init_scopes_getter(self) -> None:
        scope_map = {}
        for _rs, tok_data in self._by_resource_server.items():
            for s in tok_data["scope"].split():
                scope_map[s] = tok_data
        self._by_scopes = _ByScopesGetter(scope_map)

    def _init_rs_dict(self) -> None:
        # call the helper at the top level
        self._by_resource_server = {
            self["resource_server"]: _convert_token_info_dict(self)
        }
        # call the helper on everything in 'other_tokens'
        self._by_resource_server.update(
            {
                unprocessed_item["resource_server"]: _convert_token_info_dict(
                    unprocessed_item
                )
                for unprocessed_item in self["other_tokens"]
            }
        )

    @property
    def by_resource_server(self) -> dict[str, dict[str, t.Any]]:
        """
        Representation of the token response in a ``dict`` indexed by resource
        server.

        Although ``OAuthTokenResponse.data`` is still available and
        valid, this representation is typically more desirable for applications
        doing inspection of access tokens and refresh tokens.
        """
        return self._by_resource_server

    @property
    def by_scopes(self) -> _ByScopesGetter:
        """
        Representation of the token response in a dict-like object indexed by
        scope name (or even space delimited scope names, so long as they match
        the same token).

        If you request scopes `scope1 scope2 scope3`, where `scope1` and
        `scope2` are for the same service (and therefore map to the same
        token), but `scope3` is for a different service, the following forms of
        access are valid:

        >>> tokens = ...
        >>> # single scope
        >>> token_data = tokens.by_scopes['scope1']
        >>> token_data = tokens.by_scopes['scope2']
        >>> token_data = tokens.by_scopes['scope3']
        >>> # matching scopes
        >>> token_data = tokens.by_scopes['scope1 scope2']
        >>> token_data = tokens.by_scopes['scope2 scope1']
        """
        return self._by_scopes

    def decode_id_token(
        self,
        openid_configuration: None | GlobusHTTPResponse | dict[str, t.Any] = None,
        jwk: RSAPublicKey | None = None,
        jwt_params: dict[str, t.Any] | None = None,
    ) -> dict[str, t.Any]:
        """
        Parse the included ID Token (OIDC) as a dict and return it.

        If you provide the `jwk`, you must also provide `openid_configuration`.

        :param openid_configuration: The OIDC config as a GlobusHTTPResponse or dict.
            When not provided, it will be fetched automatically.
        :param jwk: The JWK as a cryptography public key object. When not provided, it
            will be fetched and parsed automatically.
        :param jwt_params: An optional dict of parameters to pass to the jwt decode
            step. If ``"leeway"`` is included, it will be passed as the ``leeway``
            parameter, and all other values are passed as ``options``.
        """
        logger.info('Decoding ID Token "%s"', self["id_token"])
        if not isinstance(self.client, SupportsJWKMethods):
            raise exc.GlobusSDKUsageError(
                "decode_id_token() requires a client which supports JWK methods. "
                "This error suggests that an improper client type is attached to "
                "the token response."
            )
        else:
            auth_client: SupportsJWKMethods = self.client

        jwt_params = jwt_params or {}

        jwt_leeway: float | datetime.timedelta = 0.5
        if "leeway" in jwt_params:
            jwt_params = jwt_params.copy()
            jwt_leeway = jwt_params.pop("leeway")

        if not openid_configuration:
            if jwk:
                raise exc.GlobusSDKUsageError(
                    "passing jwk without openid configuration is not allowed"
                )
            logger.debug("No OIDC Config provided, autofetching...")
            oidc_config: GlobusHTTPResponse | dict[str, t.Any] = (
                auth_client.get_openid_configuration()
            )
        else:
            oidc_config = openid_configuration

        if not jwk:
            logger.debug("No JWK provided, autofetching + decoding...")
            jwk = auth_client.get_jwk(openid_configuration=oidc_config, as_pem=True)

        logger.debug("final step: decode with JWK")
        signing_algos = oidc_config["id_token_signing_alg_values_supported"]
        decoded = jwt.decode(
            self["id_token"],
            key=jwk,
            algorithms=signing_algos,
            audience=auth_client.client_id,
            options=jwt_params,
            leeway=jwt_leeway,
        )
        logger.debug("decode ID token finished successfully")
        return decoded

    def __str__(self) -> str:
        by_rs = json.dumps(self.by_resource_server, indent=2, separators=(",", ": "))
        id_token_to_print = t.cast(t.Optional[str], self.get("id_token"))
        if id_token_to_print is not None:
            id_token_to_print = id_token_to_print[:10] + "... (truncated)"
        return (
            f"{self.__class__.__name__}:\n"
            + f"  id_token: {id_token_to_print}\n"
            + "  by_resource_server:\n"
            + textwrap.indent(by_rs, "    ")
        )


class OAuthAuthorizationCodeResponse(OAuthTokenResponse):
    """
    Class for responses from the OAuth2 'authorization_code' grant.

    This class of response is returned by methods which get new tokens via a
    code-exchange, as in 3-legged OAuth or PKCE.

    For example,
    :meth:`globus_sdk.ConfidentialAppAuthClient.oauth2_exchange_code_for_tokens`
    will return an ``OAuthAuthorizationCodeResponse``.
    """


class OAuthClientCredentialsResponse(OAuthTokenResponse):
    """
    Class for responses from the OAuth2 'client_credentials' grant.

    This class of response is returned by methods which get new tokens by means of
    client credentials, namely
    :meth:`globus_sdk.ConfidentialAppAuthClient.oauth2_client_credentials_tokens`.
    """


class OAuthRefreshTokenResponse(OAuthTokenResponse):
    """
    Class for responses from the OAuth2 'refresh_token' grant.

    This class of response is returned by methods which get new tokens from an
    existing Refresh Token, e.g.,
    :meth:`globus_sdk.NativeAppAuthClient.oauth2_refresh_token`.
    """


class OAuthDependentTokenResponse(OAuthTokenResponse):
    """
    Class for responses from the OAuth2
    'urn:globus:auth:grant_type:dependent_token' grant.

    This is an extension grant type defined by Globus.

    :meth:`oauth2_get_dependent_tokens \
    <globus_sdk.ConfidentialAppAuthClient.oauth2_get_dependent_tokens>`
    provides this response, and includes some documentation on its proper usage.
    """

    def _init_rs_dict(self) -> None:
        # call the helper on everything in the response array
        self._by_resource_server = {
            unprocessed_item["resource_server"]: _convert_token_info_dict(
                unprocessed_item
            )
            for unprocessed_item in self.data
        }

    def decode_id_token(
        self,
        openid_configuration: None | (GlobusHTTPResponse | dict[str, t.Any]) = None,
        jwk: RSAPublicKey | None = None,
        jwt_params: dict[str, t.Any] | None = None,
    ) -> dict[str, t.Any]:
        # just in case
        raise NotImplementedError(
            "OAuthDependentTokenResponse.decode_id_token() is not and cannot "
            "be implemented. Dependent Tokens data does not include an "
            "id_token"
        )
