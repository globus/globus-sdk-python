from __future__ import annotations

import time
import typing as t

from globus_sdk import AuthClient, OAuthTokenResponse, Scope
from globus_sdk.experimental.consents import ConsentForest
from globus_sdk.tokenstorage import StorageAdapter

from ..._types import UUIDLike
from ._identifiable_oauth_token_response import (
    IdentifiedOAuthTokenResponse,
    expand_id_token,
)
from .errors import (
    ExpiredTokenError,
    IdentityMismatchError,
    UnmetScopeRequirementsError,
)


class ValidatingStorageAdapter(StorageAdapter):
    """
    A special version of a StorageAdapter which wraps another storage adapter and
        validates that tokens meet certain requirements when storing/retrieving them.

    The adapter is not concerned with the actual storage location of tokens but rather
        validating that they meet certain requirements:
        1) Identity Requirements
            a) Identity info is present in the token data (this requires that the
                token data was retrieved with the "openid" scope in addition to any
                other scope requirements).
            b) The identity info in the token data matches the identity info stored
                previously in the adapter.
        2) Scope Requirements
            b) Each newly polled resource server's token meets the root scope
                requirements for that resource server.
            c) Polled consents meets all dependent scope requirements.
    """

    def __init__(
        self,
        storage_adapter: StorageAdapter,
        scope_requirements: dict[str, list[Scope]],
        *,
        consent_client: AuthClient | None = None,
    ):
        """
        :param storage_adapter: The storage adapter being wrapped.
        :param scope_requirements: A collection of resource-server keyed scope
            requirements to validate on token storage/retrieval.
        :param consent_client: An AuthClient to be used for consent polling. If omitted,
            dependent scope requirements are ignored during validation.
        """
        self._storage_adapter = storage_adapter
        self.scope_requirements = scope_requirements
        self._consent_client = consent_client

        self.identity_id = self._lookup_stored_identity_id()
        self._cached_consent_forest = self._poll_and_cache_consents()

    def _lookup_stored_identity_id(self) -> UUIDLike | None:
        """
        Attempts to extract an identity id from stored token data using the internal
            storage adapter.

        :returns: An identity id if one can be extracted from the internal storage
            adapter, otherwise None
        """
        auth_token_data = self._storage_adapter.get_token_data("auth.globus.org")
        if auth_token_data is None or "identity_id" not in auth_token_data:
            # Either:
            #  (1) No auth token data is present in the storage adapter or
            #  (2) No identity token is present in the auth token data.
            return None
        return t.cast(str, auth_token_data["identity_id"])

    def store(self, token_response: OAuthTokenResponse) -> None:
        """
        :param token_response: A OAuthTokenResponse resulting from a Globus Auth flow.
        :raises: :exc:`TokenValidationError` if the token has expired does not meet
            the attached scope requirements, or is associated with a different identity
            than was previously used with this adapter.
        """

        # Extract id_token info, raising an error if it's not present.
        identified_token_response = expand_id_token(token_response)

        self._validate_response(identified_token_response)
        self._storage_adapter.store(identified_token_response)

    def get_token_data(self, resource_server: str) -> dict[str, t.Any] | None:
        """
        :param resource_server: A resource server with cached token data.
        :returns: The token data for the given resource server, or None if no token data
            is present in the attached storage adapter.
        :raises: :exc:`TokenValidationError` if the token has expired or does not meet
            the attached scope requirements.
        """
        token_data = self._storage_adapter.get_token_data(resource_server)
        if token_data is None:
            return None

        self._validate_token_meets_scope_requirements(resource_server, token_data)

        return token_data

    def _validate_response(self, token_response: IdentifiedOAuthTokenResponse) -> None:
        self._validate_response_meets_identity_requirements(token_response)
        self._validate_response_meets_scope_requirements(token_response)

    def _validate_token(self, resource_server: str, token: dict[str, t.Any]) -> None:
        if token["expires_at_seconds"] < time.time():
            raise ExpiredTokenError(token["expires_at_seconds"])

        self._validate_token_meets_scope_requirements(resource_server, token)

    def _validate_response_meets_identity_requirements(
        self, token_response: IdentifiedOAuthTokenResponse
    ) -> None:
        """
        Validate that the identity info in the token data matches the stored identity
            info.

        Side Effect
        ===========
        If no identity info was previously stored, the attached identity is considered
            authoritative and stored on the adapter instance.

        :raises: :exc:`IdentityMismatchError` if the identity info in the token data
            does not match the stored identity info.
        """
        if self.identity_id is None:
            self.identity_id = token_response.identity_id
            return

        if token_response.identity_id != self.identity_id:
            raise IdentityMismatchError(
                "Detected a change in identity associated with the token data.",
                stored_id=self.identity_id,
                new_id=token_response.identity_id,
            )

    def _validate_response_meets_scope_requirements(
        self, token_response: IdentifiedOAuthTokenResponse
    ) -> None:
        for resource_server, token_data in token_response.by_resource_server.items():
            self._validate_token(resource_server, token_data)

    def _validate_token_meets_scope_requirements(
        self, resource_server: str, token: dict[str, t.Any]
    ) -> None:
        """
        Given a particular resource server/token, evaluate whether the token + user's
            consent forest meet the attached scope requirements.

        Note: If consent_client was omitted, only root scope requirements are validated.

        :raises: :exc:`UnmetScopeRequirements` if token/consent data does not meet the
            attached root or dependent scope requirements for the resource server.
        """
        required_scopes = self.scope_requirements.get(resource_server)

        # Short circuit - No scope requirements are, by definition, met.
        if required_scopes is None:
            return

        # 1. Does the token meet root scope requirements?
        root_scopes = token["scope"].split(" ")
        if not all(scope.scope_string in root_scopes for scope in required_scopes):
            raise UnmetScopeRequirementsError(
                "Unmet root scope requirements",
                scope_requirements=self.scope_requirements,
            )

        # Short circuit - No dependent scopes or ability to poll consents, don't
        #    validate them.
        if self._consent_client is None or not any(
            scope.dependencies for scope in required_scopes
        ):
            return

        # 2. Does the consent forest meet all dependent scope requirements?
        # 2a. Try with the cached consent forest first.
        forest = self._cached_consent_forest
        if forest is None or not forest.meets_scope_requirements(required_scopes):
            # 2b. Poll for fresh consents and try again.
            forest = self._poll_and_cache_consents()
            if forest is None:
                raise UnmetScopeRequirementsError(
                    "Failed to poll for consents",
                    scope_requirements=self.scope_requirements,
                )
            elif not forest.meets_scope_requirements(required_scopes):
                raise UnmetScopeRequirementsError(
                    "Unmet dependent scope requirements",
                    scope_requirements=self.scope_requirements,
                )

    def _poll_and_cache_consents(self) -> ConsentForest | None:
        """
        Poll for consents, caching and returning the result.

        :returns: The consent forest associated with the stored identity, or None if no
            stored identity info is present.
        """
        if self.identity_id is None or self._consent_client is None:
            return None

        forest = self._consent_client.get_consents(self.identity_id).to_forest()
        # Cache the consent forest first.
        self._cached_consent_forest = forest
        return forest
