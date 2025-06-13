import uuid

import pytest

from globus_sdk import MISSING
from globus_sdk._payload import Payload
from globus_sdk.transport import FormRequestEncoder, JSONRequestEncoder, RequestEncoder


@pytest.mark.parametrize("data", ("foo", b"bar"))
def test_text_request_encoder_accepts_string_data(data):
    encoder = RequestEncoder()
    request = encoder.encode(
        "GET",
        "http://bogus/foo",
        data=data,
        params={},
        headers={},
    )
    assert request.data == data


@pytest.mark.parametrize(
    "encoder_class",
    [FormRequestEncoder, JSONRequestEncoder, RequestEncoder],
)
def test_all_request_encoders_stringify_uuids_in_params_and_headers(encoder_class):
    # ensure the different classes get data which they will find palatable
    data = "bar" if encoder_class is RequestEncoder else {"bar": "baz"}

    id_ = uuid.uuid1()
    id_str = str(id_)

    encoder = encoder_class()
    request = encoder.encode(
        "GET",
        "http://bogus/foo",
        params={"id": id_},
        data=data,
        headers={"X-UUID": id_},
    )

    assert request.params["id"] == id_str
    assert request.headers["X-UUID"] == id_str


@pytest.mark.parametrize(
    "encoder_class",
    [FormRequestEncoder, JSONRequestEncoder, RequestEncoder],
)
def test_all_request_encoders_remove_missing_in_params_and_headers(encoder_class):
    # ensure the different classes get data which they will find palatable
    data = "bar" if encoder_class is RequestEncoder else {"bar": "baz"}

    encoder = encoder_class()
    request = encoder.encode(
        "GET",
        "http://bogus/foo",
        params={"foo": "foo", "bar": MISSING},
        data=data,
        headers={
            "X-FOO": "foo",
            "X-BAR": MISSING,
        },
    )
    assert request.params == {"foo": "foo"}
    if encoder_class is JSONRequestEncoder:
        assert request.headers == {"X-FOO": "foo", "Content-Type": "application/json"}
    else:
        assert request.headers == {"X-FOO": "foo"}


@pytest.mark.parametrize(
    "using_payload_type, payload_contents, expected_data",
    [
        # basic dicts
        (False, {"foo": 1}, {"foo": 1}),
        (True, {"foo": 1}, {"foo": 1}),
        # containing a UUID (stringifies)
        (True, {"foo": uuid.UUID(int=1)}, {"foo": str(uuid.UUID(int=1))}),
        (False, {"foo": uuid.UUID(int=1)}, {"foo": str(uuid.UUID(int=1))}),
        # containing MISSING (removes)
        (True, {"foo": MISSING}, {}),
        (False, {"foo": MISSING}, {}),
        # nested payload wrappers (get dictified / "unwrapped")
        (
            True,
            {"bar": Payload(foo=1), "baz": [2, Payload(foo=1)]},
            {"bar": {"foo": 1}, "baz": [2, {"foo": 1}]},
        ),
        # document with UUIDs and tuples buried inside nested structures
        (
            True,
            {"foo": ({"bar": uuid.UUID(int=2)},)},
            {"foo": [{"bar": str(uuid.UUID(int=2))}]},
        ),
    ],
)
def test_json_encoder_payload_preparation(
    using_payload_type, payload_contents, expected_data
):
    encoder = JSONRequestEncoder()
    x = Payload() if using_payload_type else {}
    for k, v in payload_contents.items():
        x[k] = v
    request = encoder.encode(
        "POST",
        "http://bogus/foo",
        params={},
        data=x,
        headers={},
    )
    assert request.json == expected_data


def test_json_encoder_is_well_defined_on_array_containing_missing():
    # this is a test for a behavior which is publicly undefined
    # (we do not advertise or encourage its use)
    #
    # it ensures that we will not crash and will behave "reasonably" in this situation
    encoder = JSONRequestEncoder()
    x = [None, 1, MISSING, 0]
    request = encoder.encode(
        "POST",
        "http://bogus/foo",
        params={},
        data=x,
        headers={},
    )
    assert request.json == [None, 1, 0]


@pytest.mark.parametrize(
    "using_payload_type, payload_contents, expected_data",
    [
        # basic dicts
        (True, {"foo": 1}, {"foo": 1}),
        (False, {"foo": 1}, {"foo": 1}),
        # containing a UUID (stringifies)
        (True, {"foo": uuid.UUID(int=1)}, {"foo": str(uuid.UUID(int=1))}),
        (False, {"foo": uuid.UUID(int=1)}, {"foo": str(uuid.UUID(int=1))}),
        # containing MISSING (removes)
        (True, {"foo": MISSING}, {}),
        (False, {"foo": MISSING}, {}),
    ],
)
def test_form_encoder_payload_preparation(
    using_payload_type, payload_contents, expected_data
):
    encoder = FormRequestEncoder()
    x = Payload() if using_payload_type else {}
    for k, v in payload_contents.items():
        x[k] = v
    request = encoder.encode(
        "POST",
        "http://bogus/foo",
        params={},
        data=x,
        headers={},
    )
    assert request.data == expected_data
