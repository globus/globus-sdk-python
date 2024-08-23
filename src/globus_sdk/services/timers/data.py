from __future__ import annotations

# the name "datetime" is used in this module, so use an alternative name
# in order to avoid name shadowing
import datetime as dt
import logging
import typing as t

from globus_sdk.config import get_service_url
from globus_sdk.exc import warn_deprecated
from globus_sdk.services.transfer import TransferData
from globus_sdk.utils import MISSING, MissingType, PayloadWrapper, slash_join

log = logging.getLogger(__name__)


class TransferTimer(PayloadWrapper):
    """
    A helper for defining a payload for Transfer Timer creation.
    Use this along with :meth:`create_timer <globus_sdk.TimersClient.create_timer>` to
    create a timer.

    .. note::
        ``TimersClient`` has two methods for creating timers, ``create_timer`` and
        ``create_job``.
        ``create_job`` uses a different API -- only ``create_timer`` will work with
        this helper class.

        Users are strongly recommended to use ``create_timer`` and this helper for
        timer creation.

    :param name: A name to identify this timer
    :param schedule: The schedule on which the timer runs
    :param body: A transfer payload for the timer to use. If it includes
        ``submission_id`` or ``skip_activation_check``, these parameters will be
        removed, as they are not supported in timers.

    The ``schedule`` field determines when the timer will run.
    Timers may be "run once" or "recurring", and "recurring" timers may specify an end
    date or a number of executions after which the timer will stop. A ``schedule`` is
    specified as a dict, but the SDK provides two useful helpers for constructing these
    data.

    **Example Schedules**

    .. tab-set::

        .. tab-item:: Run Once, Right Now

            .. code-block:: python

                schedule = OnceTimerSchedule()

        .. tab-item:: Run Once, At a Specific Time

            .. code-block:: python

                schedule = OnceTimerSchedule(datetime="2023-09-22T00:00:00Z")

        .. tab-item:: Run Every 5 Minutes, Until a Specific Time

            .. code-block:: python

                schedule = RecurringTimerSchedule(
                    interval_seconds=300,
                    end={"condition": "time", "datetime": "2023-10-01T00:00:00Z"},
                )

        .. tab-item:: Run Every 30 Minutes, 10 Times

            .. code-block:: python

                schedule = RecurringTimerSchedule(
                    interval_seconds=1800,
                    end={"condition": "iterations", "iterations": 10},
                )

        .. tab-item:: Run Every 10 Minutes, Indefinitely

            .. code-block:: python

                schedule = RecurringTimerSchedule(interval_seconds=600)

    Using these schedules, you can create a timer from a ``TransferData`` object:

    .. code-block:: pycon

        >>> from globus_sdk import TransferData, TransferTimer
        >>> schedule = ...
        >>> transfer_data = TransferData(...)
        >>> timer = TransferTimer(
        ...     name="my timer",
        ...     schedule=schedule,
        ...     body=transfer_data,
        ... )

    Submit the timer to the Timers service with
    :meth:`create_timer <globus_sdk.TimersClient.create_timer>`.
    """

    def __init__(
        self,
        *,
        name: str | MissingType = MISSING,
        schedule: dict[str, t.Any] | RecurringTimerSchedule | OnceTimerSchedule,
        body: dict[str, t.Any] | TransferData,
    ) -> None:
        super().__init__()
        self["timer_type"] = "transfer"
        self["name"] = name
        self["schedule"] = schedule
        self["body"] = self._preprocess_body(body)

    def _preprocess_body(
        self, body: dict[str, t.Any] | TransferData
    ) -> dict[str, t.Any]:
        # shallow-copy for dicts, convert any TransferData to a dict
        new_body = dict(body)
        # remove the skip_activation_check and submission_id parameters unconditionally
        # (not supported in timers, but often present in TransferData)
        new_body.pop("submission_id", None)
        new_body.pop("skip_activation_check", None)
        return new_body


class RecurringTimerSchedule(PayloadWrapper):
    """
    A helper used as part of a *timer* to define when the *timer* will run.

    A ``RecurringTimerSchedule`` is used to describe a *timer* which runs repeatedly
    until some end condition is reached.

    :param interval_seconds: The number of seconds between each run of the timer.
    :param start: The time at which to start the timer, either as an ISO 8601 string
        with timezone information, or as a ``datetime.datetime`` object.
    :param end: The end condition for the timer, as a dict. This either expresses a
        number of iterations for the timer or an end date.

    Example ``end`` conditions:

    .. code-block:: python

        # run 10 times
        end = {"condition": "iterations", "iterations": 10}

        # run until a specific date
        end = {"condition": "time", "datetime": "2023-10-01T00:00:00Z"}

    If the end condition is ``time``, then the ``datetime`` value can be expressed as a
    python ``datetime`` type as well, e.g.

    .. code-block:: python

        # end in 10 days
        end = {
            "condition": "time",
            "datetime": datetime.datetime.now() + datetime.timedelta(days=10),
        }
    """

    def __init__(
        self,
        interval_seconds: int,
        start: str | dt.datetime | MissingType = MISSING,
        end: dict[str, t.Any] | MissingType = MISSING,
    ) -> None:
        super().__init__()
        self["type"] = "recurring"
        self["interval_seconds"] = interval_seconds
        self["start"] = _format_date(start)
        self["end"] = end

        # if a datetime is given for part of the end condition, format it (and
        # shallow-copy the end condition)
        # primarily, this handles
        #    end={"condition": "time", "datetime": <some-datetime>}
        if isinstance(end, dict):
            self["end"] = {
                k: (_format_date(v) if isinstance(v, dt.datetime) else v)
                for k, v in end.items()
            }


