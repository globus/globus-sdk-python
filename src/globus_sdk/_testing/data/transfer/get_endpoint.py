from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import ENDPOINT_ID

ENDPOINT_DOC = {
    "DATA_TYPE": "endpoint",
    "id": ENDPOINT_ID,
    "display_name": "myserver",
    "organization": "My Org",
    "username": "auser",
    "description": "Example gridftp endpoint.",
    "entity_type": "GCSv4_host",
    "public": False,
    "french_english_bilingual": False,
    "is_globus_connect": False,
    "globus_connect_setup_key": None,
    "gcp_connected": None,
    "gcp_paused": None,
    "s3_url": None,
    "s3_owner_activated": False,
    "host_endpoint_id": None,
    "host_path": None,
    "disable_verify": False,
    "disable_anonymous_writes": False,
    "force_verify": False,
    "force_encryption": False,
    "mfa_required": False,
    "myproxy_server": None,
    "myproxy_dn": None,
    "non_functional": False,
    "non_functional_endpoint_display_name": None,
    "non_functional_endpoint_id": None,
    "oauth_server": None,
    "default_directory": None,
    "activated": False,
    "expires_in": 0,
    "expire_time": "2000-01-02 03:45:06+00:00",
    "shareable": True,
    "acl_available": False,
    "acl_editable": False,
    "in_use": False,
    "DATA": [
        {
            "DATA_TYPE": "server",
            "hostname": "gridftp.example.org",
            "uri": "gsiftp://gridftp.example.org:2811",
            "port": 2811,
            "scheme": "gsiftp",
            "id": 985,
            "subject": "/O=Grid/OU=Example/CN=host/gridftp.example.org",
        }
    ],
}


RESPONSES = ResponseSet(
    metadata={"endpoint_id": ENDPOINT_ID},
    default=RegisteredResponse(
        service="transfer",
        path=f"/endpoint/{ENDPOINT_ID}",
        json=ENDPOINT_DOC,
    ),
)
