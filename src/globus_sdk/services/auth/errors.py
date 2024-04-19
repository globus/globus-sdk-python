from __future__ import annotations

import logging

from globus_sdk import exc

log = logging.getLogger(__name__)


class AuthAPIError(exc.GlobusAPIError):
    """
    Error class for the API components of Globus Auth.
    """

    def _post_parse_hook(self) -> bool:
        # if there was only one error ID set in the response, use that as the request_id
        # this allows for some errors to omit the 'id':
        #
        #    errors=[{"id": "foo"}, {}]
        #
        # or for all errors to have the same 'id':
        #
        #    errors=[{"id": "foo"}, {"id": "foo"}]
        #
        # but not for errors to have mixed/different 'id' values:
        #
        #    errors=[{"id": "foo"}, {"id": "bar"}]

        # step 1, collect error IDs
        error_ids = {suberror.get("id") for suberror in self.errors}
        # step 2, remove `None` from any sub-errors which did not set error_id or
        # explicitly set it to null
        error_ids.discard(None)
        # step 3, check if there was exactly one error ID and it was a string
        if len(error_ids) == 1:
            maybe_error_id = error_ids.pop()
            if isinstance(maybe_error_id, str):
                self.request_id = maybe_error_id

        return True
