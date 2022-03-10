import logging
import urllib.parse
from typing import Any, Dict, Optional, Type, Union

from globus_sdk import config, exc, utils
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.paging import PaginatorTable
from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.scopes import ScopeBuilder
from globus_sdk.transport import RequestsTransport

log = logging.getLogger(__name__)


class BaseClient:
    r"""
    Abstract base class for clients with error handling for Globus APIs.

    :param authorizer: A ``GlobusAuthorizer`` which will generate Authorization headers
    :type authorizer: :class:`GlobusAuthorizer\
        <globus_sdk.authorizers.base.GlobusAuthorizer>`
    :param app_name: Optional "nice name" for the application. Has no bearing on the
        semantics of client actions. It is just passed as part of the User-Agent
        string, and may be useful when debugging issues with the Globus Team
    :type app_name: str
    :param transport_params: Options to pass to the transport for this client
    :type transport_params: dict

    All other parameters are for internal use and should be ignored.
    """
    # service name is used to lookup a service URL from config
    service_name: str = "_base"
    # path under the client base URL
    base_path: str = "/"

    #: the class for errors raised by this client on HTTP 4xx and 5xx errors
    #: this can be set in subclasses, but must always be a subclass of GlobusError
    error_class: Type[exc.GlobusAPIError] = exc.GlobusAPIError

    #: the type of Transport which will be used, defaults to ``RequestsTransport``
    transport_class: Type[RequestsTransport] = RequestsTransport

    #: the scopes for this client may be present as a ``ScopeBuilder``
    scopes: Optional[ScopeBuilder] = None

    def __init__(
        self,
        *,
        environment: Optional[str] = None,
        base_url: Optional[str] = None,
        authorizer: Optional[GlobusAuthorizer] = None,
        app_name: Optional[str] = None,
        transport_params: Optional[Dict[str, Any]] = None,
    ):
        # explicitly check the `service_name` to ensure that it was set
        #
        # unfortunately, we can't rely on declaring BaseClient as an ABC because it
        # doesn't have any abstract methods
        #
        # if we declare `service_name` without a value, we get AttributeError on access
        # instead of the (desired) TypeError when instantiating a BaseClient because
        # it's abstract
        if self.service_name == "_base":
            raise NotImplementedError(
                "Cannot instantiate clients which do not set a 'service_name'"
            )
        log.info(
            f'Creating client of type {type(self)} for service "{self.service_name}"'
        )

        # if an environment was passed, it will be used, but otherwise lookup
        # the env var -- and in the special case of `production` translate to
        # `default`, regardless of the source of that value
        # logs the environment when it isn't `default`
        self.environment = config.get_environment_name(environment)

        self.transport = self.transport_class(**(transport_params or {}))
        log.debug(f"initialized transport of type {type(self.transport)}")

        self.base_url = utils.slash_join(
            config.get_service_url(self.service_name, environment=self.environment)
            if base_url is None
            else base_url,
            self.base_path,
        )

        self.authorizer = authorizer

        # set application name if given
        self._app_name = None
        if app_name is not None:
            self.app_name = app_name

        # setup paginated methods
        self.paginated = PaginatorTable(self)

    @property
    def app_name(self) -> Optional[str]:
        return self._app_name

    @app_name.setter
    def app_name(self, value: str) -> None:
        self._app_name = self.transport.user_agent = value

    @utils.classproperty
    def resource_server(cls) -> Optional[str]:
        """
        The resource_server name for the API and scopes associated with this client.

        This information is pulled from the ``scopes`` attribute of the client class.
        If the client does not have associated scopes, this value will be ``None``.
        """
        if cls.scopes is None:
            return None
        return cls.scopes.resource_server

    def get(
        self,
        path: str,
        *,
        query_params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> GlobusHTTPResponse:
        """
        Make a GET request to the specified path.

        See :py:meth:`~.BaseClient.request` for details on the various parameters.

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        log.debug(f"GET to {path} with query_params {query_params}")
        return self.request("GET", path, query_params=query_params, headers=headers)

    def post(
        self,
        path: str,
        *,
        query_params: Optional[Dict[str, Any]] = None,
        data: Union[None, Dict[str, Any], utils.PayloadWrapper] = None,
        headers: Optional[Dict[str, str]] = None,
        encoding: Optional[str] = None,
    ) -> GlobusHTTPResponse:
        """
        Make a POST request to the specified path.

        See :py:meth:`~.BaseClient.request` for details on the various parameters.

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        log.debug(f"POST to {path} with query_params {query_params}")
        return self.request(
            "POST",
            path,
            query_params=query_params,
            data=data,
            headers=headers,
            encoding=encoding,
        )

    def delete(
        self,
        path: str,
        *,
        query_params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> GlobusHTTPResponse:
        """
        Make a DELETE request to the specified path.

        See :py:meth:`~.BaseClient.request` for details on the various parameters.

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        log.debug(f"DELETE to {path} with query_params {query_params}")
        return self.request("DELETE", path, query_params=query_params, headers=headers)

    def put(
        self,
        path: str,
        *,
        query_params: Optional[Dict[str, Any]] = None,
        data: Union[None, Dict[str, Any], utils.PayloadWrapper] = None,
        headers: Optional[Dict[str, str]] = None,
        encoding: Optional[str] = None,
    ) -> GlobusHTTPResponse:
        """
        Make a PUT request to the specified path.

        See :py:meth:`~.BaseClient.request` for details on the various parameters.

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        log.debug(f"PUT to {path} with query_params {query_params}")
        return self.request(
            "PUT",
            path,
            query_params=query_params,
            data=data,
            headers=headers,
            encoding=encoding,
        )

    def patch(
        self,
        path: str,
        *,
        query_params: Optional[Dict[str, Any]] = None,
        data: Union[None, Dict[str, Any], utils.PayloadWrapper] = None,
        headers: Optional[Dict[str, str]] = None,
        encoding: Optional[str] = None,
    ) -> GlobusHTTPResponse:
        """
        Make a PATCH request to the specified path.

        See :py:meth:`~.BaseClient.request` for details on the various parameters.

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        log.debug(f"PATCH to {path} with query_params {query_params}")
        return self.request(
            "PATCH",
            path,
            query_params=query_params,
            data=data,
            headers=headers,
            encoding=encoding,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        query_params: Optional[Dict[str, Any]] = None,
        data: Union[None, Dict[str, Any], utils.PayloadWrapper] = None,
        headers: Optional[Dict[str, str]] = None,
        encoding: Optional[str] = None,
    ) -> GlobusHTTPResponse:
        """
        Send an HTTP request

        :param method: HTTP request method, as an all caps string
        :type method: str
        :param path: Path for the request, with or without leading slash
        :type path: str
        :param query_params: Parameters to be encoded as a query string
        :type query_params: dict, optional
        :param headers: HTTP headers to add to the request
        :type headers: dict
        :param data: Data to send as the request body. May pass through encoding.
        :type data: dict or str
        :param encoding: A way to encode request data. "json", "form", and "text"
            are all valid values. Custom encodings can be used only if they are
            registered with the transport. By default, strings get "text" behavior and
            all other objects get "json".
        :type encoding: str

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object

        :raises GlobusAPIError: a `GlobusAPIError` will be raised if the response to the
            request is received and has a status code in the 4xx or 5xx categories
        """
        # prepare data...
        # copy headers if present
        rheaders = {**headers} if headers else {}

        # if a client is asked to make a request against a full URL, not just the path
        # component, then do not resolve the path, simply pass it through as the URL
        if path.startswith("https://") or path.startswith("http://"):
            url = path
        else:
            url = utils.slash_join(self.base_url, urllib.parse.quote(path))

        # make the request
        log.debug("request will hit URL: %s", url)
        r = self.transport.request(
            method=method,
            url=url,
            data=data.data if isinstance(data, utils.PayloadWrapper) else data,
            query_params=query_params,
            headers=rheaders,
            encoding=encoding,
            authorizer=self.authorizer,
        )
        log.debug("request made to URL: %s", r.url)

        if 200 <= r.status_code < 400:
            log.debug(f"request completed with response code: {r.status_code}")
            return GlobusHTTPResponse(r, self)

        log.debug(f"request completed with (error) response code: {r.status_code}")
        raise self.error_class(r)
