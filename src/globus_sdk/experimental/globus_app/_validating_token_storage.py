from __future__ import annotations

import time

from globus_sdk import AuthClient, Scope
from globus_sdk.experimental.consents import ConsentForest
from globus_sdk.experimental.tokenstorage import TokenData, TokenStorage

from ..._types import UUIDLike
from .errors import (
    ExpiredTokenError,
    IdentityMismatchError,
    MissingIdentityError,
    UnmetScopeRequirementsError,
)


def _get_identity_id_from_token_data_by_resource_server(
    token_data_by_resource_server: dict[str, TokenData]
) -> str | None:
    """
    Get the identity_id attribute from all TokenData objects by resource server
    Sanity check that they are all the same, and then return that identity_id or None
    """
    token_data_identity_ids: set[str] = set()

    for token_data in token_data_by_resource_server.values():
        if token_data.identity_id:
            token_data_identity_ids.add(token_data.identity_id)

    if len(token_data_identity_ids) == 0:
        return None
    elif len(token_data_identity_ids) == 1:
        return token_data_identity_ids.pop()
    else:
        raise ValueError(
            "token_data_by_resource_server contained TokenData objects with "
            f"different identity_id values: {token_data_identity_ids}"
        )


class ValidatingTokenStorage(TokenStorage):
    """
    A special version of TokenStorage which wraps another TokenStorage and
        validates that tokens meet certain requirements when storing/retrieving them.

    ValidatingTokenStorage is not concerned with the actual storage location of tokens
        but rather validating that they meet certain requirements:
        1) Identity Requirements
            a) Identity info is present in the token data (this requires that the
                token data was retrieved with the "openid" scope in addition to any
                other scope requirements).
            b) The identity info in the token data matches the identity info stored
                previously.
        2) Scope Requirements
            a) Each newly polled resource server's token meets the root scope
                requirements for that resource server.
            b) Polled consents meets all dependent scope requirements.
    """

    def __init__(
        self,
        token_storage: TokenStorage,
        scope_requirements: dict[str, list[Scope]],
        *,
        consent_client: AuthClient | None = None,
    ):
        """
        :param token_storage: The token storage being wrapped.
        :param scope_requirements: A collection of resource-server keyed scope
            requirements to validate on token storage/retrieval.
        :param consent_client: An AuthClient to be used for consent polling. If omitted,
            dependent scope requirements are ignored during validation.
        """
        self._token_storage = token_storage
        self.scope_requirements = scope_requirements
        self._consent_client = consent_client

        self.identity_id = self._lookup_stored_identity_id()
        self._cached_consent_forest = self._poll_and_cache_consents()

        super().__init__(namespace=token_storage.namespace)

    def _lookup_stored_identity_id(self) -> UUIDLike | None:
        """
        Attempts to extract an identity id from stored token data using the internal
            token storage.

        :returns: An identity id if one can be extracted from the internal token
            storage, otherwise None
        """
        token_data_by_resource_server = (
            self._token_storage.get_token_data_by_resource_server()
        )
        return _get_identity_id_from_token_data_by_resource_server(
            token_data_by_resource_server
        )

    def store_token_data_by_resource_server(
        self, token_data_by_resource_server: dict[str, TokenData]
    ) -> None:

        self._validate_token_data_by_resource_server(token_data_by_resource_server)
        self._token_storage.store_token_data_by_resource_server(
            token_data_by_resource_server
        )

    def get_token_data_by_resource_server(self) -> dict[str, TokenData]:
        """
        :returns: A dict of TokenData objects indexed by their resource server
        :raises: :exc:`TokenValidationError` if any of the token data have expired or
            do not meet the attached scope requirements.
        """
        token_data_by_resource_server = (
            self._token_storage.get_token_data_by_resource_server()
        )

        for resource_server, token_data in token_data_by_resource_server.items():
            self._validate_token_meets_scope_requirements(resource_server, token_data)

        return token_data_by_resource_server

    def get_token_data(self, resource_server: str) -> TokenData | None:
        """
        :param resource_server: A resource server with cached token data.
        :returns: The token data for the given resource server, or None if no token data
            is present in the attached storage adapter.
        :raises: :exc:`TokenValidationError` if the token has expired or does not meet
            the attached scope requirements.
        """
        token_data = self._token_storage.get_token_data(resource_server)
        if token_data is None:
            return None

        self._validate_token_meets_scope_requirements(resource_server, token_data)

        return token_data

    def remove_token_data(self, resource_server: str) -> bool:
        """
        :param resource_server: The resource server string to remove token data for
        """
        return self._token_storage.remove_token_data(resource_server)

    def _validate_token_data_by_resource_server(
        self, token_data_by_resource_server: dict[str, TokenData]
    ) -> None:
        self._validate_token_data_by_resource_server_meets_identity_requirements(
            token_data_by_resource_server
        )
        self._validate_token_data_by_resource_server_meets_scope_requirements(
            token_data_by_resource_server
        )

    def _validate_token_data(self, resource_server: str, token_data: TokenData) -> None:
        if token_data.expires_at_seconds < time.time():
            raise ExpiredTokenError(token_data.expires_at_seconds)

        self._validate_token_meets_scope_requirements(resource_server, token_data)

    def _validate_token_data_by_resource_server_meets_identity_requirements(
        self, token_data_by_resource_server: dict[str, TokenData]
    ) -> None:
        """
        Validate that the identity info in the token data matches the stored identity
            info.

        Side Effect
        ===========
        If no identity info was previously stored, the attached identity is considered
            authoritative and stored on the token storage instance.

        :raises: :exc:`IdentityMismatchError` if the identity info in the token data
            does not match the stored identity info.
        :raises :exc:`MissingIdentityError` if the token data did not have identity
            information (generally due to missing the openid scope)
        """
        token_data_identity_id = _get_identity_id_from_token_data_by_resource_server(
            token_data_by_resource_server
        )

        if token_data_identity_id is None:
            raise MissingIdentityError(
                "Token grant response doesn't contain an id_token. This normally "
                "occurs if the auth flow didn't include 'openid' alongside other "
                "scopes."
            )

        if self.identity_id is None:
            self.identity_id = token_data_identity_id
            return

        if token_data_identity_id != self.identity_id:
            raise IdentityMismatchError(
                "Detected a change in identity associated with the token data.",
                stored_id=self.identity_id,
                new_id=token_data_identity_id,
            )

    def _validate_token_data_by_resource_server_meets_scope_requirements(
        self, token_data_by_resource_server: dict[str, TokenData]
    ) -> None:
        for resource_server, token_data in token_data_by_resource_server.items():
            self._validate_token_data(resource_server, token_data)

    def _validate_token_meets_scope_requirements(
        self, resource_server: str, token_data: TokenData
    ) -> None:
        """
        Given a particular resource server/token data, evaluate whether the token +
            user's consent forest meet the attached scope requirements.

        Note: If consent_client was omitted, only root scope requirements are validated.

        :raises: :exc:`UnmetScopeRequirements` if token/consent data does not meet the
            attached root or dependent scope requirements for the resource server.
        """
        required_scopes = self.scope_requirements.get(resource_server)

        # Short circuit - No scope requirements are, by definition, met.
        if required_scopes is None:
            return

        # 1. Does the token meet root scope requirements?
        root_scopes = token_data.scope.split(" ")
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
