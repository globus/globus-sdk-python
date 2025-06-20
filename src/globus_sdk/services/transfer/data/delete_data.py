from __future__ import annotations

import datetime
import logging
import typing as t

from globus_sdk._missing import MISSING, MissingType
from globus_sdk._payload import GlobusPayload
from globus_sdk._remarshal import stringify
from globus_sdk._types import UUIDLike

log = logging.getLogger(__name__)


class DeleteData(GlobusPayload):
    r"""
    Convenience class for constructing a delete document, to use as the
    `data` parameter to
    :meth:`submit_delete <globus_sdk.TransferClient.submit_delete>`.

    At least one item must be added using
    :meth:`add_item <globus_sdk.DeleteData.add_item>`.

    :param endpoint: The endpoint ID which is targeted by this deletion Task
    :param label: A string label for the Task
    :param submission_id: A submission ID value fetched via :meth:`get_submission_id \
        <globus_sdk.TransferClient.get_submission_id>`. By default, the SDK
        will fetch and populate this field when :meth:`submit_delete \
        <globus_sdk.TransferClient.submit_delete>` is called.
    :param recursive: Recursively delete subdirectories on the target endpoint
      [default: ``False``]
    :param ignore_missing: Ignore nonexistent files and directories instead of treating
        them as errors. [default: ``False``]
    :param interpret_globs: Enable expansion of ``\*?[]`` characters in the last
        component of paths, unless they are escaped with a preceding backslash, ``\\``
        [default: ``False``]
    :param deadline: An ISO-8601 timestamp (as a string) or a datetime object which
        defines a deadline for the deletion. At the deadline, even if the data deletion
        is not complete, the job will be canceled. We recommend ensuring that the
        timestamp is in UTC to avoid confusion and ambiguity. Examples of ISO-8601
        timestamps include ``2017-10-12 09:30Z``, ``2017-10-12 12:33:54+00:00``, and
        ``2017-10-12``
    :param skip_activation_check: When true, allow submission even if the endpoint
        isn't currently activated
    :param notify_on_succeeded: Send a notification email when the delete task
        completes with a status of SUCCEEDED.
        [default: ``True``]
    :param notify_on_failed: Send a notification email when the delete task completes
        with a status of FAILED.
        [default: ``True``]
    :param notify_on_inactive: Send a notification email when the delete task changes
        status to INACTIVE. e.g. From credentials expiring.
        [default: ``True``]
    :param local_user: Optional value passed to identity mapping specifying which local
        user account to map to. Only usable with Globus Connect Server v5 mapped
        collections.
    :param additional_fields: additional fields to be added to the delete
        document. Mostly intended for internal use

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
        endpoint: UUIDLike,
        *,
        label: str | MissingType = MISSING,
        submission_id: UUIDLike | MissingType = MISSING,
        recursive: bool | MissingType = MISSING,
        ignore_missing: bool | MissingType = MISSING,
        interpret_globs: bool | MissingType = MISSING,
        deadline: str | datetime.datetime | MissingType = MISSING,
        skip_activation_check: bool | MissingType = MISSING,
        notify_on_succeeded: bool | MissingType = MISSING,
        notify_on_failed: bool | MissingType = MISSING,
        notify_on_inactive: bool | MissingType = MISSING,
        local_user: str | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self["DATA_TYPE"] = "delete"
        self["DATA"] = []
        self["endpoint"] = endpoint
        self["label"] = label
        self["submission_id"] = submission_id
        self["deadline"] = stringify(deadline)
        self["local_user"] = local_user
        self["recursive"] = recursive
        self["ignore_missing"] = ignore_missing
        self["interpret_globs"] = interpret_globs
        self["skip_activation_check"] = skip_activation_check
        self["notify_on_succeeded"] = notify_on_succeeded
        self["notify_on_failed"] = notify_on_failed
        self["notify_on_inactive"] = notify_on_inactive

        for k, v in self.items():
            log.debug("DeleteData.%s = %s", k, v)

        if additional_fields is not None:
            self.update(additional_fields)
            for option, value in additional_fields.items():
                log.debug(
                    f"DeleteData.{option} = {value} (option passed "
                    "in via additional_fields)"
                )

    def add_item(
        self,
        path: str,
        *,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        """
        Add a file or directory or symlink to be deleted. If any of the paths
        are directories, ``recursive`` must be set True on the top level
        ``DeleteData``. Symlinks will never be followed, only deleted.

        Appends a delete_item document to the DATA key of the delete
        document.

        :param path: Path to the directory or file to be deleted
        :param additional_fields: additional fields to be added to the delete item
        """
        item_data = {
            "DATA_TYPE": "delete_item",
            "path": path,
            **(additional_fields or {}),
        }
        log.debug('DeleteData[{}].add_item: "{}"'.format(self["endpoint"], path))
        self["DATA"].append(item_data)

    def iter_items(self) -> t.Iterator[dict[str, t.Any]]:
        """
        An iterator of items created by ``add_item``.

        Each item takes the form of a dictionary.
        """
        yield from iter(self["DATA"])
