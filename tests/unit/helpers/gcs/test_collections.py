import uuid

import pytest

from globus_sdk import (
    CollectionDocument,
    GoogleCloudStorageCollectionPolicies,
    GuestCollectionDocument,
    MappedCollectionDocument,
    POSIXCollectionPolicies,
    POSIXStagingCollectionPolicies,
)

STUB_SG_ID = uuid.uuid1()  # storage gateway
STUB_MC_ID = uuid.uuid1()  # mapped collection
STUB_UC_ID = uuid.uuid1()  # user credential


def test_collection_base_abstract():
    with pytest.raises(TypeError):
        CollectionDocument()


def test_collection_type_field():
    m = MappedCollectionDocument(
        storage_gateway_id=STUB_SG_ID, collection_base_path="/"
    )
    g = GuestCollectionDocument(
        mapped_collection_id=STUB_MC_ID,
        user_credential_id=STUB_UC_ID,
        collection_base_path="/",
    )
    assert m["collection_type"] == "mapped"
    assert g["collection_type"] == "guest"


@pytest.mark.parametrize(
    "use_kwargs,doc_version",
    [
        ({}, "1.0.0"),
        ({"user_message_link": "https://example.net/"}, "1.1.0"),
        ({"user_message": "kthxbye"}, "1.1.0"),
        ({"user_message": ""}, "1.1.0"),
        ({"enable_https": True}, "1.1.0"),
        ({"enable_https": False}, "1.1.0"),
        # a string of length > 64
        ({"user_message": "long message..." + "x" * 100}, "1.7.0"),
    ],
)
def test_datatype_version_deduction(use_kwargs, doc_version):
    m = MappedCollectionDocument(**use_kwargs)
    assert m["DATA_TYPE"] == f"collection#{doc_version}"
    g = GuestCollectionDocument(**use_kwargs)
    assert g["DATA_TYPE"] == f"collection#{doc_version}"


@pytest.mark.parametrize(
    "use_kwargs,doc_version",
    [
        ({"sharing_users_allow": "sirosen"}, "1.2.0"),
        ({"sharing_users_allow": ["sirosen", "aaschaer"]}, "1.2.0"),
        ({"sharing_users_deny": "sirosen"}, "1.2.0"),
        ({"sharing_users_deny": ["sirosen", "aaschaer"]}, "1.2.0"),
        ({"force_verify": True}, "1.4.0"),
        ({"force_verify": False}, "1.4.0"),
        ({"disable_anonymous_writes": True}, "1.5.0"),
        ({"disable_anonymous_writes": False}, "1.5.0"),
        ({"guest_auth_policy_id": str(uuid.uuid4())}, "1.6.0"),
    ],
)
def test_datatype_version_deduction_mapped_specific_fields(use_kwargs, doc_version):
    d = MappedCollectionDocument(**use_kwargs)
    assert d["DATA_TYPE"] == f"collection#{doc_version}"


def test_datatype_version_deduction_add_custom(monkeypatch):
    custom_field = "foo-made-up-field"
    monkeypatch.setitem(
        CollectionDocument.DATATYPE_VERSION_IMPLICATIONS, custom_field, (1, 20, 0)
    )

    m = MappedCollectionDocument(
        storage_gateway_id=STUB_SG_ID,
        collection_base_path="/",
        additional_fields={custom_field: "foo"},
    )
    assert m["DATA_TYPE"] == "collection#1.20.0"
    g = GuestCollectionDocument(
        mapped_collection_id=STUB_MC_ID,
        user_credential_id=STUB_UC_ID,
        collection_base_path="/",
        additional_fields={custom_field: "foo"},
    )
    assert g["DATA_TYPE"] == "collection#1.20.0"


@pytest.mark.parametrize(
    "policies_type",
    (
        dict,
        POSIXCollectionPolicies,
        POSIXStagingCollectionPolicies,
        GoogleCloudStorageCollectionPolicies,
    ),
)
def test_collection_policies_field(policies_type):
    if policies_type is dict:
        policy_data = {"spam": "eggs"}
    elif policies_type in (POSIXCollectionPolicies, POSIXStagingCollectionPolicies):
        policy_data = policies_type(
            sharing_groups_allow=["foo", "bar"],
            sharing_groups_deny="baz",
            additional_fields={"spam": "eggs"},
        )
    elif policies_type is GoogleCloudStorageCollectionPolicies:
        policy_data = GoogleCloudStorageCollectionPolicies(
            project="foo", additional_fields={"spam": "eggs"}
        )
    else:
        raise NotImplementedError

    # only Mapped Collections support a policies subdocument
    doc = MappedCollectionDocument(
        storage_gateway_id=STUB_SG_ID,
        collection_base_path="/",
        policies=policy_data,
    )

    assert "policies" in doc
    assert isinstance(doc["policies"], dict)

    if policies_type is dict:
        assert doc["policies"] == {"spam": "eggs"}
    elif policies_type is POSIXCollectionPolicies:
        assert doc["policies"] == {
            "DATA_TYPE": "posix_collection_policies#1.0.0",
            "spam": "eggs",
            "sharing_groups_allow": ["foo", "bar"],
            "sharing_groups_deny": ["baz"],
        }
    elif policies_type is POSIXStagingCollectionPolicies:
        assert doc["policies"] == {
            "DATA_TYPE": "posix_staging_collection_policies#1.0.0",
            "spam": "eggs",
            "sharing_groups_allow": ["foo", "bar"],
            "sharing_groups_deny": ["baz"],
        }
    elif policies_type is GoogleCloudStorageCollectionPolicies:
        assert doc["policies"] == {
            "DATA_TYPE": "google_cloud_storage_collection_policies#1.0.0",
            "spam": "eggs",
            "project": "foo",
        }
    else:
        raise NotImplementedError
