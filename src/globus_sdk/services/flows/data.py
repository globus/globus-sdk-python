from __future__ import annotations

import logging
import typing as t

from globus_sdk._missing import MISSING, MissingType
from globus_sdk._payload import Payload

log = logging.getLogger(__name__)


class RunActivityNotificationPolicy(Payload):
    """
    A notification policy for a run, determining when emails will be sent.

    :param status: A list of statuses which will trigger notifications. When
        the run's status changes, it is evaluated against this list. If the new
        status matches the policy, an email is sent.
    """

    def __init__(
        self,
        status: (
            list[t.Literal["INACTIVE", "SUCCEEDED", "FAILED"]] | MissingType
        ) = MISSING,
    ) -> None:
        super().__init__()
        self["status"] = status
