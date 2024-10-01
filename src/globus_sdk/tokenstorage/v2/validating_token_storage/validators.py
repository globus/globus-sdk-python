from __future__ import annotations

import abc
import time
import typing as t

import globus_sdk
from globus_sdk.scopes.consents import ConsentForest

from ..token_data import TokenStorageData
from .context import TokenValidationContext
from .errors import (
    ExpiredTokenError,
    IdentityMismatchError,
    MissingIdentityError,
    MissingTokenError,
    UnmetScopeRequirementsError,
)


class TokenDataValidator(abc.ABC):
    """
    The abstract base class for custom token validation logic.

    Implementations should raise a :class:`TokenValidationError` if a validation error
    is encountered.
    """

    @abc.abstractmethod
    def before_store(
        self,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
        context: TokenValidationContext,
    ) -> None:
        """
        Validate token data against this validator's constraints before it is
        written to token storage.

        :param token_data_by_resource_server: The data to validate.
        :param context: The validation context object, containing state of the system at
            the time of validation.

        :raises TokenValidationError: On failure.
        """

    @abc.abstractmethod
    def after_retrieve(
        self,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
        context: TokenValidationContext,
    ) -> None:
        """
        Validate token data against this validator's constraints after it is
        retrieved from token storage.

        :param token_data_by_resource_server: The data to validate.
        :param context: The validation context object, containing state of the system at
            the time of validation.

        :raises TokenValidationError: On failure.
        """


class _OnlyBeforeValidator(TokenDataValidator, abc.ABC):
    def after_retrieve(
        self,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
        context: TokenValidationContext,
    ) -> None:
        return None


class _OnlyAfterValidator(TokenDataValidator, abc.ABC):
    def before_store(
        self,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
        context: TokenValidationContext,
    ) -> None:
        return None


class HasRefreshTokensValidator(_OnlyAfterValidator):
    """
    A validator to validate that token data contains refresh tokens.

    *  This validator only runs `after_retrieve`.

    :raises MissingTokenError: If any token data does not contain a refresh token.
    """

    def after_retrieve(
        self,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
        context: TokenValidationContext,  # pylint: disable=unused-argument
    ) -> None:
        for token_data in token_data_by_resource_server.values():
            if token_data.refresh_token is None:
                msg = f"No refresh_token for {token_data.resource_server}"
                raise MissingTokenError(msg, resource_server=token_data.resource_server)


class NotExpiredValidator(_OnlyAfterValidator):
    """
    A validator to validate that token data has not expired.

    * This validator only runs `after_retrieve`.

    :raises ExpiredTokenError: If any token data shows has expired.
    """

    def after_retrieve(
        self,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
        context: TokenValidationContext,  # pylint: disable=unused-argument
    ) -> None:
        for token_data in token_data_by_resource_server.values():
            if token_data.expires_at_seconds < time.time():
                raise ExpiredTokenError(token_data.expires_at_seconds)


class UnchangingIdentityIDValidator(_OnlyBeforeValidator):
    """
    A validator to validate that user identity does not change across token grants.

    *   This validator only runs `before_store`.

    :raises IdentityMismatchError: If identity info changes across token storage
        operations.
    :raises MissingIdentityError: If the token data did not have any identity
        information.
    """

    def before_store(
        self,
        token_data_by_resource_server: t.Mapping[  # pylint: disable=unused-argument
            str, TokenStorageData
        ],
        context: TokenValidationContext,
    ) -> None:
        if context.token_data_identity_id is None:
            raise MissingIdentityError(
                "Token grant response doesn't contain an id_token. This normally "
                "occurs if the auth flow didn't include 'openid' alongside other "
                "scopes."
            )

        # no prior ID means we cannot validate the content further
        if context.prior_identity_id is None:
            return

        if context.token_data_identity_id != context.prior_identity_id:
            raise IdentityMismatchError(
                "Detected a change in identity associated with the token data.",
                stored_id=context.prior_identity_id,
                new_id=context.token_data_identity_id,
            )


class ScopeRequirementsValidator(TokenDataValidator):
    """
    A validator to validate that token data meets scope requirements.

    A scope requirement, i.e., "transfer:all[collection:data_access]", can be broken
    into two parts: the **root scope**, "transfer:all", and one or more
    **dependent scopes**, "collection:data_access".

    *   On `before_store`, this validator only evaluates **root** scope requirements.
    *   On `after_retrieve`, this validator evaluates both **root** and **dependent**
        scope requirements.

    .. note::

        Dependent scopes are only evaluated if an identity ID is extractable from
        token grants. If no identity ID is available, dependent scope evaluation
        is silently skipped.

    :param scope_requirements: A mapping of resource servers to required scopes.
    :param consent_client: An AuthClient to fetch consents with. This auth client must
        have (or have access to) any valid Globus Auth scoped token.

    :raises UnmetScopeRequirementsError: If any scope requirements are not met.
    """

    def __init__(
        self,
        scope_requirements: t.Mapping[str, t.Sequence[globus_sdk.Scope]],
        consent_client: globus_sdk.AuthClient,
    ) -> None:
        self.scope_requirements = scope_requirements
        self.consent_client: globus_sdk.AuthClient = consent_client
        self._cached_consent_forest: ConsentForest | None = None

    def before_store(
        self,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
        context: TokenValidationContext,
    ) -> None:
        identity_id = context.token_data_identity_id or context.prior_identity_id
        for resource_server, token_data in token_data_by_resource_server.items():
            self._validate_token_data_meets_scope_requirements(
                resource_server=resource_server,
                token_data=token_data,
                identity_id=identity_id,
                eval_dependent=False,
            )

    def after_retrieve(
        self,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
        context: TokenValidationContext,
    ) -> None:
        identity_id = context.token_data_identity_id or context.prior_identity_id
        for token_data in token_data_by_resource_server.values():
            self._validate_token_data_meets_scope_requirements(
                resource_server=token_data.resource_server,
                token_data=token_data,
                identity_id=identity_id,
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
        Evaluate whether the scope requirements for a given resource server are met.

        :param resource_server: A resource server to access scope requirements.
        :param token_data: A token data object to validate.
        :param identity_id: The identity ID of the user, from the surrounding context.
        :param eval_dependent: Whether to evaluate dependent scope requirements.

        :raises UnmetScopeRequirements: If token/consent data does not meet the
            attached root or dependent scope requirements for the resource server.
        """
        required_scopes = self.scope_requirements.get(resource_server)
        # Short circuit - No scope requirements are, by definition, met.
        if required_scopes is None:
            return

        # 1. Does the token meet root scope requirements?
        root_scopes = token_data.scope.split()
        if not all(scope.scope_string in root_scopes for scope in required_scopes):
            raise UnmetScopeRequirementsError(
                "Unmet scope requirements",
                scope_requirements={
                    k: list(v) for k, v in self.scope_requirements.items()
                },
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

        # Identity id is required to fetch consents.
        # if we cannot fetch consents, we cannot do any further validation
        if identity_id is None:
            return

        # 2b. Poll for fresh consents and try again.
        forest = self._poll_and_cache_consents(identity_id)
        if not forest.meets_scope_requirements(required_scopes):
            raise UnmetScopeRequirementsError(
                "Unmet dependent scope requirements",
                scope_requirements={
                    k: list(v) for k, v in self.scope_requirements.items()
                },
            )

    def _poll_and_cache_consents(self, identity_id: str) -> ConsentForest:
        forest = self.consent_client.get_consents(identity_id).to_forest()
        self._cached_consent_forest = forest
        return forest
