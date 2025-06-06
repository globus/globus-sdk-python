from __future__ import annotations

import json
import logging
import typing as t

import jwt
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from globus_sdk._missing import MISSING, MissingType
from globus_sdk._types import ScopeCollectionType
from globus_sdk.exc import GlobusSDKUsageError
from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.scopes import scopes_to_str

log = logging.getLogger(__name__)


def stringify_requested_scopes(requested_scopes: ScopeCollectionType) -> str:
    requested_scopes_string: str = scopes_to_str(requested_scopes)
    if requested_scopes_string == "":
        raise GlobusSDKUsageError(
            "requested_scopes cannot be the empty string or empty collection"
        )
    return requested_scopes_string


class _JWKGetCallbackProto(t.Protocol):
    def __call__(
        self,
        path: str,
        *,
        query_params: dict[str, t.Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> GlobusHTTPResponse: ...


def get_jwk_data(
    *,
    fget: _JWKGetCallbackProto,
    openid_configuration: GlobusHTTPResponse | dict[str, t.Any],
) -> dict[str, t.Any]:
    jwks_uri = openid_configuration["jwks_uri"]
    log.debug("fetching from jwks_uri=%s", jwks_uri)
    data = fget(jwks_uri).data
    if not isinstance(data, dict):
        # how could this happen?
        # some guesses:
        # - interfering proxy or cache
        # - user passed explicit (incorrect) OIDC config
        raise ValueError(
            "JWK data was not a dict. This should be an unreachable condition."
        )
    return data


def pem_decode_jwk_data(
    *,
    jwk_data: dict[str, t.Any],
) -> RSAPublicKey:
    log.debug("JWK PEM decode requested, decoding...")
    # decode from JWK to an RSA PEM key for JWT decoding
    # cast here because this should never be private key
    jwk_as_pem: RSAPublicKey = t.cast(
        RSAPublicKey,
        jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk_data["keys"][0])),
    )
    log.debug("JWK PEM decoding finished successfully")
    return jwk_as_pem


@t.runtime_checkable
class SupportsJWKMethods(t.Protocol):
    client_id: str | None

    def get_openid_configuration(self) -> GlobusHTTPResponse: ...

    @t.overload
    def get_jwk(
        self,
        openid_configuration: GlobusHTTPResponse | dict[str, t.Any] | MissingType,
        *,
        as_pem: t.Literal[True],
    ) -> RSAPublicKey: ...

    @t.overload
    def get_jwk(
        self,
        openid_configuration: GlobusHTTPResponse | dict[str, t.Any] | MissingType,
        *,
        as_pem: t.Literal[False],
    ) -> dict[str, t.Any]: ...

    def get_jwk(
        self,
        openid_configuration: (
            GlobusHTTPResponse | dict[str, t.Any] | MissingType
        ) = MISSING,
        *,
        as_pem: bool = False,
    ) -> RSAPublicKey | dict[str, t.Any]: ...
