from __future__ import annotations

import sys
import typing as t

from globus_sdk.experimental.tokenstorage import TokenStorageData

from .context import TokenValidationContext

if sys.version_info < (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol


class TokenDataValidatorFunc(Protocol):
    """
    A validator function is a callable which checks token data against some
    constraints.
    """

    def __call__(
        self,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
        context: TokenValidationContext,
    ) -> None: ...


# validator objects are objects which support at least one of the two well-defined hook
# methods for a validator
# if a method is not supported, it must be set explicitly as `None` -- this will be
# checked at runtime
#
# there is no such thing as a TokenDataValidator implementation which defines one method
# and leaves the other one undefined


class SupportsOnlyBeforeStoreValidator(Protocol):
    after_retrieve: None

    def before_store(
        self,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
        context: TokenValidationContext,
    ) -> None: ...


class SupportsOnlyAfterRetrieveValidator(Protocol):
    before_store: None

    def after_retrieve(
        self,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
        context: TokenValidationContext,
    ) -> None: ...


class SupportsBeforeStoreAndAfterRetrieveValidator(Protocol):
    def before_store(
        self,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
        context: TokenValidationContext,
    ) -> None: ...

    def after_retrieve(
        self,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
        context: TokenValidationContext,
    ) -> None: ...


TokenDataValidator = t.Union[
    SupportsOnlyAfterRetrieveValidator,
    SupportsOnlyBeforeStoreValidator,
    SupportsBeforeStoreAndAfterRetrieveValidator,
]
