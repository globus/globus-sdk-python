import importlib
import typing as t

import responses

import globus_sdk

from .models import RegisteredResponse, ResponseList, ResponseSet

_RESPONSE_SET_REGISTRY: t.Dict[t.Any, ResponseSet] = {}


def register_response_set(
    set_id: t.Any,
    rset: t.Union[ResponseSet, t.Dict[str, t.Dict[str, t.Any]]],
    metadata: t.Optional[t.Dict[str, t.Any]] = None,
) -> ResponseSet:
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
    return f"{service_name}.{suffix}"


def get_response_set(set_id: t.Any) -> ResponseSet:
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
    set_id: t.Any, *, requests_mock: t.Optional[responses.RequestsMock] = None
) -> ResponseSet:
    if isinstance(set_id, ResponseSet):
        return set_id.activate_all(requests_mock=requests_mock)
    ret = get_response_set(set_id)
    ret.activate_all(requests_mock=requests_mock)
    return ret


def load_response(
    set_id: t.Any,
    *,
    case: str = "default",
    requests_mock: t.Optional[responses.RequestsMock] = None,
) -> t.Union[RegisteredResponse, ResponseList]:
    if isinstance(set_id, RegisteredResponse):
        return set_id.add(requests_mock=requests_mock)
    rset = get_response_set(set_id)
    return rset.activate(case, requests_mock=requests_mock)
