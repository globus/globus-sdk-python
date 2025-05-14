from __future__ import annotations

import typing as t

from globus_sdk import _guards
from globus_sdk.exc import ErrorSubdocument, GlobusAPIError


class TimersAPIError(GlobusAPIError):
    """
    Error class to represent error responses from Timers.

    Implements a dedicated method for parsing error responses from Timers due
    to the differences between various error formats used.
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
        # extract 'code' and 'messages' from it
        if isinstance(self._dict_data.get("error"), dict):
            self.errors = [ErrorSubdocument(self._dict_data["error"])]
            self.code = self._extract_code_from_error_array(self.errors)
            self.messages = self._extract_messages_from_error_array(self.errors)
            return True
        elif _guards.is_list_of(self._dict_data.get("detail"), dict):
            # collect the errors array from details
            self.errors = [
                ErrorSubdocument(d, message_fields=("msg",))
                for d in self._dict_data["detail"]
            ]
            # extract a 'code' if there is one
            self.code = self._extract_code_from_error_array(self.errors)

            # build custom 'messages' for this case
            self.messages = [
                f"{message}: {loc}"
                for (message, loc) in _parse_detail_docs(self.errors)
            ]
            return True
        else:
            return super()._parse_undefined_error_format()


def _parse_detail_docs(
    errors: list[ErrorSubdocument],
) -> t.Iterator[tuple[str, str]]:
    for d in errors:
        if d.message is None:
            continue
        loc_list = d.get("loc")
        if not _guards.is_list_of(loc_list, str):
            continue
        yield (d.message, ".".join(loc_list))
