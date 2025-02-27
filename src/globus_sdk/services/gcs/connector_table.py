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

    It supports access by attribute or via a helper method for doing lookups.
    For example, all of the following three usages retrieve the Azure Blob connector:

    .. code-block:: pycon

        >>> ConnectorTable.AZURE_BLOB
        >>> ConnectorTable.lookup("Azure Blob")
        >>> ConnectorTable.lookup("9436da0c-a444-11eb-af93-12704e0d6a4d")

    Given the results of such a lookup, you can retrieve the canonical name and ID for
    a connector like so:

    .. code-block:: pycon

        >>> connector = ConnectorTable.AZURE_BLOB
        >>> connector.name
        'Azure Blob'
        >>> connector.connector_id
        '9436da0c-a444-11eb-af93-12704e0d6a4d'
    """

    _connectors: t.ClassVar[tuple[tuple[str, str, str], ...]] = (
        ("ACTIVESCALE", "ActiveScale", "7251f6c8-93c9-11eb-95ba-12704e0d6a4d"),
        ("AZURE_BLOB", "Azure Blob", "9436da0c-a444-11eb-af93-12704e0d6a4d"),
        ("BLACKPEARL", "BlackPearl", "7e3f3f5e-350c-4717-891a-2f451c24b0d4"),
        ("BOX", "Box", "7c100eae-40fe-11e9-95a3-9cb6d0d9fd63"),
        ("CEPH", "Ceph", "1b6374b0-f6a4-4cf7-a26f-f262d9c6ca72"),
        ("DROPBOX", "Dropbox", "49b00fd6-63f1-48ae-b27f-d8af4589f876"),
        (
            "GOOGLE_CLOUD_STORAGE",
            "Google Cloud Storage",
            "56366b96-ac98-11e9-abac-9cb6d0d9fd63",
        ),
        ("GOOGLE_DRIVE", "Google Drive", "976cf0cf-78c3-4aab-82d2-7c16adbcc281"),
        ("HPSS", "HPSS", "fb656a17-0f69-4e59-95ff-d0a62ca7bdf5"),
        ("IRODS", "iRODS", "e47b6920-ff57-11ea-8aaa-000c297ab3c2"),
        ("POSIX", "POSIX", "145812c8-decc-41f1-83cf-bb2a85a2a70b"),
        ("POSIX_STAGING", "POSIX Staging", "052be037-7dda-4d20-b163-3077314dc3e6"),
        ("ONEDRIVE", "OneDrive", "28ef55da-1f97-11eb-bdfd-12704e0d6a4d"),
        ("S3", "S3", "7643e831-5f6c-4b47-a07f-8ee90f401d23"),
    )

    ACTIVESCALE: t.ClassVar[GlobusConnectServerConnector]
    AZURE_BLOB: t.ClassVar[GlobusConnectServerConnector]
    BLACKPEARL: t.ClassVar[GlobusConnectServerConnector]
    BOX: t.ClassVar[GlobusConnectServerConnector]
    CEPH: t.ClassVar[GlobusConnectServerConnector]
    DROPBOX: t.ClassVar[GlobusConnectServerConnector]
    GOOGLE_CLOUD_STORAGE: t.ClassVar[GlobusConnectServerConnector]
    GOOGLE_DRIVE: t.ClassVar[GlobusConnectServerConnector]
    HPSS: t.ClassVar[GlobusConnectServerConnector]
    IRODS: t.ClassVar[GlobusConnectServerConnector]
    ONEDRIVE: t.ClassVar[GlobusConnectServerConnector]
    POSIX: t.ClassVar[GlobusConnectServerConnector]
    POSIX_STAGING: t.ClassVar[GlobusConnectServerConnector]
    S3: t.ClassVar[GlobusConnectServerConnector]

    @classmethod
    def all_connectors(cls) -> t.Iterable[GlobusConnectServerConnector]:
        """
        Return an iterator of all known connectors.
        """
        for attribute, _, _ in cls._connectors:
            item: GlobusConnectServerConnector = getattr(cls, attribute)
            yield item

    @classmethod
    def lookup(cls, name_or_id: UUIDLike) -> GlobusConnectServerConnector | None:
        """
        Convert a name or ID into a connector object.
        Returns None if the name or ID is not recognized.

        Names are normalized before lookup so that they are case-insensitive and
        spaces, dashes, and underscores are all treated equivalently. For
        example, ``Google Drive``, ``google-drive``, and ``gOOgle_dRiVe`` are
        all equivalent.

        :param name_or_id: The name or ID of the connector
        """
        normalized = _normalize_name(str(name_or_id))
        for connector in cls.all_connectors():
            if normalized == connector.connector_id or normalized == _normalize_name(
                connector.name
            ):
                return connector
        return None

    @classmethod
    def extend(
        cls,
        *,
        connector_name: str,
        connector_id: UUIDLike,
        attribute_name: str | None = None,
    ) -> type[ConnectorTable]:
        """
        Extend the ConnectorTable class with a new connector, returning a new
        ConnectorTable subclass.

        Usage example:

        .. code-block:: pycon

            >>> MyTable = ConnectorTable.extend(
            ...     connector_name="Star Trek Transporter",
            ...     connector_id="0b19772d-729a-4c8f-93e1-59d5778cecf3",
            ... )
            >>> obj = MyTable.STAR_TREK_TRANSPORTER
            >>> obj.connector_id
            '0b19772d-729a-4c8f-93e1-59d5778cecf3'
            >>> obj.name
            'Star Trek Transporter'

        :param connector_name: The name of the connector to add
        :param connector_id: The ID of the connector to add
        :param attribute_name: The attribute name with which the connector will be
            attached to the new subclass. Defaults to the connector name uppercased and
            with spaces converted to underscores.
        """
        if attribute_name is None:
            attribute_name = connector_name.upper().replace(" ", "_")
        connector_id_str = str(connector_id)

        connectors = cls._connectors + (
            (attribute_name, connector_name, connector_id_str),
        )
        connector_obj = GlobusConnectServerConnector(
            name=connector_name, connector_id=connector_id_str
        )
        return type(
            "ExtendedConnectorTable",
            (cls,),
            {"_connectors": connectors, attribute_name: connector_obj},
        )


# "render" the _connectors to live attributes of the ConnectorTable
for _attribute, _name, _id in ConnectorTable._connectors:
    setattr(
        ConnectorTable,
        _attribute,
        GlobusConnectServerConnector(name=_name, connector_id=_id),
    )
del _attribute, _name, _id
