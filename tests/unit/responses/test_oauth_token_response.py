import pytest


def test_by_resource_server_lookups(oauth_token_response):
    by_rs = oauth_token_response.by_resource_server

    # things which should hold for all
    for n in (1, 2, 3):
        name = f"resource_server_{n}"
        for attr in ("access_token", "refresh_token", "resource_server"):
            assert by_rs[name][attr] == f"{attr}_{n}"

        assert "expires_in" not in by_rs[name]
        assert "expires_at_seconds" in by_rs[name]

        assert by_rs[name]["token_type"] == "bearer"

    assert by_rs["resource_server_1"]["scope"] == "scope1"
    assert by_rs["resource_server_2"]["scope"] == "scope2 scope2:0 scope2:1"
    assert by_rs["resource_server_3"]["scope"] == "scope3:0 scope3:1"


@pytest.mark.parametrize(
    "scopestr, resource_server",
    [
        ("scope1", "resource_server_1"),
        ("scope2 scope2:0 scope2:1", "resource_server_2"),
        ("scope3:0 scope3:1", "resource_server_3"),
    ],
)
def test_by_scopes_lookups_simple(scopestr, resource_server, oauth_token_response):
    by_scopes = oauth_token_response.by_scopes

    # containment
    assert scopestr in by_scopes
    for x in scopestr.split():
        assert x in by_scopes

    # maps correctly
    assert by_scopes[scopestr]["resource_server"] == resource_server


def test_by_scopes_lookups_failures(oauth_token_response):
    by_scopes = oauth_token_response.by_scopes

    mixed_scopes = "scope1 scope2"

    # containment
    assert mixed_scopes not in by_scopes
    assert "badscope" not in by_scopes

    # try to actually do it, ensure KeyErrors have good messages
    with pytest.raises(KeyError) as excinfo:
        by_scopes[mixed_scopes]
    assert "did not match exactly one token" in str(excinfo.value)

    with pytest.raises(KeyError) as excinfo:
        by_scopes["badscope"]
    assert "was not found" in str(excinfo.value)


def test_by_scopes_lookups_fancy(oauth_token_response):
    by_scopes = oauth_token_response.by_scopes

    # repeated scope
    assert by_scopes["scope3:0 scope3:0"]["resource_server"] == "resource_server_3"

    # not matching order from original document
    assert (
        by_scopes["scope2:1 scope2 scope2:0"]["resource_server"] == "resource_server_2"
    )


def test_stringify(oauth_token_response):
    data = str(oauth_token_response)
    # it starts the right way
    assert data.startswith("OAuthTokenResponse:\n")
    # it contains the id_token, but heavily truncated and annotated as such
    assert "  id_token: id_token_v... (truncated)\n" in data
    # it contains the by_resource_server mapping (but we won't assert anything about
    # that data other than that it starts with a '{')
    assert "  by_resource_server:\n    {" in data
