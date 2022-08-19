from typing import Any, Dict, Iterator, List, Optional, Union

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
        service: Optional[str] = None,
        method: str = responses.GET,
        headers: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        json: Union[None, List[Any], Dict[str, Any]] = None,
        body: Optional[str] = None,
        **kwargs: Any,
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

        self.parent: Optional["ResponseSet"] = None

    @property
    def metadata(self) -> Dict[str, Any]:
        if self._metadata is not None:
            return self._metadata
        if self.parent is not None:
            return self.parent.metadata
        return {}

    def add(
        self, *, requests_mock: Optional[responses.RequestsMock] = None
    ) -> "RegisteredResponse":
        kwargs: Dict[str, Any] = {
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


class ResponseSet:
    """
    A collection of responses. On init, this implicitly sets the parent of
    any response objects to this response set. On register() it does not do
    so automatically.
    """

    def __init__(
        self,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: RegisteredResponse,
    ) -> None:
        self.metadata = metadata or {}
        self._data: Dict[str, RegisteredResponse] = {**kwargs}
        for res in self._data.values():
            res.parent = self

    def register(self, case: str, value: RegisteredResponse) -> None:
        self._data[case] = value

    def lookup(self, case: str) -> RegisteredResponse:
        try:
            return self._data[case]
        except KeyError as e:
            raise Exception("did not find a matching registered response") from e

    def __bool__(self) -> bool:
        return bool(self._data)

    def __iter__(self) -> Iterator[RegisteredResponse]:
        return iter(self._data.values())

    def activate(
        self, case: str, *, requests_mock: Optional[responses.RequestsMock] = None
    ) -> RegisteredResponse:
        return self.lookup(case).add(requests_mock=requests_mock)

    def activate_all(
        self, *, requests_mock: Optional[responses.RequestsMock] = None
    ) -> "ResponseSet":
        for x in self:
            x.add(requests_mock=requests_mock)
        return self

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Dict[str, Dict[str, Any]],
    ) -> "ResponseSet":
        # constructor which expects native dicts and converts them to RegisteredResponse
        # objects, then puts them into the ResponseSet
        return cls(
            metadata=metadata, **{k: RegisteredResponse(**v) for k, v in data.items()}
        )
