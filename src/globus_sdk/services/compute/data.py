from __future__ import annotations

from globus_sdk import utils
from globus_sdk._types import UUIDLike
from globus_sdk.utils import MISSING, MissingType


class ComputeFunctionMetadata(utils.PayloadWrapper):
    """A wrapper for function metadata.

    :param python_version: The Python version used to serialize the function.
    :param sdk_version: The Globus Compute SDK version used to serialize the function.
    """

    def __init__(
        self,
        *,
        python_version: str | MissingType = MISSING,
        sdk_version: str | MissingType = MISSING,
    ):
        super().__init__()
        self["python_version"] = python_version
        self["sdk_version"] = sdk_version


class ComputeFunctionDocument(utils.PayloadWrapper):
    """A function registration document.

    :param function_name: The name of the function.
    :param function_code: The serialized function source code.
    :param description: The description of the function.
    :param metadata: The metadata of the function.
    :param group: Restrict function access to members of this Globus group.
    :param public: Indicates whether the function is public.
    """

    def __init__(
        self,
        *,
        function_name: str,
        function_code: str,
        description: str | MissingType = MISSING,
        metadata: ComputeFunctionMetadata | MissingType = MISSING,
        group: UUIDLike | MissingType = MISSING,
        public: bool = False,
    ):
        super().__init__()
        self["function_name"] = function_name
        self["function_code"] = function_code
        self["description"] = description
        self["metadata"] = metadata
        self["group"] = group
        self["public"] = public
