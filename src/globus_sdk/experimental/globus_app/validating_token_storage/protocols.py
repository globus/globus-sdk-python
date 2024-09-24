import sys
import typing as t

from globus_sdk.experimental.tokenstorage import TokenStorageData

from .context import TokenValidationContext

if sys.version_info < (3, 8):
    from typing_extensions import Protocol, runtime_checkable
else:
    from typing import Protocol, runtime_checkable


@runtime_checkable
class TokenDataValidator(Protocol):
    def __call__(
        self,
        token_data_by_resource_server: t.Mapping[str, TokenStorageData],
        context: TokenValidationContext,
    ) -> None:
        pass
