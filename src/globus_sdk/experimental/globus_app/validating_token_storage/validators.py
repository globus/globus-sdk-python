from __future__ import annotations

import abc
import time
import typing as t

import globus_sdk
from globus_sdk.scopes.consents import ConsentForest
from globus_sdk.tokenstorage import TokenStorageData

from ..errors import (
    ExpiredTokenError,
    IdentityMismatchError,
    MissingIdentityError,
    MissingTokenError,
    UnmetScopeRequirementsError,
)
from .context import TokenValidationContext


class TokenDataValidator(abc.ABC):
    """
    TokenDataValidators are objects which define and apply validation criteria
    before token data is stored and after it is retrieved.

    They are expected to raise errors on failure.
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


class _OnlyBeforeValidator(TokenDataValidator):
    def after_retrieve(
        self,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
        context: TokenValidationContext,
    ) -> None:
        return None


class _OnlyAfterValidator(TokenDataValidator):
    def before_store(
        self,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
        context: TokenValidationContext,
    ) -> None:
        return None


class UnchangingIdentityIDValidator(_OnlyBeforeValidator):
    def before_store(
        self,
        token_data_by_resource_server: t.Mapping[  # pylint: disable=unused-argument
            str, TokenStorageData
        ],
        context: TokenValidationContext,
    ) -> None:
        """
        Validate that the identity info in the token data matches the prior identity
        info. If no prior identity was set, any new identity_id is accepted.

        :param token_data_by_resource_server: The data to validate.
        :param context: The validation context object, containing state of the system at
            the time of validation.

        :raises IdentityMismatchError: If the identity info in the token data
            does not match the stored identity info.
        :raises MissingIdentityError: If the token data did not have identity
            information (generally due to missing the openid scope).
        """
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
        """
        Validate the token data against scope requirements, but do not check
        dependent scopes before storage.

        :param token_data_by_resource_server: The data to validate.
        :param context: The validation context object, containing state of the system at
            the time of validation.
        """
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
        """
        Validate the token data against scope requirements, including dependent
        scope requirements.

        :param token_data_by_resource_server: The data to validate.
        :param context: The validation context object, containing state of the system at
            the time of validation.
        """
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
        Given a particular resource server and token data, evaluate whether or not the
        user's consent forest meet the attached scope requirements.

        .. note::

            If consent_client was omitted, only root scope requirements are validated.

        :param resource_server: The resource server whose scope requirements are being
            validated.
        :param token_data: The token data which is used for initial validation steps,
            and potential fail-fast before consents are inspected.
        :param identity_id: The identity ID of the user, from the surrounding context.
        :param eval_dependent: Whether to evaluate dependent scope requirements.
        :raises UnmetScopeRequirements: If token/consent data does not meet the
            attached root or dependent scope requirements for the resource server.
        :returns: None if all scope requirements are met (or indeterminable).
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
        """
        Poll for consents, caching and returning the result.

        :param identity_id: The identity_id of the user.
        """
        forest = self.consent_client.get_consents(identity_id).to_forest()
        # Cache the consent forest first.
        self._cached_consent_forest = forest
        return forest


class HasRefreshTokensValidator(_OnlyAfterValidator):
    def after_retrieve(
        self,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
        context: TokenValidationContext,  # pylint: disable=unused-argument
    ) -> None:
        """
        Verify that token data contains `refresh_token` values.

        :param token_data_by_resource_server: The data to validate.
        :param context: The validation context object, containing state of the system at
            the time of validation.

        :raises MissingTokenError: On failure to find a refresh_token.
        """
        for token_data in token_data_by_resource_server.values():
            if token_data.refresh_token is None:
                msg = f"No refresh_token for {token_data.resource_server}"
                raise MissingTokenError(msg, resource_server=token_data.resource_server)


class NotExpiredValidator(_OnlyAfterValidator):
    def after_retrieve(
        self,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
        context: TokenValidationContext,  # pylint: disable=unused-argument
    ) -> None:
        """
        Verify that the `expires_at_seconds` times in the token data are in the future.

        :param token_data_by_resource_server: The data to validate.
        :param context: The validation context object, containing state of the system at
            the time of validation.

        :raises ExpiredTokenError: If any token_data shows a past timestamp.
        """
        for token_data in token_data_by_resource_server.values():
            if token_data.expires_at_seconds < time.time():
                raise ExpiredTokenError(token_data.expires_at_seconds)
