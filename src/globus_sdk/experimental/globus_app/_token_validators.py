from __future__ import annotations

import typing as t

import globus_sdk
from globus_sdk.experimental.tokenstorage import TokenStorageData
from globus_sdk.scopes.consents import ConsentForest

from ._identity_id_reader import IdentityIDReader
from ._validating_token_storage import ValidatingTokenStorage
from .errors import (
    IdentityMismatchError,
    MissingIdentityError,
    UnmetScopeRequirementsError,
)


class UnchangingIdentityIDValidator:
    def __init__(self) -> None:
        self.identity_id: str | None = None
        self._reader = IdentityIDReader()

    def before_store(
        self,
        token_storage: ValidatingTokenStorage,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
    ) -> None:
        """
        Validate that the identity info in the token data matches the prior identity
        info. If no prior identity was set, the incoming identity_id may be stored
        (but only if the token storage

        :param token_storage: The token storage which invoked this validator.
        :param token_data_by_resource_server: The data to validate.

        :raises IdentityMismatchError: if the identity info in the token data
            does not match the stored identity info.
        :raises MissingIdentityError: if the token data did not have identity
            information (generally due to missing the openid scope)
        """
        # if an identity ID is not known to the validator, but one is known to the
        # storage, trust the storage and set that on the validator
        if self.identity_id is None:
            self.identity_id = token_storage.identity_id

        token_data_identity_id = self._reader.read_token_data_by_resource_server(
            token_data_by_resource_server
        )

        if token_data_identity_id is None:
            raise MissingIdentityError(
                "Token grant response doesn't contain an id_token. This normally "
                "occurs if the auth flow didn't include 'openid' alongside other "
                "scopes."
            )

        # at this point, if the identity_id is not known, this can only mean that
        # we are storing an initial response (which has not been seen by the storage
        # before now), as from a new login flow
        #
        # therefore, trust the token data and set that as the expected identity_id
        if self.identity_id is None:
            self.identity_id = token_data_identity_id
            return

        if token_data_identity_id != self.identity_id:
            raise IdentityMismatchError(
                "Detected a change in identity associated with the token data.",
                stored_id=self.identity_id,
                new_id=token_data_identity_id,
            )


class ScopeRequirementsValidator:
    def __init__(
        self,
        scope_requirements: dict[str, list[globus_sdk.Scope]],
        consent_client: globus_sdk.AuthClient,
    ) -> None:
        self.scope_requirements = scope_requirements
        self.consent_client: globus_sdk.AuthClient = consent_client
        self._cached_consent_forest: ConsentForest | None = None

    def before_store(
        self,
        token_storage: ValidatingTokenStorage,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
    ) -> None:
        """
        Validate the token data against scope requirements, but do not check
        dependent scopes before storage.

        :param token_storage: The token storage which invoked this validator.
        :param token_data_by_resource_server: The data to validate.
        """
        for resource_server, token_data in token_data_by_resource_server.items():
            self._validate_token_data_meets_scope_requirements(
                resource_server=resource_server,
                token_data=token_data,
                identity_id=token_storage.identity_id,
                eval_dependent=False,
            )

    def after_retrieve(
        self, token_storage: ValidatingTokenStorage, token_data: TokenStorageData
    ) -> None:
        """
        Validate the token data against scope requirements, including dependent
        scope requirements.

        :param token_storage: The token storage which invoked this validator.
        :param token_data: The data to validate.
        """
        self._validate_token_data_meets_scope_requirements(
            resource_server=token_data.resource_server,
            token_data=token_data,
            identity_id=token_storage.identity_id,
        )

    def _validate_token_data_meets_scope_requirements(
        self,
        *,
        resource_server: str,
        token_data: TokenStorageData,
        identity_id: str | None,
        eval_dependent: bool = True,
    ) -> None:
        """
        Given a particular resource server/token data, evaluate whether the token +
            user's consent forest meet the attached scope requirements.

        Note: If consent_client was omitted, only root scope requirements are validated.

        :param resource_server: The resource server string to validate against.
        :param token_data: The token data to validate against.
        :param identity_id: The identity ID of the user, from the surrounding context.
        :param eval_dependent: Whether to evaluate dependent scope requirements.
        :raises UnmetScopeRequirements: if token/consent data does not meet the
            attached root or dependent scope requirements for the resource server.
        :returns: None if all scope requirements are met (or indeterminable).
        """
        required_scopes = self.scope_requirements.get(resource_server)

        # Short circuit - No scope requirements are, by definition, met.
        if required_scopes is None:
            return

        # 1. Does the token meet root scope requirements?
        root_scopes = token_data.scope.split(" ")
        if not all(scope.scope_string in root_scopes for scope in required_scopes):
            raise UnmetScopeRequirementsError(
                "Unmet scope requirements",
                scope_requirements=self.scope_requirements,
            )

        # Short circuit - No dependent scopes; don't validate them.
        if not eval_dependent or not any(
            scope.dependencies for scope in required_scopes
        ):
            return

        # 2. Does the consent forest meet all dependent scope requirements?
        # 2a. Try with the cached consent forest first.
        forest = self._cached_consent_forest
        if forest is not None and forest.meets_scope_requirements(required_scopes):
            return

        # if we cannot fetch consents, we cannot do any further validation
        if identity_id is None:
            return

        # 2b. Poll for fresh consents and try again.
        forest = self._poll_and_cache_consents(identity_id)
        if not forest.meets_scope_requirements(required_scopes):
            raise UnmetScopeRequirementsError(
                "Unmet dependent scope requirements",
                scope_requirements=self.scope_requirements,
            )

    def _poll_and_cache_consents(self, identity_id: str) -> ConsentForest:
        """
        Poll for consents, caching and returning the result.

        :param identity_id: The identity_id of the user.
        """
        forest = self.consent_client.get_consents(identity_id).to_forest()
        # Cache the consent forest first.
        self._cached_consent_forest = forest
        return forest
