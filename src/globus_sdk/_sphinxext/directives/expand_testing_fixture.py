import json
import typing as t

from docutils.parsers.rst import directives

from globus_sdk._testing import ResponseList

from .add_content_directive import AddContentDirective


class ExpandTestingFixture(AddContentDirective):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        "case": directives.unchanged,
    }

    def gen_rst(self) -> t.Iterator[str]:
        from globus_sdk._testing import get_response_set

        response_set_name = self.arguments[0]
        casename = "default"
        if "case" in self.options:
            casename = self.options["case"].strip()
        response_set = get_response_set(response_set_name)
        response = response_set.lookup(casename)
        if isinstance(response, ResponseList):
            # If the default responses is a list of responses, use the first one
            response = response.responses[0]
        if response.json is not None:
            yield ".. code-block:: json"
            yield ""
            output_lines = json.dumps(
                response.json, indent=2, separators=(",", ": ")
            ).split("\n")
            for line in output_lines:
                yield f"    {line}"
        elif response.body is not None:
            yield ".. code-block:: text"
            yield ""
            output_lines = response.body.split("\n")
            for line in output_lines:
                yield f"    {line}"
        else:
            raise RuntimeError(
                "Error loading example content for response "
                f"{response_set_name}:{casename}. Neither JSON nor text body was found."
            )
