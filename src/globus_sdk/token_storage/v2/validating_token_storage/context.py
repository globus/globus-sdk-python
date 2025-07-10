from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class TokenValidationContext:
    """
    A data object of information available to
    :class:`TokenDataValidators <TokenDataValidator>` during validation.

    :ivar str | None prior_identity_id: The identity ID associated with the
        :class:`ValidatingTokenStorage` before the operation began, if there was one.
    :ivar str | None token_data_identity_id: The identity ID extracted from the token
        data being validated.
    """

    prior_identity_id: str | None
    token_data_identity_id: str | None
