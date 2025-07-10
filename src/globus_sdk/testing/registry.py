from __future__ import annotations

import importlib
import re
import typing as t

import responses

import globus_sdk

from .models import RegisteredResponse, ResponseList, ResponseSet

# matches "V2", "V11", etc as a string suffix
# see usage in _resolve_qualname for details
_SUFFIX_VERSION_MATCH_PATTERN = re.compile(r"V\d+$")

_RESPONSE_SET_REGISTRY: dict[t.Any, ResponseSet] = {}


def register_response_set(
    set_id: t.Any,
    rset: ResponseSet | dict[str, dict[str, t.Any]],
    metadata: dict[str, t.Any] | None = None,
) -> ResponseSet:
    """
    Register a new ``ResponseSet`` object.

    The response set may be specified as a dict or a ResponseSet object.

    :param set_id: The ID used to retrieve the response set later
    :param rset: The response set to register
    :param metadata: Metadata dict to assign to the response set when it is specified
        as a dict. If the response set is an object, this argument is ignored.
    """
    if isinstance(rset, dict):
        rset = ResponseSet.from_dict(rset, metadata=metadata)
    _RESPONSE_SET_REGISTRY[set_id] = rset
    return rset


def _resolve_qualname(name: str) -> str:
    if "." not in name:
        return name
    prefix, suffix = name.split(".", 1)
    if not hasattr(globus_sdk, prefix):
        return name

    # something from globus_sdk, could be a client class
    maybe_client = getattr(globus_sdk, prefix)

    # there are a dozen ways of writing this check, but the point is
    # "if it's not a client class"
    if not (
        isinstance(maybe_client, type)
        and issubclass(maybe_client, globus_sdk.BaseClient)
    ):
        return name

    assert issubclass(maybe_client, globus_sdk.BaseClient)
    service_name = maybe_client.service_name

    # TODO: Consider alternative strategies for mapping versioned clients
    # to subdirs. For now, we do it by name matching.
    #
    # 'prefix' is the client name, and it may end in `V2`, `V3`, etc.
    # in which case we want to map it to a subdir
    suffix_version_match = _SUFFIX_VERSION_MATCH_PATTERN.search(prefix)
    if suffix_version_match:
        suffix = f"{suffix_version_match.group(0).lower()}.{suffix}"

    return f"{service_name}.{suffix}"


def get_response_set(set_id: t.Any) -> ResponseSet:
    """
    Lookup a ``ResponseSet`` as in ``load_response_set``, but without
    activating it.

    :param set_id: The ID used to retrieve the response set. Typically a string, but
        could be any key used to register a response set.
    """
    # first priority: check the explicit registry
    if set_id in _RESPONSE_SET_REGISTRY:
        return _RESPONSE_SET_REGISTRY[set_id]

    # if ID is a string, it's the (optionally dotted) name of a module
    if isinstance(set_id, str):
        module_name = f"globus_sdk._testing.data.{set_id}"
    else:
        assert hasattr(
            set_id, "__qualname__"
        ), f"cannot load response set from {type(set_id)}"
        # support modules like
        #   globus_sdk/_testing/data/auth/get_identities.py
        # for lookups like
        #   get_response_set(AuthClient.get_identities)
        module_name = (
            f"globus_sdk._testing.data.{_resolve_qualname(set_id.__qualname__)}"
        )

    # after that, check the built-in "registry" built from modules
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        raise ValueError(f"no fixtures defined for {module_name}") from e
    assert isinstance(module.RESPONSES, ResponseSet)
    return module.RESPONSES


def load_response_set(
    set_id: t.Any, *, requests_mock: responses.RequestsMock | None = None
) -> ResponseSet:
    """
    Optionally lookup a response set and activate all of its responses. If
    passed a ``ResponseSet``, activate it, otherwise the first argument is an
    ID used for lookup.

    :param set_id: The ID used to retrieve the response set. Typically a string, but
        could be any key used to register a response set.
    :param requests_mock: A ``responses`` library mock to use for response mocking,
        defaults to the ``responses`` default
    """
    if isinstance(set_id, ResponseSet):
        return set_id.activate_all(requests_mock=requests_mock)
    ret = get_response_set(set_id)
    ret.activate_all(requests_mock=requests_mock)
    return ret


def load_response(
    set_id: t.Any,
    *,
    case: str = "default",
    requests_mock: responses.RequestsMock | None = None,
) -> RegisteredResponse | ResponseList:
    """
    Optionally lookup and activate an individual response. If given a
    ``RegisteredResponse``, activate it, otherwise the first argument is an ID
    of a ``ResponseSet`` used for lookup. By default, looks for the response
    registered under ``case="default"``.

    :param set_id: The ID used to retrieve the response set. Typically a string, but
        could be any key used to register a response set.
    :param case: The name of a case within the response set to load, ignoring all other
        registered mocks in the response set
    :param requests_mock: A ``responses`` library mock to use for response mocking,
        defaults to the ``responses`` default
    """
    if isinstance(set_id, RegisteredResponse):
        return set_id.add(requests_mock=requests_mock)
    rset = get_response_set(set_id)
    return rset.activate(case, requests_mock=requests_mock)
