from typing import Any, Dict, List, Optional

from globus_sdk.utils import PayloadWrapper
from globus_sdk.validation_utils import (
    AUTH_URN_REGEX,
    UUID_REGEX,
    LenValidator,
    ListValidator,
    RegexValidator,
)


class FlowCreateRequest(PayloadWrapper):
    r"""
    Class for specifying parameters used to create a flow in the Flows service. Used as
    the ``data`` argument in
    :meth:`create_flow <globus_sdk.FlowsClient.create_flow>`.

    :param title: A non-unique, human-friendly name used for displaying the provider to
        end users.
    :type title: str (1 - 128 characters)
    :param definition: JSON object specifying flows states and execution order. For a
        more detailed explanation of the flow definition, see
        `Authoring Flows <https://globus-automate-client.readthedocs.io/en/latest/authoring_flows.html>`_
    :type definition: dict
    :param input_schema: A JSON Schema to which Flow Invocation input must conform
    :type input_schema: dict
    :param subtitle: A concise summary of the flow’s purpose.
    :type subtitle: str (0 - 128 characters), optional
    :param description: A detailed description of the flow's purpose for end user
        display.
    :type description: str (0 - 4096 characters), optional
    :param flow_viewers: A set of Principal URN values, or the value "public"
        indicating entities who can view the flow

        Examples:

        .. code-block:: json

            [ "public" ]

        .. code-block:: json

            [
                "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
                "urn:globus:groups:id:c1dcd951-3f35-4ea3-9f28-a7cdeaf8b68f"
            ]


    :type flow_viewers: list[str], optional
    :param flow_starters: A set of Principal URN values, or the value
        "all_authenticated_users" indicating entities who can initiate a *Run* of
        the flow

        Examples:

        .. code-block:: json

            [ "all_authenticated_users" ]


        .. code-block:: json

            [
                "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
                "urn:globus:groups:id:c1dcd951-3f35-4ea3-9f28-a7cdeaf8b68f"
            ]

    :type flow_starters: list[str], optional
    :param flow_administrators: A set of Principal URN values indicating entities who
        can perform administrative operations on the flow (create, delete, update)

        Example:

        .. code-block:: json

            [
                "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
                "urn:globus:groups:id:c1dcd951-3f35-4ea3-9f28-a7cdeaf8b68f"
            ]

    :type flow_administrators: list[str], optional
    :param keywords: A set of terms used to categorize the flow used in query and
        discovery operations
    :type keywords: list[str] (0 - 1024 items), optional
    :param subscription_id: A uuid subscription id associated with this Flow. If no
        subscription_id is present, the Flow may be accepted, but have limits on how
        long or how much it can be used.
    :type subscription_id: str, optional
    :raises ValueError: Results from any values failing validation
    """  # noqa E501

    def __init__(
        self,
        title: str,
        definition: Dict[str, Any],
        input_schema: Dict[str, Any],
        subtitle: Optional[str] = None,
        description: Optional[str] = None,
        flow_viewers: Optional[List[str]] = None,
        flow_starters: Optional[List[str]] = None,
        flow_administrators: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        subscription_id: Optional[str] = None,
    ):
        super().__init__()
        title_validator = LenValidator(min_len=1, max_len=128)
        self["title"] = title_validator.validate(title, key="title")
        self["definition"] = definition
        self["input_schema"] = input_schema
        if subtitle is not None:
            subtitle_validator = LenValidator(min_len=0, max_len=128)
            self["subtitle"] = subtitle_validator.validate(subtitle, key="subtitle")
        if description is not None:
            description_validator = LenValidator(min_len=0, max_len=4096)
            self["description"] = description_validator.validate(
                description, key="description"
            )
        if flow_viewers is not None:
            viewers_validator = ListValidator(
                RegexValidator(f"^{AUTH_URN_REGEX}|public$")
            )
            self["flow_viewers"] = viewers_validator.validate(
                flow_viewers, "flow_viewers"
            )
        if flow_starters is not None:
            starters_validator = ListValidator(
                RegexValidator(f"^{AUTH_URN_REGEX}|all_authenticated_users$")
            )
            self["flow_starters"] = starters_validator.validate(
                flow_starters, "flow_starters"
            )
        if flow_administrators is not None:
            administrators_validator = ListValidator(
                RegexValidator(f"^{AUTH_URN_REGEX}$")
            )
            self["flow_administrators"] = administrators_validator.validate(
                flow_administrators, "flow_administrators"
            )
        if keywords is not None:
            keywords_validator = LenValidator(max_len=1024)
            self["keywords"] = keywords_validator.validate(keywords, "keywords")
        if subscription_id is not None:
            uuid_validator = RegexValidator(UUID_REGEX)
            self["subscription_id"] = uuid_validator.validate(
                subscription_id, "subscription_id"
            )
