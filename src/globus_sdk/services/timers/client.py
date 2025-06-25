from __future__ import annotations

import logging
import typing as t
import uuid

from globus_sdk import _guards, client, exc, response
from globus_sdk._types import UUIDLike
from globus_sdk.scopes import (
    GCSCollectionScopes,
    Scope,
    TimersScopes,
    TransferScopes,
)

from .data import TimerJob, TransferTimer
from .errors import TimersAPIError

log = logging.getLogger(__name__)


class TimersClient(client.BaseClient):
    r"""
    Client for the Globus Timers API.

    .. sdk-sphinx-copy-params:: BaseClient

    .. automethodlist:: globus_sdk.TimersClient
    """

    error_class = TimersAPIError
    service_name = "timer"
    scopes = TimersScopes
    default_scope_requirements = [TimersScopes.timer]

    def add_app_transfer_data_access_scope(
        self, collection_ids: UUIDLike | t.Iterable[UUIDLike]
    ) -> TimersClient:
        """
        Add a dependent ``data_access`` scope for one or more given ``collection_ids``
        to this client's ``GlobusApp``, under the Transfer ``all`` scope.
        Useful for preventing ``ConsentRequired`` errors when creating timers
        that use Globus Connect Server mapped collection(s) as the source or
        destination.

        .. warning::

            This method must only be used on ``collection_ids`` for non-High-Assurance
            GCS Mapped Collections.

            Use on other collection types, e.g., on GCP Mapped Collections or any form
            of Guest Collection, will result in "Unknown Scope" errors during the login
            flow.

        Returns ``self`` for chaining.

        Raises ``GlobusSDKUsageError`` if this client was not initialized with an app.

        :param collection_ids: a collection ID or an iterable of IDs.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    app = UserApp("myapp", client_id=NATIVE_APP_CLIENT_ID)
                    client = TimersClient(app=app).add_app_transfer_data_access_scope(COLLECTION_ID)

                    transfer_data = TransferData(COLLECTION_ID, COLLECTION_ID)
                    transfer_data.add_item("/staging/", "/active/")

                    daily_timer = TransferTimer(
                        name="test_timer", schedule=RecurringTimerSchedule(24 * 60 * 60), body=transfer_data
                    )

                    client.create_timer(daily_timer)
        """  # noqa: E501
        if isinstance(collection_ids, (str, uuid.UUID)):
            _guards.validators.uuidlike("collection_ids", collection_ids)
            # wrap the collection_ids input in a list for consistent iteration below
            collection_ids_ = [collection_ids]
        else:
            # copy to a list so that ephemeral iterables can be iterated multiple times
            collection_ids_ = list(collection_ids)
            for i, c in enumerate(collection_ids_):
                _guards.validators.uuidlike(f"collection_ids[{i}]", c)

        dependencies: list[Scope] = []
        for coll_id in collection_ids_:
            data_access_scope = GCSCollectionScopes(
                str(coll_id)
            ).data_access.with_optional(True)
            dependencies.append(data_access_scope)
        transfer_scope = TransferScopes.all.with_dependencies(dependencies)

        timers_scope = TimersScopes.timer.with_dependency(transfer_scope)
        self.add_app_scope(timers_scope)
        return self

    def list_jobs(
        self, *, query_params: dict[str, t.Any] | None = None
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /jobs/``

        :param query_params: additional parameters to pass as query params

        **Examples**

        >>> timer_client = globus_sdk.TimersClient(...)
        >>> jobs = timer_client.list_jobs()
        """
        log.debug(f"TimersClient.list_jobs({query_params})")
        return self.get("/jobs/", query_params=query_params)

    def get_job(
        self,
        job_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /jobs/<job_id>``

        :param job_id: the ID of the timer ("job")
        :param query_params: additional parameters to pass as query params

        **Examples**

        >>> timer_client = globus_sdk.TimersClient(...)
        >>> job = timer_client.get_job(job_id)
        >>> assert job["job_id"] == job_id
        """
        log.debug(f"TimersClient.get_job({job_id})")
        return self.get(f"/jobs/{job_id}", query_params=query_params)

    def create_timer(
        self, timer: dict[str, t.Any] | TransferTimer
    ) -> response.GlobusHTTPResponse:
        """
        :param timer: a document defining the new timer

        A ``TransferTimer`` object can be constructed from a ``TransferData`` object,
        which is the recommended way to create a timer for data transfers.

        **Examples**

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> transfer_data = TransferData(...)
                    >>> timers_client = globus_sdk.TimersClient(...)
                    >>> create_doc = globus_sdk.TransferTimer(
                    ...     name="my-timer",
                    ...     schedule={"type": "recurring", "interval": 1800},
                    ...     body=transfer_data,
                    ... )
                    >>> response = timers_client.create_timer(timer=create_doc)

            .. tab-item:: Example Response Data

                .. expandtestfixture:: timer.create_timer

            .. tab-item:: API Info

                ``POST /v2/timer``
        """
        if isinstance(timer, TimerJob):
            raise exc.GlobusSDKUsageError(
                "Cannot pass a TimerJob to create_timer(). "
                "Create a TransferTimer instead."
            )
        log.debug("TimersClient.create_timer(...)")
        return self.post("/v2/timer", data={"timer": timer})

    def create_job(
        self, data: dict[str, t.Any] | TimerJob
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /jobs/``

        :param data: a timer document used to create the new timer ("job")

        **Examples**

        >>> from datetime import datetime, timedelta
        >>> transfer_data = TransferData(...)
        >>> timers_client = globus_sdk.TimersClient(...)
        >>> job = TimerJob.from_transfer_data(
        ...     transfer_data,
        ...     datetime.utcnow(),
        ...     timedelta(days=14),
        ...     name="my-timer-job"
        ... )
        >>> timer_result = timers_client.create_job(job)
        """
        if isinstance(data, TransferTimer):
            raise exc.GlobusSDKUsageError(
                "Cannot pass a TransferTimer to create_job(). Use create_timer() "
                "instead."
            )
        log.debug(f"TimersClient.create_job({data})")
        return self.post("/jobs/", data=data)

    def update_job(
        self, job_id: UUIDLike, data: dict[str, t.Any]
    ) -> response.GlobusHTTPResponse:
        """
        ``PATCH /jobs/<job_id>``

        :param job_id: the ID of the timer ("job")
        :param data: a partial timer document used to update the job

        **Examples**

        >>> timer_client = globus_sdk.TimersClient(...)
        >>> timer_client.update_job(job_id, {"name": "new name}"})
        """
        log.debug(f"TimersClient.update_job({job_id}, {data})")
        return self.patch(f"/jobs/{job_id}", data=data)

    def delete_job(
        self,
        job_id: UUIDLike,
    ) -> response.GlobusHTTPResponse:
        """
        ``DELETE /jobs/<job_id>``

        :param job_id: the ID of the timer ("job")

        **Examples**

        >>> timer_client = globus_sdk.TimersClient(...)
        >>> timer_client.delete_job(job_id)
        """
        log.debug(f"TimersClient.delete_job({job_id})")
        return self.delete(f"/jobs/{job_id}")

    def pause_job(
        self,
        job_id: UUIDLike,
    ) -> response.GlobusHTTPResponse:
        """
        Make a timer job inactive, preventing it from running until it is resumed.

        :param job_id: The ID of the timer to pause

        **Examples**

        >>> timer_client = globus_sdk.TimersClient(...)
        >>> timer_client.pause_job(job_id)
        """
        log.debug(f"TimersClient.pause_job({job_id})")
        return self.post(f"/jobs/{job_id}/pause")

    def resume_job(
        self,
        job_id: UUIDLike,
        *,
        update_credentials: bool | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Resume an inactive timer job, optionally replacing credentials to resolve
        issues with insufficient authorization.

        :param job_id: The ID of the timer to resume
        :param update_credentials: When true, replace the credentials for the timer
            using the credentials for this resume call. This can be used to resolve
            authorization errors (such as session and consent errors), but it also
            could introduce session and consent errors, if the credentials being used
            to resume lack some necessary properties of the credentials they're
            replacing. If not supplied, the Timers service will determine whether to
            replace credentials according to the reason why the timer job
            became inactive.

        **Examples**

        >>> timer_client = globus_sdk.TimersClient(...)
        >>> timer_client.resume_job(job_id)
        """
        log.debug(f"TimersClient.resume_job({job_id})")
        data = {}
        if update_credentials is not None:
            data["update_credentials"] = update_credentials
        return self.post(f"/jobs/{job_id}/resume", data=data)
