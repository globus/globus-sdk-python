from __future__ import annotations

import logging
import typing as t

from globus_sdk import exc

from ._auth_requirements_error import GARE
from ._variants import (
    LegacyAuthorizationParametersError,
    LegacyAuthRequirementsErrorVariant,
    LegacyConsentRequiredAPError,
    LegacyConsentRequiredTransferError,
)

log = logging.getLogger(__name__)


def to_gare(
    error: exc.GlobusAPIError | exc.ErrorSubdocument | dict[str, t.Any]
) -> GARE | None:
    """
    Converts a GlobusAPIError, ErrorSubdocument, or dict into a
    GARE by attempting to match to GARE (preferred) or legacy variants.

    .. note::

        A GlobusAPIError may contain multiple errors, and in this case only a single
        GARE is returned for the first error that matches a known format.


    If the provided error does not match a known format, None is returned.

    :param error: The error to convert.
    """
    from globus_sdk.exc import ErrorSubdocument, GlobusAPIError

    # GlobusAPIErrors may contain more than one error, so we consider all of them
    # even though we only return the first.
    if isinstance(error, GlobusAPIError):
        # Iterate over ErrorSubdocuments
        for subdoc in error.errors:
            authreq_error = to_gare(subdoc)
            if authreq_error is not None:
                # Return only the first auth requirements error we encounter
                return authreq_error
        # We failed to find a Globus Auth Requirements Error
        return None
    elif isinstance(error, ErrorSubdocument):
        error_dict = error.raw
    else:
        error_dict = error

    # Prefer a proper auth requirements error, if possible
    try:
        return GARE.from_dict(error_dict)
    except exc.ValidationError as err:
        log.debug(f"Failed to parse error as 'GARE' ({err})")

    supported_variants: list[type[LegacyAuthRequirementsErrorVariant]] = [
        LegacyAuthorizationParametersError,
        LegacyConsentRequiredTransferError,
        LegacyConsentRequiredAPError,
    ]
    for variant in supported_variants:
        try:
            return variant.from_dict(error_dict).to_auth_requirements_error()
        except exc.ValidationError as err:
            log.debug(f"Failed to parse error as '{variant.__name__}' ({err})")

    return None


def to_gares(
    errors: list[exc.GlobusAPIError | exc.ErrorSubdocument | dict[str, t.Any]]
) -> list[GARE]:
    """
    Converts a list of GlobusAPIErrors, ErrorSubdocuments, or dicts into a list of
    GAREs by attempting to match each error to GARE (preferred) or legacy variants.

    .. note::

        A GlobusAPIError may contain multiple errors, so the result
        list could be longer than the provided list.

    If no errors match any known formats, an empty list is returned.

    :param errors: The errors to convert.
    """
    from globus_sdk.exc import GlobusAPIError

    candidate_errors: list[exc.ErrorSubdocument | dict[str, t.Any]] = []
    for error in errors:
        if isinstance(error, GlobusAPIError):
            # Use the ErrorSubdocuments
            candidate_errors.extend(error.errors)
        else:
            candidate_errors.append(error)

    # Try to convert all candidate errors to auth requirements errors
    all_errors = [to_gare(error) for error in candidate_errors]

    # Remove any errors that did not resolve to a Globus Auth Requirements Error
    return [error for error in all_errors if error is not None]


def is_gare(
    error: exc.GlobusAPIError | exc.ErrorSubdocument | dict[str, t.Any]
) -> bool:
    """
    Return True if the provided error matches a known
    Globus Auth Requirements Error format.

    :param error: The error to check.
    """
    return to_gare(error) is not None


def has_gares(
    errors: list[exc.GlobusAPIError | exc.ErrorSubdocument | dict[str, t.Any]]
) -> bool:
    """
    Return True if any of the provided errors match a known
    Globus Auth Requirements Error format.

    :param errors: The errors to check.
    """
    return any(is_gare(error) for error in errors)
