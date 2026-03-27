from __future__ import annotations

import logging
import typing as t
import uuid

from globus_sdk._missing import MISSING, MissingType
from globus_sdk._payload import GlobusPayload

log = logging.getLogger(__name__)


class TunnelCreateDocument(GlobusPayload):
    """
    Convenience class for constructing a tunnel document to use as the
    ``data`` parameter to
    :meth:`create_tunnel <globus_sdk.TransferClientV2.create_tunnel>`.
    """

    def __init__(
        self,
        initiator_stream_access_point: uuid.UUID | str,
        listener_stream_access_point: uuid.UUID | str,
        *,
        label: str | MissingType = MISSING,
        listener_port: int | MissingType = MISSING,
        listener_ip_address: str | MissingType = MISSING,
        submission_id: uuid.UUID | str | MissingType = MISSING,
        lifetime_mins: int | MissingType = MISSING,
        restartable: bool | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        log.debug("Creating a new TunnelCreateDocument object")

        # Auto-create submission_id if not given now so that the same
        # submission_id will be used across retries
        if submission_id is MISSING:
            submission_id = uuid.uuid1()

        relationships = {
            "listener": {
                "data": {
                    "type": "StreamAccessPoint",
                    "id": listener_stream_access_point,
                }
            },
            "initiator": {
                "data": {
                    "type": "StreamAccessPoint",
                    "id": initiator_stream_access_point,
                }
            },
        }
        attributes = {
            "label": label,
            "listener_port": listener_port,
            "listener_ip_address": listener_ip_address,
            "submission_id": submission_id,
            "restartable": restartable,
            "lifetime_mins": lifetime_mins,
        }
        if additional_fields is not None:
            attributes.update(additional_fields)

        self["data"] = {
            "type": "Tunnel",
            "relationships": relationships,
            "attributes": attributes,
        }


class TunnelUpdateDocument(GlobusPayload):
    """
    Convenience class for constructing a tunnel document to use as the
    ``data`` parameter to
    :meth:`update_tunnel <globus_sdk.TransferClientV2.update_tunnel>`.
    """

    def __init__(
        self,
        *,
        label: str | MissingType = MISSING,
        listener_port: int | MissingType = MISSING,
        listener_ip_address: str | MissingType = MISSING,
        state: t.Literal["STOPPING"] | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        log.debug("Creating a new TunnelUpdateDocument object")

        attributes = {
            "label": label,
            "listener_port": listener_port,
            "listener_ip_address": listener_ip_address,
            "state": state,
        }
        if additional_fields is not None:
            attributes.update(additional_fields)

        self["data"] = {
            "type": "Tunnel",
            "attributes": attributes,
        }
