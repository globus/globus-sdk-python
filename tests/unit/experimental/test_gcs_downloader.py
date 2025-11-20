import uuid
from unittest import mock

import pytest
import responses

import globus_sdk
from globus_sdk.experimental.gcs_downloader import GCSDownloader


def test_collection_id_sniffing():
    file_url = "https://some-base-url.example.com/bogus.txt"
    client_id = str(uuid.UUID(int=3))

    responses.add(
        method="GET",
        url=file_url,
        status=302,
        headers={
            "Location": f"https://auth.globus.org/authenticate?client_id={client_id}"
        },
    )

    downloader = GCSDownloader(app=mock.Mock())
    assert downloader._sniff_collection_id(file_url) == client_id


@pytest.mark.parametrize(
    "entity_type", ("GCSv5_mapped_collection", "GCSv5_guest_collection")
)
@pytest.mark.parametrize("high_assurance", (True, False))
def test_scope_detection(entity_type, high_assurance):
    collection_id = str(uuid.UUID(int=8))
    scopes = globus_sdk.scopes.GCSCollectionScopes(collection_id)

    transfer_client = mock.Mock()
    transfer_client.get_endpoint.return_value = {
        "entity_type": entity_type,
        "high_assurance": high_assurance,
    }

    downloader = GCSDownloader(mock.Mock(), transfer_client=transfer_client)

    result = downloader._detect_scopes(collection_id)
    if "mapped" in entity_type and not high_assurance:
        assert {str(s) for s in result} == {str(scopes.https), str(scopes.data_access)}
    else:
        assert {str(s) for s in result} == {str(scopes.https)}
