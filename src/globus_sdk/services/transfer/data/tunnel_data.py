from __future__ import annotations

import logging
import typing as t
import uuid

from globus_sdk._missing import MISSING, MissingType
from globus_sdk._payload import GlobusPayload

log = logging.getLogger(__name__)


class CreateTunnelData(GlobusPayload):
    def __init__(
        self,
        initiator_stream_access_point: uuid.UUID | str,
        listener_stream_access_point: uuid.UUID | str,
        *,
        label: str | MissingType = MISSING,
        submission_id: uuid.UUID | str | MissingType = MISSING,
        lifetime_mins: int | MissingType = MISSING,
        restartable: bool | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        log.debug("Creating a new TunnelData object")

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
