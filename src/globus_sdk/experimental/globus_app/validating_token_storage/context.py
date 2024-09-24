from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class TokenValidationContext:
    """
    This is the context object which will be passed to token validators.

    It allows the ValidatingTokenStorage to capture state about its execution and pass
    that information, nicely bundled, to validators.
    """

    prior_identity_id: str | None
    token_data_identity_id: str | None
