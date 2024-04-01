import inspect
import os

import responses

from globus_sdk import utils


def register_api_route_fixture_file(service, path, filename, **kwargs):
    """
    register an API route to serve the contents of a file, given the name of
    that file in a `fixture_data` directory, adjacent to the current (calling)
    module

    i.e. in a dir like this:
      path/to/tests
      ├── test_mod.py
      └── fixture_data
          └── dat.txt

    you can call
    >>> register_api_route_fixture_file('transfer', '/foo', 'dat.txt')

    in `test_mod.py`

    it will "do the right thing" and find the abspath to dat.txt , and
    load the contents of that file as the response for '/foo'
    """
    # get calling frame
    frm = inspect.stack()[1]
    # get filename from frame, make it absolute
    modpath = os.path.abspath(frm[1])

    abspath = os.path.join(os.path.dirname(modpath), "fixture_data", filename)
    with open(abspath, "rb") as f:
        body = f.read()

    register_api_route(service, path, body=body, **kwargs)


def register_api_route(
    service, path, method=responses.GET, adding_headers=None, replace=False, **kwargs
):
    """
    Handy wrapper for adding URIs to the response mock state.
    """
    base_url_map = {
        "auth": "https://auth.globus.org/",
        "nexus": "https://nexus.api.globusonline.org/",
        "groups": "https://groups.api.globus.org/",
        "transfer": "https://transfer.api.globus.org/v0.10",
        "search": "https://search.api.globus.org/",
        "gcs": "https://abc.xyz.data.globus.org/api/",
    }
    assert service in base_url_map
    base_url = base_url_map.get(service)
    full_url = utils.slash_join(base_url, path)

    # can set it to `{}` explicitly to clear the default
    if adding_headers is None:
        adding_headers = {"Content-Type": "application/json"}

    if replace:
        responses.replace(
            method, full_url, headers=adding_headers, match_querystring=None, **kwargs
        )
    else:
        responses.add(
            method, full_url, headers=adding_headers, match_querystring=None, **kwargs
        )
