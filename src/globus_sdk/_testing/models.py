from __future__ import annotations

import types
import typing as t

import responses

from globus_sdk._utils import slash_join


class RegisteredResponse:
    """
    A mock response along with descriptive metadata to let a fixture "pass data
    forward" to the consuming test cases. (e.g. a ``GET Task`` fixture which
    shares the ``task_id`` it uses with consumers via ``.metadata["task_id"]``)

    When initializing a ``RegisteredResponse``, you can use ``path`` and ``service``
    to describe a path on a Globus service rather than a full URL. The ``metadata``
    data container is also globus-sdk specific. Most other parameters are wrappers
    over ``responses`` response characteristics.

    :param path: Path on the target service or full URL if service is null
    :param service: A known service name like ``"transfer"`` or ``"compute"``. This will
        be used to deduce the base URL onto which ``path`` should be joined
    :param method: A string HTTP Method
    :param headers: HTTP headers for the response
    :param json: A dict or list structure for a JSON response (mutex with ``body``)
    :param body: A string response body (mutex with ``json``)
    :param status: The HTTP status code for the response
    :param content_type: A Content-Type header value for the response
    :param match: A tuple or list of ``responses`` matchers
    :param metadata: A dict of data to store on the response, which allows the usage
        site which declares the response to pass information forward to the site which
        activates and tests against the response.
    """

    _url_map = {
        "auth": "https://auth.globus.org/",
        "nexus": "https://nexus.api.globusonline.org/",
        "transfer": "https://transfer.api.globus.org/",
        "search": "https://search.api.globus.org/",
        "gcs": "https://abc.xyz.data.globus.org/api/",
        "groups": "https://groups.api.globus.org/",
        "timer": "https://timer.automate.globus.org/",
        "flows": "https://flows.automate.globus.org/",
        "compute": "https://compute.api.globus.org/",
    }

    def __init__(
        self,
        *,
        # path and service are glbous-sdk specific
        # in `responses`, these are just `url`
        path: str,
        service: (
            t.Literal[
                "auth",
                "nexus",
                "transfer",
                "search",
                "gcs",
                "groups",
                "timer",
                "flows",
                "compute",
            ]
            | None
        ) = None,
        # method will be passed through to `responses.Response`, so we
        # support all of the values which it supports
        method: t.Literal[
            "GET",
            "PUT",
            "POST",
            "PATCH",
            "HEAD",
            "DELETE",
            "OPTIONS",
            "CONNECT",
            "TRACE",
        ] = "GET",
        # these parameters are passed through to `response.Response` (or omitted)
        body: str | None = None,
        content_type: str | None = None,
        headers: dict[str, str] | None = None,
        json: None | list[t.Any] | dict[str, t.Any] = None,
        status: int = 200,
        stream: bool | None = None,
        match: t.Sequence[t.Callable[..., tuple[bool, str]]] | None = None,
        # metadata is globus-sdk specific
        metadata: dict[str, t.Any] | None = None,
        # the following are known parameters to `responses.Response` which
        # `RegisteredResponse` does not support:
        #   - url: calculated from (path, service)
        #   - auto_calculate_content_length: a bool setting, usually not needed and can
        #                                    be achieved in user code via `headers`
        #   - passthrough: bool setting allowing calls to be emitted to the services
        #                  (undesirable in any ordinary cases)
        #   - match_querystring: legacy param which has been replaced with `match`
    ) -> None:
        self.service = service

        if service:
            self.full_url = slash_join(self._url_map[service], path)
        else:
            self.full_url = path

        self.path = path

        # convert the method to uppercase so that specifying `method="post"` will match
        # correctly -- method matching is case sensitive but we don't need to expose the
        # possibility of a non-uppercase method
        self.method = method.upper()

        self.body = body
        self.content_type = content_type
        self.headers = headers
        self.json = json
        self.status = status
        self.stream = stream

        self.match = match

        self._metadata = metadata

        self.parent: ResponseSet | ResponseList | None = None

    @property
    def metadata(self) -> dict[str, t.Any]:
        if self._metadata is not None:
            return self._metadata
        if self.parent is not None:
            return self.parent.metadata
        return {}

    def _add_or_replace(
        self,
        method: t.Literal["add", "replace"],
        *,
        requests_mock: responses.RequestsMock | None = None,
    ) -> RegisteredResponse:
        kwargs: dict[str, t.Any] = {
            "headers": self.headers,
            "status": self.status,
            "stream": self.stream,
            "match_querystring": None,
        }
        if self.json is not None:
            kwargs["json"] = self.json
        if self.body is not None:
            kwargs["body"] = self.body
        if self.content_type is not None:
            kwargs["content_type"] = self.content_type
        if self.match is not None:
            kwargs["match"] = self.match

        if requests_mock is None:
            use_requests_mock: responses.RequestsMock | types.ModuleType = responses
        else:
            use_requests_mock = requests_mock

        if method == "add":
            use_requests_mock.add(self.method, self.full_url, **kwargs)
        else:
            use_requests_mock.replace(self.method, self.full_url, **kwargs)
        return self

    def add(
        self, *, requests_mock: responses.RequestsMock | None = None
    ) -> RegisteredResponse:
        """
        Activate the response, adding it to a mocked requests object.

        :param requests_mock: The mocked requests object to use. Defaults to the default
            provided by the ``responses`` library
        """
        return self._add_or_replace("add", requests_mock=requests_mock)

    def replace(
        self, *, requests_mock: responses.RequestsMock | None = None
    ) -> RegisteredResponse:
        """
        Activate the response, adding it to a mocked requests object and replacing any
        existing response for the particular path and method.

        :param requests_mock: The mocked requests object to use. Defaults to the default
            provided by the ``responses`` library
        """
        return self._add_or_replace("replace", requests_mock=requests_mock)


