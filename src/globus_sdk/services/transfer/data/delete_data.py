import logging
from typing import Any, Dict, Optional

from globus_sdk import utils

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
    :type transfer_client: :class:`TransferClient <globus_sdk.TransferClient>`
    :param endpoint: The endpoint ID which is targeted by this deletion Task
    :type endpoint: str
    :param label: A string label for the Task
    :type label: str, optional
    :param submission_id: A submission ID value fetched via
        :meth:`get_submission_id <globus_sdk.TransferClient.get_submission_id>`.
        Defaults to using ``transfer_client.get_submission_id``
    :type submission_id: str, optional
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
        transfer_client,
        endpoint,
        label=None,
        submission_id=None,
        recursive=False,
        deadline=None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ):
        super().__init__()
        endpoint = utils.safe_stringify(endpoint)
        log.info("Creating a new DeleteData object")
        self["DATA_TYPE"] = "delete"
        self["submission_id"] = (
            submission_id or transfer_client.get_submission_id()["value"]
        )
        log.info("DeleteData.submission_id = {}".format(self["submission_id"]))
        self["endpoint"] = endpoint
        log.info(f"DeleteData.endpoint = {endpoint}")
        self["recursive"] = recursive
        log.info(f"DeleteData.recursive = {recursive}")

        if label is not None:
            self["label"] = label
            log.debug(f"DeleteData.label = {label}")

        if deadline is not None:
            self["deadline"] = str(deadline)
            log.debug(f"DeleteData.deadline = {deadline}")

        self["DATA"] = []

        if additional_fields is not None:
            self.update(additional_fields)
            for option, value in additional_fields.items():
                log.info(f"DeleteData.{option} = {value} (option passed in via kwargs)")

    def add_item(self, path, additional_fields: Optional[Dict[str, Any]] = None):
        """
        Add a file or directory or symlink to be deleted. If any of the paths
        are directories, ``recursive`` must be set True on the top level
        ``DeleteData``. Symlinks will never be followed, only deleted.

        Appends a delete_item document to the DATA key of the delete
        document.
        """
        path = utils.safe_stringify(path)
        item_data = {"DATA_TYPE": "delete_item", "path": path}
        if additional_fields is not None:
            item_data.update(additional_fields)
        log.debug('DeleteData[{}].add_item: "{}"'.format(self["endpoint"], path))
        self["DATA"].append(item_data)
