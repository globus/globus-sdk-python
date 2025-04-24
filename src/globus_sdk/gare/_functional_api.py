from __future__ import annotations

import logging
import sys
import typing as t

from globus_sdk import exc

from ._auth_requirements_error import GARE
from ._variants import (
    LegacyAuthorizationParametersError,
    LegacyAuthRequirementsErrorVariant,
    LegacyConsentRequiredAPError,
    LegacyConsentRequiredTransferError,
)

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias


AnyErrorDocumentType: TypeAlias = (
    "exc.GlobusAPIError | exc.ErrorSubdocument | dict[str, t.Any]"
)

log = logging.getLogger(__name__)


def to_gare(error: AnyErrorDocumentType) -> GARE | None:
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
        # first, try to parse a GARE from the root document,
        # and if we can do so, return it
        authreq_error = _lenient_dict2gare(error.raw_json)
        if authreq_error is not None:
            return authreq_error

        # Iterate over ErrorSubdocuments
        for subdoc in error.errors:
            authreq_error = _lenient_dict2gare(subdoc.raw)
            if authreq_error is not None:
                # Return only the first auth requirements error we encounter
                return authreq_error

        # We failed to find a Globus Auth Requirements Error
        return None
    elif isinstance(error, ErrorSubdocument):
        return _lenient_dict2gare(error.raw)
    else:
        return _lenient_dict2gare(error)


def to_gares(errors: list[AnyErrorDocumentType]) -> list[GARE]:
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

    maybe_gares: list[GARE | None] = []
    for error in errors:
        # when handling an API error, avoid `to_gare(error)` because that will
        # only unpack a single result
        if isinstance(error, GlobusAPIError):
            # Use the ErrorSubdocuments when handling API error types
            maybe_gares.extend(to_gare(e) for e in error.errors)
            # Also use the root document, but only if there is an `"errors"`
            # key inside of the error document
            # Why? Because the *default* for `.errors` when there is no inner
            # `"errors"` array is an array containing the root document as a
            # subdocument
            if isinstance(error.raw_json, dict) and "errors" in error.raw_json:
                # use dict parsing directly so that the native descent in 'to_gare'
                # to subdocuments does not apply in this case
                maybe_gares.append(_lenient_dict2gare(error.raw_json))
        else:
            maybe_gares.append(to_gare(error))

    # Remove any errors that did not resolve to a Globus Auth Requirements Error
    return [error for error in maybe_gares if error is not None]


def _lenient_dict2gare(error_dict: dict[str, t.Any] | None) -> GARE | None:
    """
    Parse a GARE from a dict, accepting legacy variants.

    If given ``None``, returns ``None``. This allows this to accept inputs
    which are themselves dict|None.

    :param error_dict: the error input
    :eturns: ``None`` on a failed parse
    """
    if error_dict is None:
        return None

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


def is_gare(error: AnyErrorDocumentType) -> bool:
    """
    Return True if the provided error matches a known
    Globus Auth Requirements Error format.

    :param error: The error to check.
    """
    return to_gare(error) is not None


def has_gares(errors: list[AnyErrorDocumentType]) -> bool:
    """
    Return True if any of the provided errors match a known
    Globus Auth Requirements Error format.

    :param errors: The errors to check.
    """
    return any(is_gare(error) for error in errors)
