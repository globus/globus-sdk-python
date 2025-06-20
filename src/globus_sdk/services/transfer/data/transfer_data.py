from __future__ import annotations

import datetime
import logging
import typing as t

from globus_sdk._missing import MISSING, MissingType
from globus_sdk._payload import GlobusPayload
from globus_sdk._types import UUIDLike

log = logging.getLogger(__name__)
_sync_level_dict: dict[t.Literal["exists", "size", "mtime", "checksum"], int] = {
    "exists": 0,
    "size": 1,
    "mtime": 2,
    "checksum": 3,
}


def _parse_sync_level(
    sync_level: t.Literal["exists", "size", "mtime", "checksum"] | int | MissingType,
) -> int | MissingType:
    """
    Map sync_level strings to known int values

    Important: if more levels are added in the future you can always pass as an int
    """
    if isinstance(sync_level, str):
        try:
            sync_level = _sync_level_dict[sync_level]
        except KeyError as err:
            raise ValueError(f"Unrecognized sync_level {sync_level}") from err
    return sync_level


class TransferData(GlobusPayload):
    r"""
    Convenience class for constructing a transfer document, to use as the
    ``data`` parameter to
    :meth:`submit_transfer <globus_sdk.TransferClient.submit_transfer>`.

    At least one item must be added using
    :meth:`add_item <globus_sdk.TransferData.add_item>`.

    :param source_endpoint: The endpoint ID of the source endpoint
    :param destination_endpoint: The endpoint ID of the destination endpoint
    :param label: A string label for the Task
    :param submission_id: A submission ID value fetched via :meth:`get_submission_id \
        <globus_sdk.TransferClient.get_submission_id>`. By default, the SDK
        will fetch and populate this field when :meth:`submit_transfer \
        <globus_sdk.TransferClient.submit_transfer>` is called.
    :param sync_level: The method used to compare items between the source and
        destination. One of  ``"exists"``, ``"size"``, ``"mtime"``, or ``"checksum"``
        See the section below on sync-level for an explanation of values.
    :param verify_checksum: When true, after transfer verify that the source and
        destination file checksums match. If they don't, re-transfer the entire file and
        keep trying until it succeeds. This will create CPU load on both the origin and
        destination of the transfer, and may even be a bottleneck if the network speed
        is high enough.
        [default: ``False``]
    :param preserve_timestamp: When true, Globus Transfer will attempt to set file
        timestamps on the destination to match those on the origin. [default: ``False``]
    :param encrypt_data: When true, all files will be TLS-protected during transfer.
        [default: ``False``]
    :param deadline: An ISO-8601 timestamp (as a string) or a datetime object which
        defines a deadline for the transfer. At the deadline, even if the data transfer
        is not complete, the job will be canceled. We recommend ensuring that the
        timestamp is in UTC to avoid confusion and ambiguity. Examples of ISO-8601
        timestamps include ``2017-10-12 09:30Z``, ``2017-10-12 12:33:54+00:00``, and
        ``2017-10-12``
    :param recursive_symlinks: Specify the behavior of recursive directory transfers
        when encountering symlinks. One of ``"ignore"``, ``"keep"``, or ``"copy"``.
        ``"ignore"`` skips symlinks, ``"keep"`` creates symlinks at the destination
        matching the source (without modifying the link path at all), and
        ``"copy"`` follows symlinks on the source, failing if the link is invalid.
        [default: ``"ignore"``]
    :param skip_activation_check: When true, allow submission even if the endpoints
        aren't currently activated
    :param skip_source_errors: When true, source permission denied and file
        not found errors from the source endpoint will cause the offending
        path to be skipped.
        [default: ``False``]
    :param fail_on_quota_errors: When true, quota exceeded errors will cause the
        task to fail.
        [default: ``False``]
    :param delete_destination_extra: Delete files, directories, and symlinks on the
        destination endpoint which don’t exist on the source endpoint or are a
        different type. Only applies for recursive directory transfers.
        [default: ``False``]
    :param notify_on_succeeded: Send a notification email when the transfer completes
        with a status of SUCCEEDED.
        [default: ``True``]
    :param notify_on_failed: Send a notification email when the transfer completes
        with a status of FAILED.
        [default: ``True``]
    :param notify_on_inactive: Send a notification email when the transfer changes
        status to INACTIVE. e.g. From credentials expiring.
        [default: ``True``]
    :param source_local_user: Optional value passed to the source's identity mapping
        specifying which local user account to map to. Only usable with Globus Connect
        Server v5 mapped collections.
    :param destination_local_user: Optional value passed to the destination's identity
        mapping specifying which local user account to map to. Only usable with Globus
        Connect Server v5 mapped collections.
    :param additional_fields: additional fields to be added to the transfer
        document. Mostly intended for internal use

    **Sync Levels**

    The values for ``sync_level`` are used to determine how comparisons are made between
    files found both on the source and the destination. When files match, no data
    transfer will occur.

    For compatibility, this can be an integer ``0``, ``1``, ``2``, or ``3`` in addition
    to the string values.

    The meanings are as follows:

    =====================   ========
    value                   behavior
    =====================   ========
    ``0``, ``exists``       Determine whether or not to transfer based on file
                            existence. If the destination file is absent, do the
                            transfer.
    ``1``, ``size``         Determine whether or not to transfer based on the size of
                            the file. If destination file size does not match the
                            source, do the transfer.
    ``2``, ``mtime``        Determine whether or not to transfer based on modification
                            times. If source has a newer modified time than the
                            destination, do the transfer.
    ``3``, ``checksum``     Determine whether or not to transfer based on checksums of
                            file contents. If source and destination contents differ, as
                            determined by a checksum of their contents, do the transfer.
    =====================   ========

    **Examples**

    See the
    :meth:`submit_transfer <globus_sdk.TransferClient.submit_transfer>`
    documentation for example usage.

    **External Documentation**

    See the
    `Task document definition \
    <https://docs.globus.org/api/transfer/task_submit/#document_types>`_
    and
    `Transfer specific fields \
    <https://docs.globus.org/api/transfer/task_submit/#transfer_specific_fields>`_
    in the REST documentation for more details on Transfer Task documents.

    .. automethodlist:: globus_sdk.TransferData
    """

    def __init__(
        self,
        source_endpoint: UUIDLike,
        destination_endpoint: UUIDLike,
        *,
        label: str | MissingType = MISSING,
        submission_id: UUIDLike | MissingType = MISSING,
        sync_level: (
            int | t.Literal["exists", "size", "mtime", "checksum"] | MissingType
        ) = MISSING,
        verify_checksum: bool | MissingType = MISSING,
        preserve_timestamp: bool | MissingType = MISSING,
        encrypt_data: bool | MissingType = MISSING,
        deadline: datetime.datetime | str | MissingType = MISSING,
        skip_activation_check: bool | MissingType = MISSING,
        skip_source_errors: bool | MissingType = MISSING,
        fail_on_quota_errors: bool | MissingType = MISSING,
        recursive_symlinks: str | MissingType = MISSING,
        delete_destination_extra: bool | MissingType = MISSING,
        notify_on_succeeded: bool | MissingType = MISSING,
        notify_on_failed: bool | MissingType = MISSING,
        notify_on_inactive: bool | MissingType = MISSING,
        source_local_user: str | MissingType = MISSING,
        destination_local_user: str | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        log.debug("Creating a new TransferData object")
        self["DATA_TYPE"] = "transfer"
        self["DATA"] = []
        self["source_endpoint"] = source_endpoint
        self["destination_endpoint"] = destination_endpoint
        self["label"] = label
        self["submission_id"] = submission_id
        self["recursive_symlinks"] = recursive_symlinks
        self["deadline"] = deadline
        self["source_local_user"] = source_local_user
        self["destination_local_user"] = destination_local_user
        self["verify_checksum"] = verify_checksum
        self["preserve_timestamp"] = preserve_timestamp
        self["encrypt_data"] = encrypt_data
        self["skip_activation_check"] = skip_activation_check
        self["skip_source_errors"] = skip_source_errors
        self["fail_on_quota_errors"] = fail_on_quota_errors
        self["delete_destination_extra"] = delete_destination_extra
        self["notify_on_succeeded"] = notify_on_succeeded
        self["notify_on_failed"] = notify_on_failed
        self["notify_on_inactive"] = notify_on_inactive
        self["sync_level"] = _parse_sync_level(sync_level)

        for k, v in self.items():
            log.debug("TransferData.%s = %s", k, v)

        if additional_fields is not None:
            self.update(additional_fields)
            for option, value in additional_fields.items():
                log.debug(
                    f"TransferData.{option} = {value} (option passed "
                    "in via additional_fields)"
                )

    def add_item(
        self,
        source_path: str,
        destination_path: str,
        *,
        recursive: bool | MissingType = MISSING,
        external_checksum: str | MissingType = MISSING,
        checksum_algorithm: str | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        """
        Add a file or directory to be transferred. If the item is a symlink
        to a file or directory, the file or directory at the target of
        the symlink will be transferred.

        Appends a transfer_item document to the DATA key of the transfer
        document.

        .. note::

            The full path to the destination file must be provided for file items.
            Parent directories of files are not allowed. See
            `task submission documentation
            <https://docs.globus.org/api/transfer/task_submit/#submit_transfer_task>`_
            for more details.

        :param source_path: Path to the source directory or file to be transferred
        :param destination_path: Path to the destination directory or file will be
            transferred to
        :param recursive: Set to True if the target at source path is a directory
        :param external_checksum: A checksum to verify both source file and destination
            file integrity. The checksum will be verified after the data transfer and a
            failure will cause the entire task to fail. Cannot be used with directories.
            Assumed to be an MD5 checksum unless checksum_algorithm is also given.
        :param checksum_algorithm: Specifies the checksum algorithm to be used when
            verify_checksum is True, sync_level is "checksum" or 3, or an
            external_checksum is given.
        :param additional_fields: additional fields to be added to the transfer item
        """
        item_data: dict[str, t.Any] = {
            "DATA_TYPE": "transfer_item",
            "source_path": source_path,
            "destination_path": destination_path,
            "recursive": recursive,
            "external_checksum": external_checksum,
            "checksum_algorithm": checksum_algorithm,
            **(additional_fields or {}),
        }
        log.debug(
            'TransferData[{}, {}].add_item: "{}"->"{}"'.format(
                self["source_endpoint"],
                self["destination_endpoint"],
                source_path,
                destination_path,
            )
        )
        self["DATA"].append(item_data)

    def add_symlink_item(self, source_path: str, destination_path: str) -> None:
        """
        Add a symlink to be transferred as a symlink rather than as the
        target of the symlink.

        Appends a transfer_symlink_item document to the DATA key of the
        transfer document.

        :param source_path: Path to the source symlink
        :param destination_path: Path to which the source symlink will be transferred
        """
        item_data = {
            "DATA_TYPE": "transfer_symlink_item",
            "source_path": source_path,
            "destination_path": destination_path,
        }
        log.debug(
            'TransferData[{}, {}].add_symlink_item: "{}"->"{}"'.format(
                self["source_endpoint"],
                self["destination_endpoint"],
                source_path,
                destination_path,
            )
        )
        self["DATA"].append(item_data)

    def add_filter_rule(
        self,
        name: str,
        *,
        method: t.Literal["include", "exclude"] = "exclude",
        type: (  # pylint: disable=redefined-builtin
            t.Literal["file", "dir"] | MissingType
        ) = MISSING,
    ) -> None:
        """
        Add a filter rule to the transfer document.

        These rules specify which items are or are not included when recursively
        transferring directories. Each item that is found during recursive directory
        traversal is matched against these rules in the order they are listed.
        The method of the first filter rule that matches an item is applied (either
        "include" or "exclude"), and filter rule matching stops. If no rules match,
        the item is included in the transfer. Notably, this makes "include" filter
        rules only useful when overriding more general "exclude" filter rules later
        in the list.

        :param name: A pattern to match against item names. Wildcards are supported, as
            are character groups: ``*`` matches everything, ``?`` matches any single
            character, ``[]`` matches any single character within the brackets, and
            ``[!]`` matches any single character not within the brackets.
        :param method: The method to use for filtering. If "exclude" (the default)
            items matching this rule will not be included in the transfer. If
            "include" items matching this rule will be included in the transfer.
        :param type: The types of items on which to apply this filter rule. Either
            ``"file"`` or ``"dir"``. If unspecified, the rule applies to both.
            Note that if a ``"dir"`` is excluded then all items within it will
            also be excluded regardless if they would have matched any include rules.

        Example Usage:

        >>> tdata = TransferData(...)
        >>> tdata.add_filter_rule(method="exclude", "*.tgz", type="file")
        >>> tdata.add_filter_rule(method="exclude", "*.tar.gz", type="file")

        ``tdata`` now describes a transfer which will skip any gzipped tar files with
        the extensions ``.tgz`` or ``.tar.gz``

        >>> tdata = TransferData(...)
        >>> tdata.add_filter_rule(method="include", "*.txt", type="file")
        >>> tdata.add_filter_rule(method="exclude", "*", type="file")

        ``tdata`` now describes a transfer which will only transfer files
        with the ``.txt`` extension.
        """
        if self.get("filter_rules", MISSING) is MISSING:
            self["filter_rules"] = []
        rule = {
            "DATA_TYPE": "filter_rule",
            "method": method,
            "name": name,
            "type": type,
        }
        self["filter_rules"].append(rule)

    def iter_items(self) -> t.Iterator[dict[str, t.Any]]:
        """
        An iterator of items created by ``add_item``.

        Each item takes the form of a dictionary.
        """
        yield from iter(self["DATA"])
