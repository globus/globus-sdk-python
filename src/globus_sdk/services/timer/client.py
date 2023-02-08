from __future__ import annotations

import logging
import typing as t

from globus_sdk import client, response
from globus_sdk._types import UUIDLike
from globus_sdk.scopes import TimerScopes

from .data import TimerJob
from .errors import TimerAPIError

log = logging.getLogger(__name__)


class TimerClient(client.BaseClient):
    r"""
    Client for the Globus Timer API.

    :param authorizer: An authorizer instance used for all calls to Timer
    :type authorizer: :class:`GlobusAuthorizer\
                      <globus_sdk.authorizers.base.GlobusAuthorizer>`
    :param app_name: Optional "nice name" for the application. Has no bearing on the
        semantics of client actions. It is just passed as part of the User-Agent
        string, and may be useful when debugging issues with the Globus team
    :type app_name: str
    :param transport_params: Options to pass to the transport for this client
    :type transport_params: dict

    .. automethodlist:: globus_sdk.TimerClient
    """
    error_class = TimerAPIError
    service_name = "timer"
    scopes = TimerScopes

    def list_jobs(
        self, *, query_params: dict[str, t.Any] | None = None
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /jobs/``

        **Examples**

        >>> timer_client = globus_sdk.TimerClient(...)
        >>> jobs = timer_client.list_jobs()
        """
        log.info(f"TimerClient.list_jobs({query_params})")
        return self.get("/jobs/", query_params=query_params)

    def get_job(
        self,
        job_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /jobs/<job_id>``

        **Examples**

        >>> timer_client = globus_sdk.TimerClient(...)
        >>> job = timer_client.get_job(job_id)
        >>> assert job["job_id"] == job_id
        """
        log.info(f"TimerClient.get_job({job_id})")
        return self.get(f"/jobs/{job_id}", query_params=query_params)

    def create_job(
        self, data: TimerJob | dict[str, t.Any]
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /jobs/``

        **Examples**

        >>> from datetime import datetime, timedelta
        >>> transfer_client = TransferClient(...)
        >>> transfer_data = TransferData(transfer_client, ...)
        >>> timer_client = globus_sdk.TimerClient(...)
        >>> job = TimerJob.from_transfer_data(
        ...     transfer_data,
        ...     datetime.utcnow(),
        ...     timedelta(days=14),
        ...     name="my-timer-job"
        ... )
        >>> timer_result = timer_client.create_job(job)
        """
        log.info(f"TimerClient.create_job({data})")
        return self.post("/jobs/", data=data)

    def update_job(
        self, job_id: UUIDLike, data: dict[str, t.Any]
    ) -> response.GlobusHTTPResponse:
        """
        ``PATCH /jobs/<job_id>``

        **Examples**

        >>> timer_client = globus_sdk.TimerClient(...)
        >>> timer_client.update_job(job_id, {"name": "new name}"})
        """
        log.info(f"TimerClient.update_job({job_id}, {data})")
        return self.patch(f"/jobs/{job_id}", data=data)

    def delete_job(
        self,
        job_id: UUIDLike,
    ) -> response.GlobusHTTPResponse:
        """
        ``DELETE /jobs/<job_id>``

        **Examples**

        >>> timer_client = globus_sdk.TimerClient(...)
        >>> timer_client.delete_job(job_id)
        """
        log.info(f"TimerClient.delete_job({job_id})")
        return self.delete(f"/jobs/{job_id}")