class ResponseList:
    """
    A series of unnamed responses, meant to be used and referred to as a single case
    within a ResponseSet.

    This can be stored in a ``ResponseSet`` as a case, describing a series
    of responses registered to a specific name (e.g. to describe a paginated API).
    """

    def __init__(
        self,
        *data: RegisteredResponse,
        metadata: dict[str, t.Any] | None = None,
    ) -> None:
        self.responses = list(data)
        self._metadata = metadata
        self.parent: ResponseSet | None = None
        for r in data:
            r.parent = self

    @property
    def metadata(self) -> dict[str, t.Any]:
        if self._metadata is not None:
            return self._metadata
        if self.parent is not None:
            return self.parent.metadata
        return {}

    def add(
        self, *, requests_mock: responses.RequestsMock | None = None
    ) -> ResponseList:
        for r in self.responses:
            r.add(requests_mock=requests_mock)
        return self


class ResponseSet:
    """
    A collection of mock responses, potentially all meant to be activated together
    (``.activate_all()``), or to be individually selected as options/alternatives
    (``.activate("case_foo")``).

    On init, this implicitly sets the parent of any response objects to this response
    set. On register() it does not do so automatically.
    """

    def __init__(
        self,
        metadata: dict[str, t.Any] | None = None,
        **kwargs: RegisteredResponse | ResponseList,
    ) -> None:
        self.metadata = metadata or {}
        self._data: dict[str, RegisteredResponse | ResponseList] = {**kwargs}
        for res in self._data.values():
            res.parent = self

    def register(self, case: str, value: RegisteredResponse) -> None:
        self._data[case] = value

    def lookup(self, case: str) -> RegisteredResponse | ResponseList:
        try:
            return self._data[case]
        except KeyError as e:
            raise LookupError("did not find a matching registered response") from e

    def __bool__(self) -> bool:
        return bool(self._data)

    def __iter__(
        self,
    ) -> t.Iterator[RegisteredResponse | ResponseList]:
        return iter(self._data.values())

    def cases(self) -> t.Iterator[str]:
        return iter(self._data)

    def activate(
        self,
        case: str,
        *,
        requests_mock: responses.RequestsMock | None = None,
    ) -> RegisteredResponse | ResponseList:
        return self.lookup(case).add(requests_mock=requests_mock)

    def activate_all(
        self, *, requests_mock: responses.RequestsMock | None = None
    ) -> ResponseSet:
        for x in self:
            x.add(requests_mock=requests_mock)
        return self

    @classmethod
    def from_dict(
        cls,
        data: t.Mapping[
            str,
            (dict[str, t.Any] | list[dict[str, t.Any]]),
        ],
        metadata: dict[str, t.Any] | None = None,
        **kwargs: dict[str, dict[str, t.Any]],
    ) -> ResponseSet:
        # constructor which expects native dicts and converts them to RegisteredResponse
        # objects, then puts them into the ResponseSet
        def handle_value(
            v: dict[str, t.Any] | list[dict[str, t.Any]],
        ) -> RegisteredResponse | ResponseList:
            if isinstance(v, dict):
                return RegisteredResponse(**v)
            else:
                return ResponseList(*(RegisteredResponse(**subv) for subv in v))

        reassembled_data: dict[str, RegisteredResponse | ResponseList] = {
            k: handle_value(v) for k, v in data.items()
        }
        return cls(metadata=metadata, **reassembled_data)
