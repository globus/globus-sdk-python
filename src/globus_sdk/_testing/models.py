import typing as t

import responses

from ..utils import slash_join


class RegisteredResponse:
    _url_map = {
        "auth": "https://auth.globus.org/",
        "nexus": "https://nexus.api.globusonline.org/",
        "transfer": "https://transfer.api.globus.org/v0.10",
        "search": "https://search.api.globus.org/",
        "gcs": "https://abc.xyz.data.globus.org/api",
        "groups": "https://groups.api.globus.org/v2/",
        "timer": "https://timer.automate.globus.org/",
        "flows": "https://flows.automate.globus.org/",
    }

    def __init__(
        self,
        *,
        path: str,
        service: t.Optional[str] = None,
        method: str = responses.GET,
        headers: t.Optional[t.Dict[str, str]] = None,
        metadata: t.Optional[t.Dict[str, t.Any]] = None,
        json: t.Union[None, t.List[t.Any], t.Dict[str, t.Any]] = None,
        body: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> None:
        self.service = service
        self.path = path
        if service:
            self.full_url = slash_join(self._url_map[service], path)
        else:
            self.full_url = path

        # convert the method to uppercase so that specifying `method="post"` will match
        # correctly -- method matching is case sensitive but we don't need to expose the
        # possibility of a non-uppercase method
        self.method = method.upper()
        self.json = json
        self.body = body

        if headers is None:
            headers = {"Content-Type": "application/json"}
        self.headers = headers

        self._metadata = metadata
        self.kwargs = kwargs

        self.parent: t.Union["ResponseSet", "ResponseList", None] = None

    @property
    def metadata(self) -> t.Dict[str, t.Any]:
        if self._metadata is not None:
            return self._metadata
        if self.parent is not None:
            return self.parent.metadata
        return {}

    def add(
        self, *, requests_mock: t.Optional[responses.RequestsMock] = None
    ) -> "RegisteredResponse":
        kwargs: t.Dict[str, t.Any] = {
            "headers": self.headers,
            "match_querystring": None,
            **self.kwargs,
        }
        if self.json is not None:
            kwargs["json"] = self.json
        if self.body is not None:
            kwargs["body"] = self.body

        if requests_mock is None:
            responses.add(self.method, self.full_url, **kwargs)
        else:
            requests_mock.add(self.method, self.full_url, **kwargs)
        return self


class ResponseList:
    """
    A series of unnamed responses, meant to be used and referred to as a single case
    within a ResponseSet.
    """

    def __init__(
        self,
        *data: RegisteredResponse,
        metadata: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        self.responses = list(data)
        self._metadata = metadata
        self.parent: t.Optional["ResponseSet"] = None
        for r in data:
            r.parent = self

    @property
    def metadata(self) -> t.Dict[str, t.Any]:
        if self._metadata is not None:
            return self._metadata
        if self.parent is not None:
            return self.parent.metadata
        return {}

    def add(
        self, *, requests_mock: t.Optional[responses.RequestsMock] = None
    ) -> "ResponseList":
        for r in self.responses:
            r.add(requests_mock=requests_mock)
        return self


class ResponseSet:
    """
    A collection of responses. On init, this implicitly sets the parent of
    any response objects to this response set. On register() it does not do
    so automatically.
    """

    def __init__(
        self,
        metadata: t.Optional[t.Dict[str, t.Any]] = None,
        **kwargs: t.Union[RegisteredResponse, ResponseList],
    ) -> None:
        self.metadata = metadata or {}
        self._data: t.Dict[str, t.Union[RegisteredResponse, ResponseList]] = {**kwargs}
        for res in self._data.values():
            res.parent = self

    def register(self, case: str, value: RegisteredResponse) -> None:
        self._data[case] = value

    def lookup(self, case: str) -> t.Union[RegisteredResponse, ResponseList]:
        try:
            return self._data[case]
        except KeyError as e:
            raise Exception("did not find a matching registered response") from e

    def __bool__(self) -> bool:
        return bool(self._data)

    def __iter__(
        self,
    ) -> t.Iterator[t.Union[RegisteredResponse, ResponseList]]:
        return iter(self._data.values())

    def activate(
        self, case: str, *, requests_mock: t.Optional[responses.RequestsMock] = None
    ) -> t.Union[RegisteredResponse, ResponseList]:
        return self.lookup(case).add(requests_mock=requests_mock)

    def activate_all(
        self, *, requests_mock: t.Optional[responses.RequestsMock] = None
    ) -> "ResponseSet":
        for x in self:
            x.add(requests_mock=requests_mock)
        return self

    @classmethod
    def from_dict(
        cls,
        data: t.Mapping[str, t.Union[t.Dict[str, t.Any], t.List[t.Dict[str, t.Any]]]],
        metadata: t.Optional[t.Dict[str, t.Any]] = None,
        **kwargs: t.Dict[str, t.Dict[str, t.Any]],
    ) -> "ResponseSet":
        # constructor which expects native dicts and converts them to RegisteredResponse
        # objects, then puts them into the ResponseSet
        def handle_value(
            v: t.Union[t.Dict[str, t.Any], t.List[t.Dict[str, t.Any]]]
        ) -> t.Union[RegisteredResponse, ResponseList]:
            if isinstance(v, dict):
                return RegisteredResponse(**v)
            else:
                return ResponseList(*(RegisteredResponse(**subv) for subv in v))

        reassembled_data: t.Dict[str, t.Union[RegisteredResponse, ResponseList]] = {
            k: handle_value(v) for k, v in data.items()
        }
        return cls(metadata=metadata, **reassembled_data)
