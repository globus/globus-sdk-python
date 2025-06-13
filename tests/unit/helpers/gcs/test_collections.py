import inspect
import typing as t
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
from globus_sdk._missing import MISSING, MissingType, filter_missing
from globus_sdk._types import UUIDLike
from globus_sdk.transport import JSONRequestEncoder

STUB_SG_ID = uuid.uuid1()  # storage gateway
STUB_MC_ID = uuid.uuid1()  # mapped collection
STUB_UC_ID = uuid.uuid1()  # user credential


MappedCollectionSignature = inspect.signature(MappedCollectionDocument.__init__)
GuestCollectionSignature = inspect.signature(GuestCollectionDocument.__init__)


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
        ({"delete_protected": False}, "1.8.0"),
        # combining a long user_message (which uses callback-based detection) with
        # higher and lower bounding fields needs to apply correctly
        (
            {"force_verify": False, "user_message": "long message..." + "x" * 100},
            "1.7.0",
        ),
        (
            {"delete_protected": False, "user_message": "long message..." + "x" * 100},
            "1.8.0",
        ),
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
def test_collection_policies_field_encoded(policies_type):
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
    assert isinstance(doc["policies"], policies_type)

    encoder = JSONRequestEncoder()
    request_data = encoder.encode("POST", "bogus.url.example", {}, doc, {}).json

    if policies_type is dict:
        assert request_data["policies"] == {"spam": "eggs"}
    elif policies_type is POSIXCollectionPolicies:
        assert request_data["policies"] == {
            "DATA_TYPE": "posix_collection_policies#1.0.0",
            "spam": "eggs",
            "sharing_groups_allow": ["foo", "bar"],
            "sharing_groups_deny": ["baz"],
        }
    elif policies_type is POSIXStagingCollectionPolicies:
        assert request_data["policies"] == {
            "DATA_TYPE": "posix_staging_collection_policies#1.0.0",
            "spam": "eggs",
            "sharing_groups_allow": ["foo", "bar"],
            "sharing_groups_deny": ["baz"],
        }
    elif policies_type is GoogleCloudStorageCollectionPolicies:
        assert request_data["policies"] == {
            "DATA_TYPE": "google_cloud_storage_collection_policies#1.0.0",
            "spam": "eggs",
            "project": "foo",
        }
    else:
        raise NotImplementedError


# these test cases enumerate parameters for Guest Collections and Mapped Collections
# and ensure that they're defined on one class but not the other
@pytest.mark.parametrize(
    "fieldname",
    (
        "allow_guest_collections",
        "delete_protected",
        "disable_anonymous_writes",
        "domain_name",
        "guest_auth_policy_id",
        "policies",
        "sharing_restrict_paths",
        "sharing_users_allow",
        "sharing_users_deny",
        "storage_gateway_id",
    ),
)
def test_settings_which_are_only_supported_in_mapped_collections(fieldname):
    assert fieldname in MappedCollectionSignature.parameters
    assert fieldname not in GuestCollectionSignature.parameters


@pytest.mark.parametrize(
    "fieldname",
    (
        "mapped_collection_id",
        "user_credential_id",
    ),
)
def test_settings_which_are_only_supported_in_guest_collections(fieldname):
    assert fieldname in GuestCollectionSignature.parameters
    assert fieldname not in MappedCollectionSignature.parameters


@pytest.mark.parametrize(
    "fieldname",
    (
        "disable_verify",
        "enable_https",
        "force_encryption",
        "force_verify",
        "public",
        "delete_protected",
        "allow_guest_collections",
        "disable_anonymous_writes",
    ),
)
@pytest.mark.parametrize("value", (True, False, None))
def test_mapped_collection_opt_bool(fieldname, value):
    data = {}
    if value is not None:
        data[fieldname] = value

    doc = filter_missing(
        MappedCollectionDocument(
            storage_gateway_id=STUB_SG_ID,
            collection_base_path="/",
            **data,
        )
    )
    if value is not None:
        assert fieldname in doc
        assert doc[fieldname] == value
    else:
        assert fieldname not in doc


common_collection_fields = [
    ("collection_base_path", (str, MissingType)),
    ("contact_email", (str, None, MissingType)),
    ("contact_info", (str, None, MissingType)),
    ("default_directory", (str, MissingType)),
    ("department", (str, None, MissingType)),
    ("description", (str, None, MissingType)),
    ("display_name", (str, MissingType)),
    ("identity_id", (UUIDLike, MissingType)),
    ("info_link", (str, None, MissingType)),
    ("organization", (str, MissingType)),
    ("user_message", (str, None, MissingType)),
    ("user_message_link", (str, None, MissingType)),
    ("keywords", (t.Iterable[str], MissingType)),
    ("disable_verify", (bool, MissingType)),
    ("enable_https", (bool, MissingType)),
    ("force_encryption", (bool, MissingType)),
    ("force_verify", (bool, MissingType)),
    ("public", (bool, MissingType)),
]


mapped_collection_fields = [
    *common_collection_fields,
    ("domain_name", (str, MissingType)),
    ("guest_auth_policy_id", (UUIDLike, None, MissingType)),
    ("disable_anonymous_writes", (bool, MissingType)),
    ("policies", (t.Dict[str, t.Any], MissingType)),
]


guest_collection_fields = [
    *common_collection_fields,
    ("mapped_collection_id", (UUIDLike, MissingType)),
    ("user_credential_id", (UUIDLike, MissingType)),
    ("activity_notification_policy", (t.Dict[str, t.List[str]], MissingType)),
]


def expand_collection_fields(fields):
    """
    Expand each collection field into (field, valid_value)
    """
    return [
        (param, value)
        for param, types in fields
        for _type in types
        for value in _gen_value(_type)
    ]


def _gen_value(_type):
    """
    Return a list of valid values for type _type.
    """
    if _type is MissingType:
        return [MISSING]
    if _type is None:
        return [None]
    if _type is str:
        return ["STRING"]
    if _type is bool:
        return [True, False]
    if _type is UUIDLike:
        return [str(uuid.uuid1()), uuid.uuid1()]
    if _type is t.Iterable[str]:
        return [[], ["a", "b", "c"]]
    if _type is t.Dict[str, t.Any]:
        return [{"A": 1}]
    if _type is t.Dict[str, t.List[str]]:
        return [{"a": ["b", "c"]}]

    raise AssertionError(f"Unexpected Type: {_type}")


@pytest.mark.parametrize(
    "fieldname,value",
    expand_collection_fields(mapped_collection_fields),
)
def test_mapped_collection_fields(fieldname, value):
    """
    Verify that each field in the mapped collection document can be set to a valid
    value.
    """
    data = {}
    if value != MISSING:
        data[fieldname] = value

    doc = MappedCollectionDocument(**data)
    assert doc[fieldname] == value


@pytest.mark.parametrize(
    "fieldname,value",
    expand_collection_fields(guest_collection_fields),
)
def test_guest_collection_fields(fieldname, value):
    """
    Verify that each field in the guest collection document can be set to a valid
    value.
    """
    data = {}
    if value != MISSING:
        data[fieldname] = value

    doc = GuestCollectionDocument(**data)
    assert doc[fieldname] == value
