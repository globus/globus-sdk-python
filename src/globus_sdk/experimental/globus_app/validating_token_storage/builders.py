from __future__ import annotations

import typing as t

import globus_sdk
from globus_sdk.experimental.globus_app.config import GlobusAppConfig
from globus_sdk.experimental.tokenstorage import TokenStorage

from .protocols import TokenDataValidator
from .storage import ValidatingTokenStorage
from .validators import ScopeRequirementsValidator, UnchangingIdentityIDValidator


def build_default_validating_token_storage(
    *,
    token_storage: TokenStorage,
    config: GlobusAppConfig,
    consent_client: globus_sdk.AuthClient,
    scope_requirements: t.Mapping[str, t.Sequence[globus_sdk.Scope]],
    add_validators: t.Iterable[TokenDataValidator] = (),
) -> ValidatingTokenStorage:
    """
    Given the appropriate configuration data, build the default
    ValidatingTokenStorage for use within GlobusApp.

    :param token_storage: The token storage to wrap in a ValidatingTokenStorage.
    :param config: The app config which is being used to build the GlobusApp.
    :param consent_client: The app's internal AuthClient instance which is used
        to fetch consent information.
    :param scope_requirements: The scope requirements for the app.
    :param add_validators: Additional validators to insert into evaluation order
        ahead of the default validators.
    """
    validating_token_storage = ValidatingTokenStorage(
        token_storage,
        validators=add_validators,
    )

    # construct ValidatingTokenStorage around the TokenStorage and
    # our initial scope requirements
    scope_validator = ScopeRequirementsValidator(scope_requirements, consent_client)
    identity_id_validator = UnchangingIdentityIDValidator()

    default_validators: tuple[TokenDataValidator, ...] = (
        scope_validator,
        identity_id_validator,
    )

    # use validators to enforce invariants about scopes and identity ID
    validating_token_storage.validators.extend(default_validators)

    return validating_token_storage