class OnceTimerSchedule(PayloadWrapper):
    """
    A helper used as part of a *timer* to define when the *timer* will run.

    A ``OnceTimerSchedule`` is used to describe a *timer* which runs exactly once.
    It may be scheduled for a time in the future.

    :param datetime: The time at which to run the timer, either as an ISO 8601
        string with timezone information, or as a ``datetime.datetime`` object.
    """

    def __init__(
        self,
        datetime: str | dt.datetime | MissingType = MISSING,
    ) -> None:
        super().__init__()
        self["type"] = "once"
        self["datetime"] = _format_date(datetime)


class TimerJob(PayloadWrapper):
    r"""
    .. warning::

        This method of specifying and creating Timers for data transfer is now
        deprecated. Users should use ``TimerData`` instead.

        ``TimerJob`` is still supported for non-transfer use-cases.

    Helper for creating a timer in the Timers service. Used as the ``data``
    argument in :meth:`create_job <globus_sdk.TimersClient.create_job>`.

    The ``callback_url`` parameter should always be the URL used to run an
    action provider.

    :param callback_url: URL for the action which the Timers job will use.
    :param callback_body: JSON data which Timers will send to the Action Provider on
        each invocation
    :param start: The datetime at which to start the Timers job.
    :param interval: The interval at which the Timers job should recur. Interpreted as
        seconds if specified as an integer. If ``stop_after_n == 1``, i.e. the job is
        set to run only a single time, then interval *must* be None.
    :param name: A (not necessarily unique) name to identify this job in Timers
    :param stop_after: A date after which the Timers job will stop running
    :param stop_after_n: A number of executions after which the Timers job will stop
    :param scope: Timers defaults to the Transfer 'all' scope. Use this parameter to
        change the scope used by Timers when calling the Transfer Action Provider.

    .. automethodlist:: globus_sdk.TimerJob
    """

    def __init__(
        self,
        callback_url: str,
        callback_body: dict[str, t.Any],
        start: dt.datetime | str,
        interval: dt.timedelta | int | None,
        *,
        name: str | None = None,
        stop_after: dt.datetime | None = None,
        stop_after_n: int | None = None,
        scope: str | None = None,
    ) -> None:
        super().__init__()
        self["callback_url"] = callback_url
        self["callback_body"] = callback_body
        if isinstance(start, dt.datetime):
            self["start"] = start.isoformat()
        else:
            self["start"] = start
        if isinstance(interval, dt.timedelta):
            self["interval"] = int(interval.total_seconds())
        else:
            self["interval"] = interval
        if name is not None:
            self["name"] = name
        if stop_after is not None:
            self["stop_after"] = stop_after.isoformat()
        if stop_after_n is not None:
            self["stop_after_n"] = stop_after_n
        if scope is not None:
            self["scope"] = scope

    @classmethod
    def from_transfer_data(
        cls,
        transfer_data: TransferData | dict[str, t.Any],
        start: dt.datetime | str,
        interval: dt.timedelta | int | None,
        *,
        name: str | None = None,
        stop_after: dt.datetime | None = None,
        stop_after_n: int | None = None,
        scope: str | None = None,
        environment: str | None = None,
    ) -> TimerJob:
        r"""
        Specify data to create a Timers job using the parameters for a transfer. Timers
        will use those parameters to run the defined transfer operation, recurring at
        the given interval.

        :param transfer_data: A :class:`TransferData <globus_sdk.TransferData>` object.
            Construct this object exactly as you would normally; Timers will use this to
            run the recurring transfer.
        :param start: The datetime at which to start the Timers job.
        :param interval: The interval at which the Timers job should recur. Interpreted
            as seconds if specified as an integer. If ``stop_after_n == 1``, i.e. the
            job is set to run only a single time, then interval *must* be None.
        :param name: A (not necessarily unique) name to identify this job in Timers
        :param stop_after: A date after which the Timers job will stop running
        :param stop_after_n: A number of executions after which the Timers job will stop
        :param scope: Timers defaults to the Transfer 'all' scope. Use this parameter to
            change the scope used by Timers when calling the Transfer Action Provider.
        :param environment: For internal use: because this method needs to generate a
            URL for the Transfer Action Provider, this argument can control which
            environment the Timers job is sent to.
        """
        warn_deprecated(
            "TimerJob.from_transfer_data(X, ...) is deprecated. "
            "Prefer TransferTimer(body=X, ...) instead."
        )

        transfer_action_url = slash_join(
            get_service_url("actions", environment=environment), "transfer/transfer/run"
        )
        log.info(
            "Creating TimerJob from TransferData, action_url=%s", transfer_action_url
        )
        for key in ("submission_id", "skip_activation_check"):
            if key in transfer_data:
                raise ValueError(
                    f"cannot create TimerJob from TransferData which has {key} set"
                )
        # dict will either convert a `TransferData` object or leave us with a dict here
        callback_body = {"body": dict(transfer_data)}
        return cls(
            transfer_action_url,
            callback_body,
            start,
            interval,
            name=name,
            stop_after=stop_after,
            stop_after_n=stop_after_n,
            scope=scope,
        )


def _format_date(date: str | dt.datetime | MissingType) -> str | MissingType:
    if isinstance(date, dt.datetime):
        if date.tzinfo is None:
            date = date.astimezone(dt.timezone.utc)
        return date.isoformat(timespec="seconds")
    else:
        return date
