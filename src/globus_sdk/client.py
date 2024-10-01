from __future__ import annotations

import logging
import typing as t
import urllib.parse

from globus_sdk import config, exc, utils
from globus_sdk._types import ScopeCollectionType
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.paging import PaginatorTable
from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.scopes import Scope, ScopeBuilder
from globus_sdk.transport import RequestsTransport

if t.TYPE_CHECKING:
    from globus_sdk.globus_app import GlobusApp

log = logging.getLogger(__name__)

_DataParamType = t.Union[None, str, bytes, t.Dict[str, t.Any], utils.PayloadWrapper]


class BaseClient:
    r"""
    Abstract base class for clients with error handling for Globus APIs.

    :param app: A ``GlobusApp`` which will be used for handling authorization and
        storing and validating tokens. Passing an ``app`` will automatically include
        a client's default scopes in the ``app``'s scope requirements unless specific
        ``app_scopes`` are given. If ``app_name`` is not given, the ``app``'s
        ``app_name`` will be used. Mutually exclusive with ``authorizer``.
    :param app_scopes: Optional list of ``Scope`` objects to be added to ``app``'s
        scope requirements instead of ``default_scope_requirements``. Requires ``app``.
    :param authorizer: A ``GlobusAuthorizer`` which will generate Authorization headers.
        Mutually exclusive with ``app``.
    :param app_name: Optional "nice name" for the application. Has no bearing on the
        semantics of client actions. It is just passed as part of the User-Agent
        string, and may be useful when debugging issues with the Globus Team.
        If both``app`` and ``app_name`` are given, this value takes priority.
    :param base_url: The URL for the service. Most client types initialize this value
        intelligently by default. Set it when inheriting from BaseClient or
        communicating through a proxy.
    :param transport_params: Options to pass to the transport for this client

    All other parameters are for internal use and should be ignored.
    """

    # service name is used to lookup a service URL from config
    service_name: str = "_base"
    # path under the client base URL
    base_path: str = "/"

    #: the class for errors raised by this client on HTTP 4xx and 5xx errors
    #: this can be set in subclasses, but must always be a subclass of GlobusError
    error_class: type[exc.GlobusAPIError] = exc.GlobusAPIError

    #: the type of Transport which will be used, defaults to ``RequestsTransport``
    transport_class: type[RequestsTransport] = RequestsTransport

    #: the scopes for this client may be present as a ``ScopeBuilder``
    scopes: ScopeBuilder | None = None

    def __init__(
        self,
        *,
        environment: str | None = None,
        base_url: str | None = None,
        app: GlobusApp | None = None,
        app_scopes: list[Scope] | None = None,
        authorizer: GlobusAuthorizer | None = None,
        app_name: str | None = None,
        transport_params: dict[str, t.Any] | None = None,
    ):
        # Determine the client's environment.
        if app is not None:
            # If we're using a GlobusApp, the client's environment must either match the
            # app's or be omitted.
            if environment is not None and environment != app.config.environment:
                raise exc.GlobusSDKUsageError(
                    f"[Environment Mismatch] {type(self).__name__}'s environment "
                    f"({environment}) does not match the GlobusApp's configured "
                    f"environment ({app.config.environment})."
                )

            self.environment = app.config.environment
        else:
            # Otherwise, figure out the environment from the provided kwarg or the
            # GLOBUS_SDK_ENVIRONMENT environment variable.
            self.environment = config.get_environment_name(environment)

        if self.service_name == "_base":
            # service_name=="_base" means that either there was no inheritance (direct
            # instantiation of BaseClient), or the inheriting class operates outside of
            # the existing service_name->URL mapping paradigm
            # in these cases, base_url must be set explicitly
            log.info(f"Creating client of type {type(self)}")
            if base_url is None:
                raise NotImplementedError(
                    "Cannot instantiate clients which do not set a 'service_name' "
                    "unless they explicitly set 'base_url'."
                )
        else:
            # if service_name is set, it can be used to deduce a base_url
            # *if* necessary
            log.info(
                f"Creating client of type {type(self)} for "
                f'service "{self.service_name}"'
            )
            if base_url is None:
                base_url = config.get_service_url(
                    self.service_name, environment=self.environment
                )

        # append the base_path to the base URL
        self.base_url: str = utils.slash_join(base_url, self.base_path)

        self.transport = self.transport_class(**(transport_params or {}))
        log.debug(f"initialized transport of type {type(self.transport)}")

        if app and authorizer:
            raise exc.GlobusSDKUsageError(
                f"A {type(self).__name__} cannot use both an 'app' and an 'authorizer'."
            )

        self._app = app
        self.authorizer = authorizer

        if app_scopes and not app:
            raise exc.GlobusSDKUsageError(
                f"A {type(self).__name__} must have an 'app' to use 'app_scopes'."
            )

        self.app_scopes = app_scopes

        # set application name if available from app_name or app with app_name
        # taking precedence if both are present
        self._app_name: str | None = None
        if app_name is not None:
            self.app_name = app_name
        elif app is not None:
            self.app_name = app.app_name

        # setup paginated methods
        self.paginated = PaginatorTable(self)

        self._finalize_app()

    @property
    def default_scope_requirements(self) -> list[Scope]:
        """
        Scopes that will automatically be added to this client's app's
        scope_requirements during _finalize_app.

        For clients with static scope requirements this can just be a static
        value. Clients with dynamic requirements should use @property and must
        return sane results while the Base Client is being initialized.
        """
        raise NotImplementedError

    def _finalize_app(self) -> None:
        if self._app:
            if self.resource_server is None:
                raise ValueError(
                    "Unable to use an 'app' with a client with no "
                    "'resource_server' defined."
                )

            if self.app_scopes:
                scope_requirements = self.app_scopes
            else:
                scope_requirements = self.default_scope_requirements

            self._app.add_scope_requirements({self.resource_server: scope_requirements})

    def add_app_scope(self, scope_collection: ScopeCollectionType) -> BaseClient:
        """
        Add a given scope collection to this client's ``GlobusApp`` scope requirements
        for this client's ``resource_server``. This allows defining additional scope
        requirements beyond the client's ``default_scope_requirements``.

        Returns ``self`` for chaining.

        Raises ``GlobusSDKUsageError`` if this client was not initialized with a
            ``GlobusApp``.

        :param scope_collection: A scope or scopes of ``ScopeCollectionType`` to be
            added to the app's required scopes.

        .. tab-set::

        .. tab-item:: Example Usage

            .. code-block:: python

                app = UserApp("myapp", ...)
                flows_client = (
                    FlowsClient(app=app)
                    .add_app_scope(FlowsScopes.manage_flows)
                    .add_app_scope(FlowsScopes.run_manage)
                )

        """
        if not self._app:
            raise exc.GlobusSDKUsageError(
                "Cannot 'add_app_scope' on a client that does not have an 'app'."
            )
        if self.resource_server is None:
            raise ValueError(
                "Unable to use an 'app' with a client with no "
                "'resource_server' defined."
            )
        self._app.add_scope_requirements({self.resource_server: scope_collection})

        return self

    @property
    def app_name(self) -> str | None:
        return self._app_name

    @app_name.setter
    def app_name(self, value: str) -> None:
        self._app_name = self.transport.user_agent = value

    @utils.classproperty
    def resource_server(  # pylint: disable=missing-param-doc
        self_or_cls: BaseClient | type[BaseClient],
    ) -> str | None:
        """
        The resource_server name for the API and scopes associated with this client.

        This information is pulled from the ``scopes`` attribute of the client class.
        If the client does not have associated scopes, this value will be ``None``.

        This must return sane results while the Base Client is being initialized.
        """
        if self_or_cls.scopes is None:
            return None
        return self_or_cls.scopes.resource_server

    def get(  # pylint: disable=missing-param-doc
        self,
        path: str,
        *,
        query_params: dict[str, t.Any] | None = None,
        headers: dict[str, str] | None = None,
        automatic_authorization: bool = True,
    ) -> GlobusHTTPResponse:
        """
        Make a GET request to the specified path.

        See :py:meth:`~.BaseClient.request` for details on the various parameters.
        """
        log.debug(f"GET to {path} with query_params {query_params}")
        return self.request(
            "GET",
            path,
            query_params=query_params,
            headers=headers,
            automatic_authorization=automatic_authorization,
        )

    def post(  # pylint: disable=missing-param-doc
        self,
        path: str,
        *,
        query_params: dict[str, t.Any] | None = None,
        data: _DataParamType = None,
        headers: dict[str, str] | None = None,
        encoding: str | None = None,
        automatic_authorization: bool = True,
    ) -> GlobusHTTPResponse:
        """
        Make a POST request to the specified path.

        See :py:meth:`~.BaseClient.request` for details on the various parameters.
        """
        log.debug(f"POST to {path} with query_params {query_params}")
        return self.request(
            "POST",
            path,
            query_params=query_params,
            data=data,
            headers=headers,
            encoding=encoding,
            automatic_authorization=automatic_authorization,
        )

    def delete(  # pylint: disable=missing-param-doc
        self,
        path: str,
        *,
        query_params: dict[str, t.Any] | None = None,
        headers: dict[str, str] | None = None,
        automatic_authorization: bool = True,
    ) -> GlobusHTTPResponse:
        """
        Make a DELETE request to the specified path.

        See :py:meth:`~.BaseClient.request` for details on the various parameters.
        """
        log.debug(f"DELETE to {path} with query_params {query_params}")
        return self.request(
            "DELETE",
            path,
            query_params=query_params,
            headers=headers,
            automatic_authorization=automatic_authorization,
        )

    def put(  # pylint: disable=missing-param-doc
        self,
        path: str,
        *,
        query_params: dict[str, t.Any] | None = None,
        data: _DataParamType = None,
        headers: dict[str, str] | None = None,
        encoding: str | None = None,
        automatic_authorization: bool = True,
    ) -> GlobusHTTPResponse:
        """
        Make a PUT request to the specified path.

        See :py:meth:`~.BaseClient.request` for details on the various parameters.
        """
        log.debug(f"PUT to {path} with query_params {query_params}")
        return self.request(
            "PUT",
            path,
            query_params=query_params,
            data=data,
            headers=headers,
            encoding=encoding,
            automatic_authorization=automatic_authorization,
        )

    def patch(  # pylint: disable=missing-param-doc
        self,
        path: str,
        *,
        query_params: dict[str, t.Any] | None = None,
        data: _DataParamType = None,
        headers: dict[str, str] | None = None,
        encoding: str | None = None,
        automatic_authorization: bool = True,
    ) -> GlobusHTTPResponse:
        """
        Make a PATCH request to the specified path.

        See :py:meth:`~.BaseClient.request` for details on the various parameters.
        """
        log.debug(f"PATCH to {path} with query_params {query_params}")
        return self.request(
            "PATCH",
            path,
            query_params=query_params,
            data=data,
            headers=headers,
            encoding=encoding,
            automatic_authorization=automatic_authorization,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        query_params: dict[str, t.Any] | None = None,
        data: _DataParamType = None,
        headers: dict[str, str] | None = None,
        encoding: str | None = None,
        allow_redirects: bool = True,
        stream: bool = False,
        automatic_authorization: bool = True,
    ) -> GlobusHTTPResponse:
        """
        Send an HTTP request

        :param method: HTTP request method, as an all caps string
        :param path: Path for the request, with or without leading slash
        :param query_params: Parameters to be encoded as a query string
        :param headers: HTTP headers to add to the request. Authorization headers may
            be overwritten unless ``automatic_authorization`` is False.
        :param data: Data to send as the request body. May pass through encoding.
        :param encoding: A way to encode request data. "json", "form", and "text"
            are all valid values. Custom encodings can be used only if they are
            registered with the transport. By default, strings get "text" behavior and
            all other objects get "json".
        :param allow_redirects: Follow Location headers on redirect response
            automatically. Defaults to ``True``
        :param stream: Do not immediately download the response content. Defaults to
            ``False``
        :param automatic_authorization: Use this client's ``app`` or ``authorizer``
            to automatically generate an Authorization header.

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
            # if passed a path which has a prefix matching the base_path, strip it
            # this means that if a client has a base path of `/v1/`, a request for
            # `/v1/foo` will hit `/v1/foo` rather than `/v1/v1/foo`
            if path.startswith(self.base_path):
                path = path[len(self.base_path) :]
            url = utils.slash_join(self.base_url, urllib.parse.quote(path))

        # either use given authorizer or get one from app
        if automatic_authorization:
            authorizer = self.authorizer
            if self._app and self.resource_server:
                authorizer = self._app.get_authorizer(self.resource_server)
        else:
            authorizer = None

        # make the request
        log.debug("request will hit URL: %s", url)
        r = self.transport.request(
            method=method,
            url=url,
            data=data,
            query_params=query_params,
            headers=rheaders,
            encoding=encoding,
            authorizer=authorizer,
            allow_redirects=allow_redirects,
            stream=stream,
        )
        log.debug("request made to URL: %s", r.url)

        if 200 <= r.status_code < 400:
            log.debug(f"request completed with response code: {r.status_code}")
            return GlobusHTTPResponse(r, self)

        log.debug(f"request completed with (error) response code: {r.status_code}")
        raise self.error_class(r)
