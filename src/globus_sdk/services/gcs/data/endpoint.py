from __future__ import annotations

import typing as t

from globus_sdk import utils
from globus_sdk.services.gcs.data._common import DatatypeCallback, ensure_datatype


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
        data_type: str | None = None,
        # strs
        contact_email: str | None = None,
        contact_info: str | None = None,
        department: str | None = None,
        description: str | None = None,
        display_name: str | None = None,
        info_link: str | None = None,
        network_use: (
            t.Literal["normal", "minimal", "aggressive", "custom"] | None
        ) = None,
        organization: str | None = None,
        subscription_id: str | None = None,
        # str lists
        keywords: t.Iterable[str] | None = None,
        # bools
        allow_udt: bool | None = None,
        public: bool | None = None,
        # ints
        gridftp_control_channel_port: int | None = None,
        max_concurrency: int | None = None,
        max_parallelism: int | None = None,
        preferred_concurrency: int | None = None,
        preferred_parallelism: int | None = None,
        # additional fields
        additional_fields: dict[str, t.Any] | None = None,
    ):
        super().__init__()
        self._set_optstrs(
            DATA_TYPE=data_type,
            contact_email=contact_email,
            contact_info=contact_info,
            department=department,
            description=description,
            display_name=display_name,
            info_link=info_link,
            network_use=network_use,
            organization=organization,
            subscription_id=subscription_id,
        )
        self._set_optstrs(
            keywords=keywords,
        )
        self._set_optbools(
            allow_udt=allow_udt,
            public=public,
        )
        self._set_optints(
            gridftp_control_channel_port=gridftp_control_channel_port,
            max_concurrency=max_concurrency,
            max_parallelism=max_parallelism,
            preferred_concurrency=preferred_concurrency,
            preferred_parallelism=preferred_parallelism,
        )

        if additional_fields is not None:
            self.update(additional_fields)
        ensure_datatype(self)
