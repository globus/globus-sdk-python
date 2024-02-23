from __future__ import annotations

import dataclasses
import re
import typing as t

from globus_sdk._types import UUIDLike

_NORMALIZATION_PATTERN = re.compile(r"[_\- ]+")


def _normalize_name(name: str) -> str:
    return _NORMALIZATION_PATTERN.sub("-", name.strip()).lower()


@dataclasses.dataclass
class GlobusConnectServerConnector:
    """
    A container for Globus Connect Server Connector descriptions.
    Contains a ``name`` and a ``connector_id``.
    """

    name: str
    connector_id: str


class ConnectorTable:
    """
    This class defines the known Globus Connect Server Connectors in a mapping
    structure.

    It supports access by attribute or via helper methods for doing lookups.
    For example, all of the following three usages retrieve the Azure Blob connector:

    .. code-block:: pycon

        >>> ConnectorTable.AZURE_BLOB
        >>> ConnectorTable.lookup("Azure Blob")
        >>> ConnectorTable.lookup_by_id("9436da0c-a444-11eb-af93-12704e0d6a4d")

    Given the results of such a lookup, you can retrieve the canonical name and ID for
    a connector like so:

    .. code-block:: pycon

        >>> connector = ConnectorTable.AZURE_BLOB
        >>> connector.name
        'Azure Blob'
        >>> connector.connector_id
        '9436da0c-a444-11eb-af93-12704e0d6a4d'
    """

    POSIX: t.ClassVar[GlobusConnectServerConnector] = GlobusConnectServerConnector(
        name="POSIX", connector_id="145812c8-decc-41f1-83cf-bb2a85a2a70b"
    )
    AZURE_BLOB: t.ClassVar[GlobusConnectServerConnector] = GlobusConnectServerConnector(
        name="Azure Blob", connector_id="9436da0c-a444-11eb-af93-12704e0d6a4d"
    )
    BLACKPEARL: t.ClassVar[GlobusConnectServerConnector] = GlobusConnectServerConnector(
        name="BlackPearl", connector_id="7e3f3f5e-350c-4717-891a-2f451c24b0d4"
    )
    BOX: t.ClassVar[GlobusConnectServerConnector] = GlobusConnectServerConnector(
        name="Box", connector_id="7c100eae-40fe-11e9-95a3-9cb6d0d9fd63"
    )
    CEPH: t.ClassVar[GlobusConnectServerConnector] = GlobusConnectServerConnector(
        name="Ceph", connector_id="1b6374b0-f6a4-4cf7-a26f-f262d9c6ca72"
    )
    DROPBOX: t.ClassVar[GlobusConnectServerConnector] = GlobusConnectServerConnector(
        name="Dropbox", connector_id="49b00fd6-63f1-48ae-b27f-d8af4589f876"
    )
    ONEDRIVE: t.ClassVar[GlobusConnectServerConnector] = GlobusConnectServerConnector(
        name="OneDrive", connector_id="28ef55da-1f97-11eb-bdfd-12704e0d6a4d"
    )
    GOOGLE_DRIVE: t.ClassVar[GlobusConnectServerConnector] = (
        GlobusConnectServerConnector(
            name="Google Drive", connector_id="976cf0cf-78c3-4aab-82d2-7c16adbcc281"
        )
    )
    GOOGLE_CLOUD_STORAGE: t.ClassVar[GlobusConnectServerConnector] = (
        GlobusConnectServerConnector(
            name="Google Cloud Storage",
            connector_id="56366b96-ac98-11e9-abac-9cb6d0d9fd63",
        )
    )
    ACTIVESCALE: t.ClassVar[GlobusConnectServerConnector] = (
        GlobusConnectServerConnector(
            name="ActiveScale", connector_id="7251f6c8-93c9-11eb-95ba-12704e0d6a4d"
        )
    )
    S3: t.ClassVar[GlobusConnectServerConnector] = GlobusConnectServerConnector(
        name="S3", connector_id="7643e831-5f6c-4b47-a07f-8ee90f401d23"
    )
    POSIX_STAGING: t.ClassVar[GlobusConnectServerConnector] = (
        GlobusConnectServerConnector(
            name="POSIX Staging", connector_id="052be037-7dda-4d20-b163-3077314dc3e6"
        )
    )
    IRODS: t.ClassVar[GlobusConnectServerConnector] = GlobusConnectServerConnector(
        name="iRODS", connector_id="e47b6920-ff57-11ea-8aaa-000c297ab3c2"
    )
    HPSS: t.ClassVar[GlobusConnectServerConnector] = GlobusConnectServerConnector(
        name="HPSS", connector_id="fb656a17-0f69-4e59-95ff-d0a62ca7bdf5"
    )

    @classmethod
    def all_connectors(cls) -> t.Iterable[GlobusConnectServerConnector]:
        """
        Return an iterator of all known connectors.
        """
        for item in vars(cls).values():
            if isinstance(item, GlobusConnectServerConnector):
                yield item

    @classmethod
    def lookup(cls, name: str) -> GlobusConnectServerConnector | None:
        """
        Convert a name into a connector object (containing name and ID).
        Returns None if the name is not recognized.

        Names are normalized before lookup so that they are case-insensitive and
        spaces, dashes, and underscores are all treated equivalently. For
        example, ``Google Drive``, ``google-drive``, and ``gOOgle_dRiVe`` are
        all equivalent.

        :param name: The name of the connector
        """
        normed_name = _normalize_name(name)
        for item in cls.all_connectors():
            if _normalize_name(item.name) == normed_name:
                return item
        return None

    @classmethod
    def lookup_by_id(
        cls, connector_id: UUIDLike
    ) -> GlobusConnectServerConnector | None:
        """
        Convert a connector_id into a connector object (containing name and ID).
        Returns None if the id is not recognized.

        :param connector_id: The ID of the connector
        """
        connector_id_s = str(connector_id)
        for item in cls.all_connectors():
            if item.connector_id == connector_id_s:
                return item
        return None
