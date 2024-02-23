from __future__ import annotations

import uuid

import pytest

from globus_sdk import ConnectorTable, GCSClient, exc

# tuple of attribute name, connector name, and connector id
#
# this is basically a copy of the ConnectorTable data, but more simply structured
_CONNECTORS: tuple[tuple[str, str, str], ...] = (
    ("POSIX", "POSIX", "145812c8-decc-41f1-83cf-bb2a85a2a70b"),
    ("AZURE_BLOB", "Azure Blob", "9436da0c-a444-11eb-af93-12704e0d6a4d"),
    ("BLACKPEARL", "BlackPearl", "7e3f3f5e-350c-4717-891a-2f451c24b0d4"),
    ("BOX", "Box", "7c100eae-40fe-11e9-95a3-9cb6d0d9fd63"),
    ("CEPH", "Ceph", "1b6374b0-f6a4-4cf7-a26f-f262d9c6ca72"),
    ("DROPBOX", "Dropbox", "49b00fd6-63f1-48ae-b27f-d8af4589f876"),
    ("ONEDRIVE", "OneDrive", "28ef55da-1f97-11eb-bdfd-12704e0d6a4d"),
    ("GOOGLE_DRIVE", "Google Drive", "976cf0cf-78c3-4aab-82d2-7c16adbcc281"),
    (
        "GOOGLE_CLOUD_STORAGE",
        "Google Cloud Storage",
        "56366b96-ac98-11e9-abac-9cb6d0d9fd63",
    ),
    ("ACTIVESCALE", "ActiveScale", "7251f6c8-93c9-11eb-95ba-12704e0d6a4d"),
    ("S3", "S3", "7643e831-5f6c-4b47-a07f-8ee90f401d23"),
    ("POSIX_STAGING", "POSIX Staging", "052be037-7dda-4d20-b163-3077314dc3e6"),
    ("IRODS", "iRODS", "e47b6920-ff57-11ea-8aaa-000c297ab3c2"),
    ("HPSS", "HPSS", "fb656a17-0f69-4e59-95ff-d0a62ca7bdf5"),
)


def test_deprecated_connector_lookup_method_warns():
    client = GCSClient("foo.bar.example.org")
    with pytest.warns(exc.RemovedInV4Warning):
        assert client.connector_id_to_name("foo") is None


@pytest.mark.parametrize("connector_data", _CONNECTORS)
def test_lookup_by_attribute(connector_data):
    attrname, connector_name, _ = connector_data

    connector = getattr(ConnectorTable, attrname)
    assert connector.name == connector_name


@pytest.mark.parametrize("connector_data", _CONNECTORS)
@pytest.mark.parametrize("as_uuid", (True, False))
def test_lookup_by_id(connector_data, as_uuid):
    _, connector_name, connector_id = connector_data

    if as_uuid:
        connector_id = uuid.UUID(connector_id)

    connector = ConnectorTable.lookup_by_id(connector_id)
    assert connector.name == connector_name


@pytest.mark.parametrize("connector_data", _CONNECTORS)
def test_lookup_by_name(connector_data):
    _, connector_name, connector_id = connector_data

    connector = ConnectorTable.lookup(connector_name)
    assert connector.connector_id == connector_id


@pytest.mark.parametrize(
    "lookup_name, expect_name",
    (
        ("Google Drive", "Google Drive"),
        ("google drive", "Google Drive"),
        ("google_drive", "Google Drive"),
        ("google-drive", "Google Drive"),
        ("google-----drive", "Google Drive"),
        ("google-_-drive", "Google Drive"),  # moody
        ("  google_-drIVE", "Google Drive"),
        ("google_-drIVE    ", "Google Drive"),
        ("   GOOGLE DRIVE    ", "Google Drive"),
    ),
)
def test_lookup_by_name_normalization(lookup_name, expect_name):
    connector = ConnectorTable.lookup(lookup_name)
    assert connector.name == expect_name


@pytest.mark.parametrize("name", [c.name for c in ConnectorTable.all_connectors()])
def test_all_connector_names_map_to_attributes(name):
    connector = ConnectorTable.lookup(name)
    assert connector is not None
    name = name.replace(" ", "_").upper()
    assert getattr(ConnectorTable, name) == connector
