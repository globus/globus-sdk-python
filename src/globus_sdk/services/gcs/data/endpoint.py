from __future__ import annotations

import typing as t

from globus_sdk import utils
from globus_sdk.services.gcs.data._common import DatatypeCallback, ensure_datatype
from globus_sdk.utils import MISSING, MissingType


class EndpointDocument(utils.PayloadWrapper):
    r"""

    :param data_type: Explicitly set the ``DATA_TYPE`` value for this endpoint document.
        Normally ``DATA_TYPE`` is deduced from the provided parameters and should not be
        set. To maximize compatibility with different versions of GCS, only set this
        value when necessary.

    :param contact_email: Email address of the support contact for this endpoint. This
        is visible to end users so that they may contact your organization for support.
    :param contact_info: Other non-email contact information for the endpoint, e.g.
        phone and mailing address. This is visible to end users for support.
    :param department: Department within organization that runs the server(s).
        Searchable. Unicode string, max 1024 characters, no new lines.
    :param description: A description of the endpoint.
    :param display_name: Friendly name for the endpoint, not unique. Unicode string, no
        new lines (\r or \n). Searchable.
    :param info_link: Link to a web page with more information about the endpoint. The
        administrator is responsible for running a website at this URL and verifying
        that it is accepting public connections.
    :param network_use: Control how Globus interacts with this endpoint over the
        network. Allowed values are:

        * ``normal``: (Default) Uses an average level of concurrency and
          parallelism. The levels depend on the number of physical servers in the
          endpoint.
        * ``minimal``: Uses a minimal level of concurrency and parallelism.
        * ``aggressive``: Uses a high level of concurrency and parallelism.
        * ``custom``: Uses custom values of concurrency and parallelism set by the
          endpoint admin. When setting this level, you must also set the
          ``max_concurrency``, ``preferred_concurrency``, ``max_parallelism``, and
          ``preferred_parallelism`` properties.
    :param organization: Organization that runs the server(s). Searchable. Unicode
        string, max 1024 characters, no new lines.
    :param subscription_id: The id of the subscription that is managing this endpoint.
        This may be the special value DEFAULT when using this as input to PATCH or PUT
        to use the caller’s default subscription id.

    :param keywords: List of search keywords for the endpoint. Unicode string, max 1024
        characters total across all strings.

    :param allow_udt: Allow data transfer on this endpoint using the UDT protocol.
    :param public: Flag indicating whether this endpoint is visible to all other Globus
        users. If false, only users which have been granted a role on the endpoint or
        one of its collections, or belong to a domain allowed access to any of its
        storage gateways may view it.

    :param gridftp_control_channel_port: TCP port for the Globus control channel to
        listen on. By default, the control channel is passed through 443 with an ALPN
        header containing the value "ftp".
    :param max_concurrency: Admin-specified value when the ``network_use`` property’s
        value is ``"custom"``; otherwise the preset value for the specified
        ``network_use``.
    :param max_parallelism: Admin-specified value when the ``network_use`` property’s
        value is ``"custom"``; otherwise the preset value for the specified
        ``network_use``.
    :param preferred_concurrency: Admin-specified value when the ``network_use``
        property’s value is ``"custom"``; otherwise the preset value for the specified
        ``network_use``.
    :param preferred_parallelism: Admin-specified value when the ``network_use``
        property’s value is ``"custom"``; otherwise the preset value for the specified
        ``network_use``.
    """

    DATATYPE_BASE = "endpoint"
    DATATYPE_VERSION_IMPLICATIONS: dict[str, tuple[int, int, int]] = {
        "gridftp_control_channel_port": (1, 1, 0),
    }
    DATATYPE_VERSION_CALLBACKS: tuple[DatatypeCallback, ...] = ()

    # Note: The fields below represent the set of mutable endpoint fields in
    #   an Endpoint#1.2.0 document.
    #   https://docs.globus.org/globus-connect-server/v5.4/api/schemas/Endpoint_1_2_0_schema/
    # Read-only fields (e.g. "gcs_manager_url", "endpoint_id", and
    #   "earliest_last_access") are intentionally omitted as this data class is designed
    #   for input construction not response parsing.
    def __init__(
        self,
        *,
        # data type
        data_type: str | MissingType = MISSING,
        # strs
        contact_email: str | MissingType = MISSING,
        contact_info: str | MissingType = MISSING,
        department: str | MissingType = MISSING,
        description: str | MissingType = MISSING,
        display_name: str | MissingType = MISSING,
        info_link: str | MissingType = MISSING,
        network_use: (
            t.Literal["normal", "minimal", "aggressive", "custom"] | MissingType
        ) = MISSING,
        organization: str | MissingType = MISSING,
        # nullable strs
        subscription_id: str | None | MissingType = MISSING,
        # str lists
        keywords: t.Iterable[str] | MissingType = MISSING,
        # bools
        allow_udt: bool | MissingType = MISSING,
        public: bool | MissingType = MISSING,
        # ints
        max_concurrency: int | MissingType = MISSING,
        max_parallelism: int | MissingType = MISSING,
        preferred_concurrency: int | MissingType = MISSING,
        preferred_parallelism: int | MissingType = MISSING,
        # nullable ints
        gridftp_control_channel_port: int | None | MissingType = MISSING,
        # additional fields
        additional_fields: dict[str, t.Any] | MissingType = MISSING,
    ):
        super().__init__()
        self["DATA_TYPE"] = data_type
        self["contact_email"] = contact_email
        self["contact_info"] = contact_info
        self["department"] = department
        self["description"] = description
        self["display_name"] = display_name
        self["info_link"] = info_link
        self["network_use"] = network_use
        self["organization"] = organization
        self["keywords"] = (
            keywords
            if isinstance(keywords, MissingType)
            else list(utils.safe_strseq_iter(keywords))
        )
        self["allow_udt"] = allow_udt
        self["public"] = public
        self["max_concurrency"] = max_concurrency
        self["max_parallelism"] = max_parallelism
        self["preferred_concurrency"] = preferred_concurrency
        self["preferred_parallelism"] = preferred_parallelism
        self["subscription_id"] = subscription_id
        self["gridftp_control_channel_port"] = gridftp_control_channel_port

        if not isinstance(additional_fields, MissingType):
            self.update(additional_fields)
        ensure_datatype(self)
