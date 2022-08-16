import datetime
import logging
from typing import Any, Dict, Optional, Union

from globus_sdk.config import get_service_url
from globus_sdk.services.transfer import TransferData
from globus_sdk.utils import PayloadWrapper, slash_join

log = logging.getLogger(__name__)


class TimerJob(PayloadWrapper):
    r"""
    Class for specifying parameters used to create a job in the Timer service. Used as
    the ``data`` argument in
    :meth:`create_job <globus_sdk.TimerClient.create_job>`.

    Timer operates through the `Globus Automate API
    <https://docs.globus.org/globus-automation-services/>`_. Crucially, the
    ``callback_url`` parameter should always be the URL used to run an action provider.

    .. warning::

        Currently the only supported action provider for this is for Transfer. Thus,
        users should generally only use the :meth:`~from_transfer_data` method here. Any
        other usage is meant for internal purposes; proceed with caution!

    :param callback_url: URL for the action which the Timer job will use.
    :type callback_url: str
    :param callback_body: JSON data which Timer will send to the Action Provider on
        each invocation
    :type callback_body: dict
    :param start: The datetime at which to start the Timer job.
    :type start: datetime.datetime or str
    :param interval: The interval at which the Timer job should recur. Interpreted as
        seconds if specified as an integer. If ``stop_after_n == 1``, i.e. the job is
        set to run only a single time, then interval *must* be None.
    :type interval: datetime.timedelta or int
    :param name: A (not necessarily unique) name to identify this job in Timer
    :type name: str, optional
    :param stop_after: A date after which the Timer job will stop running
    :type stop_after: datetime.datetime, optional
    :param stop_after_n: A number of executions after which the Timer job will stop
    :type stop_after_n: int
    :param scope: Timer defaults to the Transfer 'all' scope. Use this parameter to
        change the scope used by Timer when calling the Transfer Action Provider.
    :type scope: str, optional

    .. automethodlist:: globus_sdk.TimerJob
    """

    def __init__(
        self,
        callback_url: str,
        callback_body: Dict[str, Any],
        start: Union[datetime.datetime, str],
        interval: Union[datetime.timedelta, int, None],
        *,
        name: Optional[str] = None,
        stop_after: Optional[datetime.datetime] = None,
        stop_after_n: Optional[int] = None,
        scope: Optional[str] = None,
    ) -> None:
        super().__init__()
        self["callback_url"] = callback_url
        self["callback_body"] = callback_body
        if isinstance(start, datetime.datetime):
            self["start"] = start.isoformat()
        else:
            self["start"] = start
        if isinstance(interval, datetime.timedelta):
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
        transfer_data: Union[TransferData, Dict[str, Any]],
        start: Union[datetime.datetime, str],
        interval: Union[datetime.timedelta, int, None],
        *,
        name: Optional[str] = None,
        stop_after: Optional[datetime.datetime] = None,
        stop_after_n: Optional[int] = None,
        scope: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> "TimerJob":
        r"""
        Specify data to create a Timer job using the parameters for a transfer. Timer
        will use those parameters to run the defined transfer operation, recurring at
        the given interval.

        :param transfer_data: A :class:`TransferData <globus_sdk.TransferData>` object.
            Construct this object exactly as you would normally; Timer will use this to
            run the recurring transfer.
        :type transfer_data: globus_sdk.TransferData
        :param start: The datetime at which to start the Timer job.
        :type start: datetime.datetime or str
        :param interval: The interval at which the Timer job should recur. Interpreted
            as seconds if specified as an integer. If ``stop_after_n == 1``, i.e. the
            job is set to run only a single time, then interval *must* be None.
        :type interval: datetime.timedelta or int
        :param name: A (not necessarily unique) name to identify this job in Timer
        :type name: str, optional
        :param stop_after: A date after which the Timer job will stop running
        :type stop_after: datetime.datetime, optional
        :param stop_after_n: A number of executions after which the Timer job will stop
        :type stop_after_n: int
        :param scope: Timer defaults to the Transfer 'all' scope. Use this parameter to
            change the scope used by Timer when calling the Transfer Action Provider.
        :type scope: str, optional
        :param environment: For internal use: because this method needs to generate a
            URL for the Transfer Action Provider, this argument can control which
            environment the Timer job is sent to.
        :type environment: str, optional
        """
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
