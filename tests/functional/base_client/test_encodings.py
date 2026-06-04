from __future__ import annotations

import typing as t

import pytest
import requests
import responses

import globus_sdk
from globus_sdk.transport import RequestEncoder, RequestsTransport
from globus_sdk.transport.representation_providers import (
    RequestsJsonProvider,
    RequestsRepresentationProvider,
)
from tests.common import fast_json


def test_cannot_encode_dict_as_text(client):
    with pytest.raises(TypeError):
        client.post("/bar", data={"baz": 1}, encoding="text")


def test_cannot_encode_with_unknown_encoding(client):
    with pytest.raises(ValueError):
        client.post("/bar", data={"baz": 1}, encoding="some-random-string")


def test_cannot_form_encode_bad_types(client):
    with pytest.raises(TypeError):
        client.post("/bar", data=["baz", "buzz"], encoding="form")
    with pytest.raises(TypeError):
        client.post("/bar", data=1, encoding="form")


def test_form_encoding_works(client):
    responses.add(responses.POST, "https://foo.api.globus.org/bar", body="hi")
    client.post("/bar", data={"baz": 1}, encoding="form")

    last_req = responses.calls[-1].request
    assert last_req.body == "baz=1"


def test_text_encoding_sends_ascii_string(client):
    responses.add(responses.POST, "https://foo.api.globus.org/bar", body="hi")
    client.post("/bar", data="baz", encoding="text")

    last_req = responses.calls[-1].request
    assert last_req.body == "baz"


def test_text_encoding_can_send_non_ascii_utf8_bytes(client):
    # this test is a reproducer for an issue in which attempting to send these bytes
    # in the form of a (decoded) string would fail, as urllib3 tried to encode them as
    # latin-1 bytes incorrectly
    # passing the bytes already UTF-8 encoded should work
    responses.add(responses.POST, "https://foo.api.globus.org/bar", body="hi")
    client.post("/bar", data='{"field“: "value“}'.encode(), encoding="text")

    last_req = responses.calls[-1].request
    assert last_req.body == '{"field“: "value“}'.encode()


@pytest.mark.parametrize(
    "provider_base_class", (RequestEncoder, RequestsRepresentationProvider)
)
def test_can_configure_custom_encoding(client_class, provider_base_class):
    class MyRequestEncoder(provider_base_class):
        def encode(
            self,
            method: str,
            url: str,
            params: dict[str, t.Any] | None,
            data: t.Any,
            headers: dict[str, str],
        ) -> requests.Request:
            if data is not None:
                headers = {"Content-Type": "application/json", **headers}

            return requests.Request(
                method,
                url,
                json={"foo": self._prepare_data(data)},
                params=self._prepare_params(params),
                headers=self._prepare_headers(headers),
            )

    my_transport = RequestsTransport()
    my_transport.representation_providers["myjson"] = MyRequestEncoder()
    client = client_class(transport=my_transport)

    responses.add(responses.POST, "https://foo.api.globus.org/bar", body="hi")
    client.post("/bar", data={"baz": 1}, encoding="myjson")

    my_transport.close()

    last_req = responses.calls[-1].request
    assert fast_json.loads(last_req.body) == {"foo": {"baz": 1}}


def test_can_configure_custom_decoding(client_class):
    class MyProvider(RequestsJsonProvider):
        def decode_body(self, response: requests.Response) -> t.Any:
            return {"a": "clever-cultural-reference-goes-here"}

    my_transport = RequestsTransport()
    my_transport.json_provider = MyProvider()
    client = client_class(transport=my_transport)

    responses.add(responses.POST, "https://foo.api.globus.org/bar", body="hi")
    response = client.post("/bar", data={"baz": 1})

    my_transport.close()

    # the raw text is available
    assert response.text == "hi"
    # but the decoded data is whatever the decoder says
    assert response.data == {"a": "clever-cultural-reference-goes-here"}


def test_custom_decoding_applies_to_errors(client_class):
    class MyProvider(RequestsJsonProvider):
        def decode_body(self, response: requests.Response) -> t.Any:
            return {"a": "clever-cultural-reference-goes-here"}

    my_transport = RequestsTransport()
    my_transport.json_provider = MyProvider()
    client = client_class(transport=my_transport)

    responses.add(
        responses.POST,
        "https://foo.api.globus.org/bar",
        body="bye",
        status=404,
        content_type="application/json",
    )
    with pytest.raises(globus_sdk.GlobusAPIError) as excinfo:
        client.post("/bar", data={"baz": 1})

    my_transport.close()

    err = excinfo.value

    # the raw text is available
    assert err.text == "bye"
    # but the decoded data is whatever the decoder says
    assert err.raw_json == {"a": "clever-cultural-reference-goes-here"}
