from __future__ import annotations

import typing as t

from globus_sdk import _guards
from globus_sdk.exc import ErrorSubdocument, GlobusAPIError


class TimersAPIError(GlobusAPIError):
    """
    Error class to represent error responses from Timers.

    Has no particular additions to the base ``GlobusAPIError``, but implements a
    different method for parsing error responses from Timers due to the differences
    between various error formats used.
    """

    def _parse_undefined_error_format(self) -> bool:
        """
        Treat any top-level "error" key as an "array of size 1".
        Meaning that we'll see a single subdocument for data shaped like
            {
              "error": {
                "foo": "bar"
              }
            }

        Error shapes also include validation errors in a 'details' array:

            {
                "detail": [
                    {
                        "loc": ["body", "start"],
                        "msg": "field required",
                        "type": "value_error.missing"
                    },
                    {
                        "loc": ["body", "callback_url"],
                        "msg": "field required",
                        "type": "value_error.missing"
                    }
                ]
            }
        """
        # if there is not a top-level 'error' key and no top-level
        # 'detail' key, no special behavior is defined
        # fall-back to the base class implementation
        # but before that fallback, try the two relevant branches

        # if 'error' is present, use it to populate the errors array
        # extract 'code' from it
        # and extract 'messages' from it
        if isinstance(self._dict_data.get("error"), dict):
            self.errors = [ErrorSubdocument(self._dict_data["error"])]
            self.code = self._extract_code_from_error_array(self.errors)
            self.messages = self._extract_messages_from_error_array(self.errors)
            return True
        elif _guards.is_list_of(self._dict_data.get("detail"), dict):
            # FIXME:
            # the 'code' is currently being set explicitly by the
            # SDK in this case even though none was provided by
            # the service
            # in a future version of the SDK, the code should be `None`
            self.code = "Validation Error"

            # collect the errors array from details
            self.errors = [ErrorSubdocument(d) for d in self._dict_data["detail"]]

            # drop error objects which don't have the relevant fields
            # and then build custom 'messages' for Globus Timers errors
            details = list(_details_from_errors(self.errors))
            self.messages = [
                f"{e['msg']}: {'.'.join(k for k in e['loc'])}" for e in details
            ]
            return True
        else:
            return super()._parse_undefined_error_format()


def _details_from_errors(
    errors: list[ErrorSubdocument],
) -> t.Iterator[dict[str, t.Any]]:
    for d in errors:
        if not isinstance(d.get("msg"), str):
            continue
        loc_list = d.get("loc")
        if not _guards.is_list_of(loc_list, str):
            continue
        yield d.raw
