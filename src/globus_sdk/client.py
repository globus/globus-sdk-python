from __future__ import annotations

import logging
import sys
import typing as t
import urllib.parse

from globus_sdk import GlobusSDKUsageError, config, exc
from globus_sdk._classproperty import classproperty
from globus_sdk._types import ScopeCollectionType
from globus_sdk._utils import slash_join
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.paging import PaginatorTable
from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.scopes import Scope, ScopeCollection
from globus_sdk.transport import RequestsTransport

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

if t.TYPE_CHECKING:
    from globus_sdk.globus_app import GlobusApp

log = logging.getLogger(__name__)

_DataParamType: TypeAlias = t.Union[None, str, bytes, t.Dict[str, t.Any]]


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
        communicating through a proxy. This value takes precedence over the class
        attribute of the same name.
    :param transport_params: Options to pass to the transport for this client

    All other parameters are for internal use and should be ignored.
    """

    # service name is used to lookup a service URL from config
    service_name: str = "_base"

    # the URL for the service
    # NOTE: this is not the only way to define a base url. See the docstring of the
    # `BaseClient._resolve_base_url` method for more details.
    base_url: str = "_base"

    #: the class for errors raised by this client on HTTP 4xx and 5xx errors
    #: this can be set in subclasses, but must always be a subclass of GlobusError
    error_class: type[exc.GlobusAPIError] = exc.GlobusAPIError

    #: the type of Transport which will be used, defaults to ``RequestsTransport``
    transport_class: type[RequestsTransport] = RequestsTransport

    #: the scopes for this client may be present as a ``ScopeCollection``
    scopes: ScopeCollection | None = None

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
    ) -> None:
        # check for input parameter conflicts
        if app_scopes and not app:
            raise exc.GlobusSDKUsageError(
                f"A {type(self).__name__} must have an 'app' to use 'app_scopes'."
            )
        if app and authorizer:
            raise exc.GlobusSDKUsageError(
                f"A {type(self).__name__} cannot use both an 'app' and an 'authorizer'."
            )

        # Determine the client's environment
        # Either the provided kwarg or derived from the app used
        #
        # If neither is specified, fallback to the GLOBUS_SDK_ENVIRONMENT environment
        # variable.
        if environment:
            self.environment = environment
        elif app:
            self.environment = app.config.environment
        else:
            self.environment = config.get_environment_name()

        # resolve the base_url for the client (see docstring for resolution precedence)
        self.base_url = self._resolve_base_url(base_url, self.environment)

        self.transport = self.transport_class(**(transport_params or {}))
        log.debug(f"initialized transport of type {type(self.transport)}")

        # setup paginated methods
        self.paginated = PaginatorTable(self)

        # set application name if available from app_name
        # if this is not set, `app.app_name` may be applied below
        self._app_name: str | None = None
        if app_name is not None:
            self.app_name = app_name

        # attach the app or authorizer provided
        # starting app attributes as `None` and calling the attachment method
        self.authorizer = authorizer
        self._app: GlobusApp | None = None
        self.app_scopes: list[Scope] | None = None
        if app:
            self.attach_globus_app(app, app_scopes=app_scopes)

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

    @classmethod
    def _resolve_base_url(cls, init_base_url: str | None, environment: str) -> str:
        """
        Resolve the client's base url.

        Precedence (this evaluation will fall through if an option is not set):
          1. [Highest] Constructor `base_url` value.
          2. Class `base_url` attribute.
          3. Class `service_name` attribute (computed).

        :param init_base_url: The `base_url` value supplied to the constructor.
        :param environment: The environment to use for service URL resolution.
        :returns: The resolved base URL.
        :raises: GlobusSDKUsageError if base_url cannot be resolved.
        """
        if init_base_url is not None:
            log.debug(f"Creating client of type {cls}")
            return init_base_url
        elif cls.base_url != "_base":
            log.debug(f"Creating client of type {cls}")
            return cls.base_url
        elif cls.service_name != "_base":
            log.debug(f'Creating client of type {cls} for service "{cls.service_name}"')
            return config.get_service_url(cls.service_name, environment)

        raise GlobusSDKUsageError(
            f"Unable to resolve base_url in client {cls}. "
            f"Clients must define either one or both of 'base_url' and 'service_name'."
        )

    def attach_globus_app(
        self, app: GlobusApp, app_scopes: list[Scope] | None = None
    ) -> None:
        """
        Attach a ``GlobusApp`` to this client and, conversely, register this client with
        that app. The client's default scopes will be added to the app's scope
        requirements unless ``app_scopes`` is used to override this.

        If the ``app_name`` is not set on the client, it will be set to match that of
        the app.

        .. note::

            This method is only safe to call once per client object. It is implicitly
            called if the client is initialized with an app.

        :param app: The ``GlobusApp`` to attach to this client.
        :param app_scopes: Optional list of ``Scope`` objects to be added to ``app``'s
            scope requirements instead of ``default_scope_requirements``. These will be
            stored in the ``app_scopes`` attribute of the client.

        :raises GlobusSDKUsageError: If the attachment appears to conflict with the
            state of the client. e.g., an app or authorizer is already in place.
        """
        # If there are any incompatible or ambiguous data, usage error.
        # "In the face of ambiguity, refuse the temptation to guess."
        if self._app:
            raise exc.GlobusSDKUsageError(
                f"Cannot attach GlobusApp to {type(self).__name__} when one is "
                "already attached."
            )
        if self.app_scopes:
            # technically, we *could* allow for this, but it's not clear what
            # it would mean if a user wrote the following:
            #
            #   c = ClientClass()
            #   c.app_scopes = [foo]
            #   c.attach_globus_app(app, app_scopes=[bar])
            #
            # did the user expect a merge, overwrite, or other behavior?
            raise exc.GlobusSDKUsageError(
                f"Cannot attach GlobusApp to {type(self).__name__} when `app_scopes` "
                "is already set. "
                "The scopes for this client cannot be consistently resolved."
            )
        if self.authorizer:
            raise exc.GlobusSDKUsageError(
                f"Cannot attach GlobusApp to {type(self).__name__} when it "
                "has an authorizer assigned."
            )
        if self.resource_server is None:
            raise exc.GlobusSDKUsageError(
                "Unable to use an 'app' with a client with no "
                "'resource_server' defined."
            )
        # the client's environment must match the app's
        #
        # there are only two ways to get to a mismatch:
        #
        # 1. pass an explicit environment which doesn't match the app, e.g.,
        #   `MyClient(environment="a", app=app)` where `app.config.environment="b"`
        #
        # 2. initialize a client without an app and later attach an app which doesn't
        #    match, e.g., `MyClient(environment="a").attach_globus_app(app)`
        #
        # in these cases, the user has explicitly given us conflicting instructions
        if self.environment != app.config.environment:
            raise exc.GlobusSDKUsageError(
                f"[Environment Mismatch] {type(self).__name__}'s environment "
                f"({self.environment}) does not match the GlobusApp's configured "
                f"environment ({app.config.environment})."
            )

        # now, assign the app, app_name, and scopes
        self._app = app
        self.app_scopes = app_scopes or self.default_scope_requirements
        if self.app_name is None:
            self.app_name = app.app_name

        # finally, register the scope requirements on the app side
        self._app.add_scope_requirements({self.resource_server: self.app_scopes})

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

    @classproperty
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
            url = slash_join(self.base_url, urllib.parse.quote(path))

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
