from __future__ import annotations

from globus_sdk import _guards
from globus_sdk.exc import ErrorSubdocument, GlobusAPIError


class FlowsAPIError(GlobusAPIError):
    """
    Error class to represent error responses from Flows.
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
        """
        # if there is not a top-level 'error' key, no special behavior is defined
        # fall-back to the base class implementation
        if not isinstance(self._dict_data.get("error"), dict):
            return super()._parse_undefined_error_format()

        self.errors = [ErrorSubdocument(self._dict_data["error"])]
        self.code = self._extract_code_from_error_array(self.errors)

        details = self._dict_data["error"].get("detail")
        if _guards.is_list_of(details, dict):
            self.messages = [
                error_detail["msg"]
                for error_detail in details
                if isinstance(error_detail.get("msg"), str)
            ]
        else:
            self.messages = self._extract_messages_from_error_array(self.errors)

        return True
