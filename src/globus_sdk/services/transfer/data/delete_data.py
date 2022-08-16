import datetime
import logging
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional, Union

from globus_sdk import exc, utils
from globus_sdk._types import UUIDLike

if TYPE_CHECKING:
    import globus_sdk

log = logging.getLogger(__name__)


class DeleteData(utils.PayloadWrapper):
    r"""
    Convenience class for constructing a delete document, to use as the
    `data` parameter to
    :meth:`submit_delete <globus_sdk.TransferClient.submit_delete>`.

    At least one item must be added using
    :meth:`add_item <globus_sdk.DeleteData.add_item>`.

    If ``submission_id`` isn't passed, one will be fetched automatically. The
    submission ID can be pulled out of here to inspect, but the document
    can be used as-is multiple times over to retry a potential submission
    failure (so there shouldn't be any need to inspect it).

    :param transfer_client: A ``TransferClient`` instance which will be used to get a
        submission ID if one is not supplied. Should be the same instance that is used
        to submit the deletion.
    :type transfer_client: :class:`TransferClient <globus_sdk.TransferClient>` or None
    :param endpoint: The endpoint ID which is targeted by this deletion Task
    :type endpoint: str or UUID
    :param label: A string label for the Task
    :type label: str, optional
    :param submission_id: A submission ID value fetched via
        :meth:`get_submission_id <globus_sdk.TransferClient.get_submission_id>`.
        Defaults to using ``transfer_client.get_submission_id`` if a ``transfer_client``
        is provided
    :type submission_id: str or UUID, optional
    :param recursive: Recursively delete subdirectories on the target endpoint
      [default: ``False``]
    :type recursive: bool
    :param deadline: An ISO-8601 timestamp (as a string) or a datetime object which
        defines a deadline for the deletion. At the deadline, even if the data deletion
        is not complete, the job will be canceled. We recommend ensuring that the
        timestamp is in UTC to avoid confusion and ambiguity. Examples of ISO-8601
        timestamps include ``2017-10-12 09:30Z``, ``2017-10-12 12:33:54+00:00``, and
        ``2017-10-12``
    :type deadline: str or datetime, optional
    :param skip_activation_check: When true, allow submission even if the endpoint
        isn't currently activated
    :type skip_activation_check: bool, optional
    :param notify_on_succeeded: Send a notification email when the delete task
        completes with a status of SUCCEEDED.
        [default: ``True``]
    :type notify_on_succeeded: bool, optional
    :param notify_on_failed: Send a notification email when the delete task completes
        with a status of FAILED.
        [default: ``True``]
    :type notify_on_failed: bool, optional
    :param notify_on_inactive: Send a notification email when the delete task changes
        status to INACTIVE. e.g. From credentials expiring.
        [default: ``True``]
    :type notify_on_inactive: bool, optional
    :param additional_fields: additional fields to be added to the delete
        document. Mostly intended for internal use
    :type additional_fields: dict, optional

    **Examples**

    See the :meth:`submit_delete <globus_sdk.TransferClient.submit_delete>`
    documentation for example usage.

    **External Documentation**

    See the
    `Task document definition \
    <https://docs.globus.org/api/transfer/task_submit/#document_types>`_
    and
    `Delete specific fields \
    <https://docs.globus.org/api/transfer/task_submit/#delete_specific_fields>`_
    in the REST documentation for more details on Delete Task documents.

    .. automethodlist:: globus_sdk.TransferData
    """

    def __init__(
        self,
        transfer_client: Optional["globus_sdk.TransferClient"] = None,
        endpoint: Optional[UUIDLike] = None,
        *,
        label: Optional[str] = None,
        submission_id: Optional[UUIDLike] = None,
        recursive: bool = False,
        deadline: Optional[Union[str, datetime.datetime]] = None,
        skip_activation_check: Optional[bool] = None,
        notify_on_succeeded: bool = True,
        notify_on_failed: bool = True,
        notify_on_inactive: bool = True,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        # this must be checked explicitly to handle the fact that `transfer_client` is
        # the first arg
        if endpoint is None:
            raise exc.GlobusSDKUsageError("endpoint is required")

        self["DATA_TYPE"] = "delete"
        self["DATA"] = []
        self._set_optstrs(
            endpoint=endpoint,
            label=label,
            submission_id=submission_id
            or (
                transfer_client.get_submission_id()["value"]
                if transfer_client
                else None
            ),
            deadline=deadline,
        )
        self._set_optbools(
            recursive=recursive,
            skip_activation_check=skip_activation_check,
            notify_on_succeeded=notify_on_succeeded,
            notify_on_failed=notify_on_failed,
            notify_on_inactive=notify_on_inactive,
        )

        for k, v in self.items():
            log.info("DeleteData.%s = %s", k, v)

        if additional_fields is not None:
            self.update(additional_fields)
            for option, value in additional_fields.items():
                log.info(
                    f"DeleteData.{option} = {value} (option passed "
                    "in via additional_fields)"
                )

    def add_item(
        self, path: str, *, additional_fields: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a file or directory or symlink to be deleted. If any of the paths
        are directories, ``recursive`` must be set True on the top level
        ``DeleteData``. Symlinks will never be followed, only deleted.

        Appends a delete_item document to the DATA key of the delete
        document.
        """
        item_data = {"DATA_TYPE": "delete_item", "path": path}
        if additional_fields is not None:
            item_data.update(additional_fields)
        log.debug('DeleteData[{}].add_item: "{}"'.format(self["endpoint"], path))
        self["DATA"].append(item_data)

    def iter_items(self) -> Iterator[Dict[str, Any]]:
        """
        An iterator of items created by ``add_item``.

        Each item takes the form of a dictionary.
        """
        yield from iter(self["DATA"])
