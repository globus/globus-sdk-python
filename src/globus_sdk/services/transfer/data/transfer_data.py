import datetime
import logging
import sys
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional, Union

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from globus_sdk import exc, utils
from globus_sdk._types import UUIDLike

if TYPE_CHECKING:
    import globus_sdk

log = logging.getLogger(__name__)
_StrSyncLevel = Literal["exists", "size", "mtime", "checksum"]
_sync_level_dict: Dict[_StrSyncLevel, int] = {
    "exists": 0,
    "size": 1,
    "mtime": 2,
    "checksum": 3,
}


def _parse_sync_level(sync_level: Union[_StrSyncLevel, int]) -> int:
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


class TransferData(utils.PayloadWrapper):
    r"""
    Convenience class for constructing a transfer document, to use as the
    ``data`` parameter to
    :meth:`submit_transfer <globus_sdk.TransferClient.submit_transfer>`.

    At least one item must be added using
    :meth:`add_item <globus_sdk.TransferData.add_item>`.

    If ``submission_id`` isn't passed, one will be fetched automatically. The
    submission ID can be pulled out of here to inspect, but the document
    can be used as-is multiple times over to retry a potential submission
    failure (so there shouldn't be any need to inspect it).

    :param transfer_client: A ``TransferClient`` instance which will be used to get a
        submission ID if one is not supplied. Should be the same instance that is used
        to submit the transfer.
    :type transfer_client: :class:`TransferClient <globus_sdk.TransferClient>` or None
    :param source_endpoint: The endpoint ID of the source endpoint
    :type source_endpoint: str or UUID
    :param destination_endpoint: The endpoint ID of the destination endpoint
    :type destination_endpoint: str or UUID
    :param label: A string label for the Task
    :type label: str, optional
    :param submission_id: A submission ID value fetched via :meth:`get_submission_id \
        <globus_sdk.TransferClient.get_submission_id>`. Defaults to using
        ``transfer_client.get_submission_id``
    :type submission_id: str or UUID, optional
    :param sync_level: The method used to compare items between the source and
        destination. One of  ``"exists"``, ``"size"``, ``"mtime"``, or ``"checksum"``
        See the section below on sync-level for an explanation of values.
    :type sync_level: int or str, optional
    :param verify_checksum: When true, after transfer verify that the source and
        destination file checksums match. If they don't, re-transfer the entire file and
        keep trying until it succeeds. This will create CPU load on both the origin and
        destination of the transfer, and may even be a bottleneck if the network speed
        is high enough.
        [default: ``False``]
    :type verify_checksum: bool, optional
    :param preserve_timestamp: When true, Globus Transfer will attempt to set file
        timestamps on the destination to match those on the origin. [default: ``False``]
    :type preserve_timestamp: bool, optional
    :param encrypt_data: When true, all files will be TLS-protected during transfer.
        [default: ``False``]
    :type encrypt_data: bool, optional
    :param deadline: An ISO-8601 timestamp (as a string) or a datetime object which
        defines a deadline for the transfer. At the deadline, even if the data transfer
        is not complete, the job will be canceled. We recommend ensuring that the
        timestamp is in UTC to avoid confusion and ambiguity. Examples of ISO-8601
        timestamps include ``2017-10-12 09:30Z``, ``2017-10-12 12:33:54+00:00``, and
        ``2017-10-12``
    :type deadline: str or datetime, optional
    :param recursive_symlinks: Specify the behavior of recursive directory transfers
        when encountering symlinks. One of ``"ignore"``, ``"keep"``, or ``"copy"``.
        ``"ignore"`` skips symlinks, ``"keep"`` creates symlinks at the destination
        matching the source (without modifying the link path at all), and
        ``"copy"`` follows symlinks on the source, failing if the link is invalid.
        [default: ``"ignore"``]
    :type recursive_symlinks: str
    :param skip_activation_check: When true, allow submission even if the endpoints
        aren't currently activated
    :type skip_activation_check: bool, optional
    :param skip_source_errors: When true, source permission denied and file
        not found errors from the source endpoint will cause the offending
        path to be skipped.
        [default: ``False``]
    :type skip_source_errors: bool, optional
    :param fail_on_quota_errors: When true, quota exceeded errors will cause the
        task to fail.
        [default: ``False``]
    :type fail_on_quota_errors: bool, optional
    :param delete_destination_extra: Delete files, directories, and symlinks on the
        destination endpoint which don’t exist on the source endpoint or are a
        different type. Only applies for recursive directory transfers.
        [default: ``False``]
    :type delete_destination_extra: bool, optional
    :param notify_on_succeeded: Send a notification email when the transfer completes
        with a status of SUCCEEDED.
        [default: ``True``]
    :type notify_on_succeeded: bool, optional
    :param notify_on_failed: Send a notification email when the transfer completes
        with a status of FAILED.
        [default: ``True``]
    :type notify_on_failed: bool, optional
    :param notify_on_inactive: Send a notification email when the transfer changes
        status to INACTIVE. e.g. From credentials expiring.
        [default: ``True``]
    :type notify_on_inactive: bool, optional
    :param additional_fields: additional fields to be added to the transfer
        document. Mostly intended for internal use
    :type additional_fields: dict, optional

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
        transfer_client: Optional["globus_sdk.TransferClient"] = None,
        source_endpoint: Optional[UUIDLike] = None,
        destination_endpoint: Optional[UUIDLike] = None,
        *,
        label: Optional[str] = None,
        submission_id: Optional[UUIDLike] = None,
        sync_level: Union[_StrSyncLevel, int, None] = None,
        verify_checksum: bool = False,
        preserve_timestamp: bool = False,
        encrypt_data: bool = False,
        deadline: Union[datetime.datetime, str, None] = None,
        skip_activation_check: Optional[bool] = None,
        skip_source_errors: bool = False,
        fail_on_quota_errors: bool = False,
        recursive_symlinks: Optional[str] = None,
        delete_destination_extra: bool = False,
        notify_on_succeeded: bool = True,
        notify_on_failed: bool = True,
        notify_on_inactive: bool = True,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        # these must be checked explicitly to handle the fact that `transfer_client` is
        # the first arg
        if source_endpoint is None:
            raise exc.GlobusSDKUsageError("source_endpoint is required")
        if destination_endpoint is None:
            raise exc.GlobusSDKUsageError("destination_endpoint is required")

        log.info("Creating a new TransferData object")
        self["DATA_TYPE"] = "transfer"
        self["DATA"] = []
        self._set_optstrs(
            source_endpoint=source_endpoint,
            destination_endpoint=destination_endpoint,
            label=label,
            submission_id=submission_id
            or (
                transfer_client.get_submission_id()["value"]
                if transfer_client
                else None
            ),
            recursive_symlinks=recursive_symlinks,
            deadline=deadline,
        )
        self._set_optbools(
            verify_checksum=verify_checksum,
            preserve_timestamp=preserve_timestamp,
            encrypt_data=encrypt_data,
            skip_activation_check=skip_activation_check,
            skip_source_errors=skip_source_errors,
            fail_on_quota_errors=fail_on_quota_errors,
            delete_destination_extra=delete_destination_extra,
            notify_on_succeeded=notify_on_succeeded,
            notify_on_failed=notify_on_failed,
            notify_on_inactive=notify_on_inactive,
        )
        self._set_value("sync_level", sync_level, callback=_parse_sync_level)

        for k, v in self.items():
            log.info("TransferData.%s = %s", k, v)

        if additional_fields is not None:
            self.update(additional_fields)
            for option, value in additional_fields.items():
                log.info(
                    f"TransferData.{option} = {value} (option passed "
                    "in via additional_fields)"
                )

    def add_item(
        self,
        source_path: str,
        destination_path: str,
        *,
        recursive: bool = False,
        external_checksum: Optional[str] = None,
        checksum_algorithm: Optional[str] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
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
        :type source_path: str
        :param destination_path: Path to the destination directory or file will be
            transferred to
        :type destination_path: str
        :param recursive: Set to True if the target at source path is a directory
        :type recursive: bool
        :param external_checksum: A checksum to verify both source file and destination
            file integrity. The checksum will be verified after the data transfer and a
            failure will cause the entire task to fail. Cannot be used with directories.
            Assumed to be an MD5 checksum unless checksum_algorithm is also given.
        :type external_checksum: str, optional
        :param checksum_algorithm: Specifies the checksum algorithm to be used when
            verify_checksum is True, sync_level is "checksum" or 3, or an
            external_checksum is given.
        :type checksum_algorithm: str, optional
        :param additional_fields: additional fields to be added to the transfer item
        :type additional_fields: dict, optional
        """
        item_data = {
            "DATA_TYPE": "transfer_item",
            "source_path": source_path,
            "destination_path": destination_path,
            "recursive": recursive,
        }
        if external_checksum is not None:
            item_data["external_checksum"] = external_checksum
        if checksum_algorithm is not None:
            item_data["checksum_algorithm"] = checksum_algorithm
        if additional_fields is not None:
            item_data.update(additional_fields)

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
        :type source_path: str
        :param destination_path: Path to which the source symlink will be transferred
        :type destination_path: str
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
        method: Literal["exclude"] = "exclude",
        type: Optional[  # pylint: disable=redefined-builtin
            Literal["file", "dir"]
        ] = None,
    ) -> None:
        """
        Add a filter rule to the transfer document.

        These rules specify which items are or are not included when recursively
        transferring directories.

        Currently, only ``method="exclude"`` (the default) is supported. This means that
        items matching the ``name`` field will be excluded from the transfer.

        :param name: A pattern to match against item names. Wildcards are supported, as
            are character groups: ``*`` matches everything, ``?`` matches any single
            character, ``[]`` matches any single character within the brackets, and
            ``[!]`` matches any single character not within the brackets.
        :type name: str
        :param method: The method to use for filtering. Only the default, ``"exclude"``
            is supported.
        :type method: str, optional
        :param type: The types of items on which to apply this filter rule. Either
            ``"file"`` or ``"dir"``. If unspecified, the rule applies to both.
        :type type: str, optional

        Example Usage:

        >>> tdata = TransferData(...)
        >>> tdata.add_filter_rule("*.tgz", type="file")
        >>> tdata.add_filter_rule("*.tar.gz", type="file")

        ``tdata`` now describes a transfer which will skip any gzipped tar files with
        the extensions `.tgz` or `.tar.gz`
        """
        if "filter_rules" not in self:
            self["filter_rules"] = []
        rule = {
            "DATA_TYPE": "filter_rule",
            "method": method,
            "name": name,
        }
        if type is not None:
            rule["type"] = type
        self["filter_rules"].append(rule)

    def iter_items(self) -> Iterator[Dict[str, Any]]:
        """
        An iterator of items created by ``add_item``.

        Each item takes the form of a dictionary.
        """
        yield from iter(self["DATA"])
