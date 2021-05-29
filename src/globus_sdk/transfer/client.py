import logging
import time
import uuid
from typing import Dict, Iterable, Optional, Union

from globus_sdk import exc, response, utils
from globus_sdk.base import BaseClient
from globus_sdk.transfer.paging import PaginatedResource
from globus_sdk.transfer.response import (
    ActivationRequirementsResponse,
    IterableTransferResponse,
)

log = logging.getLogger(__name__)

ID_PARAM_TYPE = Union[bytes, str, uuid.UUID]


class TransferClient(BaseClient):
    r"""
    Client for the
    `Globus Transfer API <https://docs.globus.org/api/transfer/>`_.

    This class provides helper methods for most common resources in the
    REST API, and basic ``get``, ``put``, ``post``, and ``delete`` methods
    from the base rest client that can be used to access any REST resource.

    Some calls are paginated. If a call returns a :class:`PaginatedResource \
    <globus_sdk.transfer.paging.PaginatedResource>` object, the result is an
    iterator which can only be walked *once*. If you need to do multiple passes
    over the result, call ``list()`` on the ``PaginatedResource`` or call the
    original method again to get fresh results.

    Detailed documentation is available in the official REST API
    documentation, which is linked to from the method documentation. Methods
    that allow arbitrary keyword arguments will pass the extra arguments as
    query parameters.

    :param authorizer: An authorizer instance used for all calls to
                       Globus Transfer
    :type authorizer: :class:`GlobusAuthorizer\
                      <globus_sdk.authorizers.base.GlobusAuthorizer>`

    .. automethodlist:: globus_sdk.TransferClient
    """
    service_name = "transfer"
    base_path = "/v0.10/"
    error_class = exc.TransferAPIError

    # Convenience methods, providing more pythonic access to common REST
    # resources

    #
    # Endpoint Management
    #

    def get_endpoint(
        self, endpoint_id: ID_PARAM_TYPE, **params
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /endpoint/<endpoint_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> endpoint = tc.get_endpoint(endpoint_id)
        >>> print("Endpoint name:",
        >>>       endpoint["display_name"] or endpoint["canonical_name"])

        **External Documentation**

        See
        `Get Endpoint by ID \
        <https://docs.globus.org/api/transfer/endpoint/#get_endpoint_by_id>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.get_endpoint({endpoint_id_s})")
        path = self.qjoin_path("endpoint", endpoint_id_s)
        return self.get(path, params=params)

    def update_endpoint(
        self, endpoint_id: ID_PARAM_TYPE, data, **params
    ) -> response.GlobusHTTPResponse:
        """
        ``PUT /endpoint/<endpoint_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> epup = dict(display_name="My New Endpoint Name",
        >>>             description="Better Description")
        >>> update_result = tc.update_endpoint(endpoint_id, epup)

        **External Documentation**

        See
        `Update Endpoint by ID \
        <https://docs.globus.org/api/transfer/endpoint/#update_endpoint_by_id>`_
        in the REST documentation for details.
        """
        if data.get("myproxy_server"):
            if data.get("oauth_server"):
                raise exc.GlobusSDKUsageError(
                    "an endpoint cannot be reconfigured to use multiple "
                    "identity providers for activation; specify either "
                    "MyProxy or OAuth, not both"
                )
            else:
                data["oauth_server"] = None
        elif data.get("oauth_server"):
            data["myproxy_server"] = None

        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.update_endpoint({endpoint_id_s}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id_s)
        return self.put(path, data=data, params=params)

    def create_endpoint(self, data) -> response.GlobusHTTPResponse:
        """
        ``POST /endpoint/<endpoint_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> ep_data = {
        >>>   "DATA_TYPE": "endpoint",
        >>>   "display_name": display_name,
        >>>   "DATA": [
        >>>     {
        >>>       "DATA_TYPE": "server",
        >>>       "hostname": "gridftp.example.edu",
        >>>     },
        >>>   ],
        >>> }
        >>> create_result = tc.create_endpoint(ep_data)
        >>> endpoint_id = create_result["id"]

        **External Documentation**

        See
        `Create endpoint \
        <https://docs.globus.org/api/transfer/endpoint/#create_endpoint>`_
        in the REST documentation for details.
        """
        if data.get("myproxy_server") and data.get("oauth_server"):
            raise exc.GlobusSDKUsageError(
                "an endpoint cannot be created using multiple identity "
                "providers for activation; specify either MyProxy or OAuth, "
                "not both"
            )

        log.info("TransferClient.create_endpoint(...)")
        return self.post("endpoint", data=data)

    def delete_endpoint(
        self, endpoint_id: ID_PARAM_TYPE
    ) -> response.GlobusHTTPResponse:
        """
        ``DELETE /endpoint/<endpoint_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> delete_result = tc.delete_endpoint(endpoint_id)

        **External Documentation**

        See
        `Delete endpoint by id \
        <https://docs.globus.org/api/transfer/endpoint/#delete_endpoint_by_id>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.delete_endpoint({endpoint_id_s})")
        path = self.qjoin_path("endpoint", endpoint_id_s)
        return self.delete(path)

    def endpoint_search(
        self,
        filter_fulltext: Optional[str] = None,
        filter_scope: Optional[str] = None,
        num_results=25,
        **params,
    ) -> PaginatedResource:
        r"""
        .. parsed-literal::

            GET /endpoint_search\
            ?filter_fulltext=<filter_fulltext>&filter_scope=<filter_scope>

        :param filter_fulltext: The string to use in a full text search on endpoints.
            Effectively, the "search query" which is being requested. May be omitted
            with specific ``filter_scope`` values.
        :type filter_fulltext: str, optional
        :param filter_scope: A "scope" within which to search for endpoints. This must
            be one of the limited and known names known to the service, which can be
            found documented in the **External Documentation** below. Defaults to
            searching all endpoints (in which case ``filter_fulltext`` is required)
        :type filter_scope: str, optional
        :param num_results: The number of search results to fetch from the service. May
            be set to ``None`` to request the maximum allowable number of results.
            [Default: ``25``]
        :type num_results: int or None
        :param params: Any additional parameters will be passed through as query params.
        :type params: dict
        :rtype: :class:`PaginatedResource
                <globus_sdk.transfer.paging.PaginatedResource>`,
                an iterable of :class:`GlobusResponse
                <globus_sdk.response.GlobusResponse>`

        **Examples**

        Search for a given string as a fulltext search:

        >>> tc = globus_sdk.TransferClient(...)
        >>> for ep in tc.endpoint_search('String to search for!'):
        >>>     print(ep['display_name'])

        Search for a given string, but only on endpoints that you own:

        >>> for ep in tc.endpoint_search('foo', filter_scope='my-endpoints'):
        >>>     print('{0} has ID {1}'.format(ep['display_name'], ep['id']))

        Search results are capped at a number of elements equal to the
        ``num_results`` parameter.
        If you want more than the default, 25, elements, do like so:

        >>> for ep in tc.endpoint_search('String to search for!',
        >>>                             num_results=120):
        >>>     print(ep['display_name'])

        It is important to be aware that the Endpoint Search API limits
        you to 1000 results for any search query.
        You can request the maximum number of results either explicitly, with
        ``num_results=1000``, or by stating that you want no limit by setting
        it to ``None``:

        >>> for ep in tc.endpoint_search('String to search for!',
        >>>                             num_results=None):
        >>>     print(ep['display_name'])

        **External Documentation**

        For additional information, see `Endpoint Search
        <https://docs.globus.org/api/transfer/endpoint_search>`_.
        in the REST documentation for details.
        """
        if filter_scope is not None:
            params["filter_scope"] = filter_scope
        if filter_fulltext is not None:
            params["filter_fulltext"] = filter_fulltext
        log.info(f"TransferClient.endpoint_search({params})")
        return PaginatedResource(
            self.get,
            "endpoint_search",
            {"params": params},
            num_results=num_results,
            max_results_per_call=100,
            max_total_results=1000,
        )

    def endpoint_autoactivate(
        self, endpoint_id: ID_PARAM_TYPE, **params
    ) -> response.GlobusHTTPResponse:
        r"""
        ``POST /endpoint/<endpoint_id>/autoactivate``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        The following example will try to "auto" activate the endpoint
        using a credential available from another endpoint or sign in by
        the user with the same identity provider, but only if the
        endpoint is not already activated or going to expire within an
        hour (3600 seconds). If that fails, direct the user to the
        globus website to perform activation:

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> r = tc.endpoint_autoactivate(ep_id, if_expires_in=3600)
        >>> while (r["code"] == "AutoActivationFailed"):
        >>>     print("Endpoint requires manual activation, please open "
        >>>           "the following URL in a browser to activate the "
        >>>           "endpoint:")
        >>>     print("https://app.globus.org/file-manager?origin_id=%s"
        >>>           % ep_id)
        >>>     input("Press ENTER after activating the endpoint:")
        >>>     r = tc.endpoint_autoactivate(ep_id, if_expires_in=3600)

        This is the recommended flow for most thick client applications,
        because many endpoints require activation via OAuth MyProxy,
        which must be done in a browser anyway. Web based clients can
        link directly to the URL.

        You also might want messaging or logging depending on why and how the
        operation succeeded, in which case you'll need to look at the value of
        the "code" field and either decide on your own messaging or use the
        response's "message" field.

        >>> tc = globus_sdk.TransferClient(...)
        >>> r = tc.endpoint_autoactivate(ep_id, if_expires_in=3600)
        >>> if r['code'] == 'AutoActivationFailed':
        >>>     print('Endpoint({}) Not Active! Error! Source message: {}'
        >>>           .format(ep_id, r['message']))
        >>>     sys.exit(1)
        >>> elif r['code'] == 'AutoActivated.CachedCredential':
        >>>     print('Endpoint({}) autoactivated using a cached credential.'
        >>>           .format(ep_id))
        >>> elif r['code'] == 'AutoActivated.GlobusOnlineCredential':
        >>>     print(('Endpoint({}) autoactivated using a built-in Globus '
        >>>            'credential.').format(ep_id))
        >>> elif r['code'] = 'AlreadyActivated':
        >>>     print('Endpoint({}) already active until at least {}'
        >>>           .format(ep_id, 3600))

        **External Documentation**

        See
        `Autoactivate endpoint \
        <https://docs.globus.org/api/transfer/endpoint_activation/#autoactivate_endpoint>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.endpoint_autoactivate({endpoint_id_s})")
        path = self.qjoin_path("endpoint", endpoint_id_s, "autoactivate")
        return self.post(path, params=params)

    def endpoint_deactivate(
        self, endpoint_id: ID_PARAM_TYPE, **params
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /endpoint/<endpoint_id>/deactivate``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Deactive endpoint \
        <https://docs.globus.org/api/transfer/endpoint_activation/#deactivate_endpoint>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.endpoint_deactivate({endpoint_id_s})")
        path = self.qjoin_path("endpoint", endpoint_id_s, "deactivate")
        return self.post(path, params=params)

    def endpoint_activate(
        self, endpoint_id: ID_PARAM_TYPE, requirements_data, **params
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /endpoint/<endpoint_id>/activate``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        Consider using autoactivate and web activation instead, described
        in the example for
        :meth:`~globus_sdk.TransferClient.endpoint_autoactivate`.

        **External Documentation**

        See
        `Activate endpoint \
        <https://docs.globus.org/api/transfer/endpoint_activation/#activate_endpoint>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.endpoint_activate({endpoint_id_s})")
        path = self.qjoin_path("endpoint", endpoint_id_s, "activate")
        return self.post(path, data=requirements_data, params=params)

    def endpoint_get_activation_requirements(
        self, endpoint_id: ID_PARAM_TYPE, **params
    ) -> ActivationRequirementsResponse:
        """
        ``GET /endpoint/<endpoint_id>/activation_requirements``

        :rtype: :class:`ActivationRequirementsResponse
                <globus_sdk.transfer.response.ActivationRequirementsResponse>`

        **External Documentation**

        See
        `Get activation requirements \
        <https://docs.globus.org/api/transfer/endpoint_activation/#get_activation_requirements>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        path = self.qjoin_path("endpoint", endpoint_id_s, "activation_requirements")
        return ActivationRequirementsResponse(self.get(path, params=params))

    def my_effective_pause_rule_list(
        self, endpoint_id: ID_PARAM_TYPE, **params
    ) -> IterableTransferResponse:
        """
        ``GET /endpoint/<endpoint_id>/my_effective_pause_rule_list``

        :rtype: :class:`IterableTransferResponse
                <globus_sdk.transfer.response.IterableTransferResponse>`

        **External Documentation**

        See
        `Get my effective endpoint pause rules \
        <https://docs.globus.org/api/transfer/endpoint/#get_endpoint_pause_rules>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.my_effective_pause_rule_list({endpoint_id_s}, ...)")
        path = self.qjoin_path(
            "endpoint", endpoint_id_s, "my_effective_pause_rule_list"
        )
        return IterableTransferResponse(self.get(path, params=params))

    # Shared Endpoints

    def my_shared_endpoint_list(
        self, endpoint_id: ID_PARAM_TYPE, **params
    ) -> IterableTransferResponse:
        """
        ``GET /endpoint/<endpoint_id>/my_shared_endpoint_list``

        :rtype: :class:`IterableTransferResponse
                <globus_sdk.transfer.response.IterableTransferResponse>`

        **External Documentation**

        See
        `Get shared endpoint list \
        <https://docs.globus.org/api/transfer/endpoint/#get_shared_endpoint_list>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.my_shared_endpoint_list({endpoint_id_s}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id_s, "my_shared_endpoint_list")
        return IterableTransferResponse(self.get(path, params=params))

    def create_shared_endpoint(self, data):
        """
        ``POST /shared_endpoint``

        :param data: A python dict representation of a ``shared_endpoint`` document
        :type data: dict
        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> shared_ep_data = {
        >>>   "DATA_TYPE": "shared_endpoint",
        >>>   "host_endpoint": host_endpoint_id,
        >>>   "host_path": host_path,
        >>>   "display_name": display_name,
        >>>   # optionally specify additional endpoint fields
        >>>   "description": "my test share"
        >>> }
        >>> create_result = tc.create_shared_endpoint(shared_ep_data)
        >>> endpoint_id = create_result["id"]

        **External Documentation**

        See
        `Create shared endpoint \
        <https://docs.globus.org/api/transfer/endpoint/#create_shared_endpoint>`_
        in the REST documentation for details.
        """
        log.info("TransferClient.create_shared_endpoint(...)")
        return self.post("shared_endpoint", data=data)

    # Endpoint servers

    def endpoint_server_list(
        self, endpoint_id: ID_PARAM_TYPE, **params
    ) -> IterableTransferResponse:
        """
        ``GET /endpoint/<endpoint_id>/server_list``

        :rtype: :class:`IterableTransferResponse
                <globus_sdk.transfer.response.IterableTransferResponse>`

        **External Documentation**

        See
        `Get endpoint server list \
        <https://docs.globus.org/api/transfer/endpoint/#get_endpoint_server_list>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.endpoint_server_list({endpoint_id_s}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id_s, "server_list")
        return IterableTransferResponse(self.get(path, params=params))

    def get_endpoint_server(
        self, endpoint_id: ID_PARAM_TYPE, server_id, **params
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /endpoint/<endpoint_id>/server/<server_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Get endpoint server by id\
        <https://docs.globus.org/api/transfer/endpoint/#get_endpoint_server_by_id>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(
            "TransferClient.get_endpoint_server(%s, %s, ...)", endpoint_id_s, server_id
        )
        path = self.qjoin_path("endpoint", endpoint_id_s, "server", str(server_id))
        return self.get(path, params=params)

    def add_endpoint_server(
        self, endpoint_id: ID_PARAM_TYPE, server_data: Dict
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /endpoint/<endpoint_id>/server``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Add endpoint server \
        <https://docs.globus.org/api/transfer/endpoint/#add_endpoint_server>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.add_endpoint_server({endpoint_id_s}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id_s, "server")
        return self.post(path, data=server_data)

    def update_endpoint_server(
        self, endpoint_id: ID_PARAM_TYPE, server_id, server_data: Dict
    ) -> response.GlobusHTTPResponse:
        """
        ``PUT /endpoint/<endpoint_id>/server/<server_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Update endpoint server by id \
        <https://docs.globus.org/api/transfer/endpoint/#update_endpoint_server_by_id>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(
            "TransferClient.update_endpoint_server(%s, %s, ...)",
            endpoint_id_s,
            server_id,
        )
        path = self.qjoin_path("endpoint", endpoint_id_s, "server", str(server_id))
        return self.put(path, data=server_data)

    def delete_endpoint_server(
        self, endpoint_id: ID_PARAM_TYPE, server_id
    ) -> response.GlobusHTTPResponse:
        """
        ``DELETE /endpoint/<endpoint_id>/server/<server_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Delete endpoint server by id \
        <https://docs.globus.org/api/transfer/endpoint/#delete_endpoint_server_by_id>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(
            "TransferClient.delete_endpoint_server(%s, %s)", endpoint_id_s, server_id
        )
        path = self.qjoin_path("endpoint", endpoint_id_s, "server", str(server_id))
        return self.delete(path)

    #
    # Roles
    #

    def endpoint_role_list(
        self, endpoint_id: ID_PARAM_TYPE, **params
    ) -> IterableTransferResponse:
        """
        ``GET /endpoint/<endpoint_id>/role_list``

        :rtype: :class:`IterableTransferResponse
                <globus_sdk.transfer.response.IterableTransferResponse>`

        **External Documentation**

        See
        `Get list of endpoint roles \
        <https://docs.globus.org/api/transfer/endpoint_roles/#role_list>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.endpoint_role_list({endpoint_id_s}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id_s, "role_list")
        return IterableTransferResponse(self.get(path, params=params))

    def add_endpoint_role(
        self, endpoint_id: ID_PARAM_TYPE, role_data: Dict
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /endpoint/<endpoint_id>/role``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Create endpoint role \
        <https://docs.globus.org/api/transfer/endpoint_roles/#create_role>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.add_endpoint_role({endpoint_id_s}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id_s, "role")
        return self.post(path, data=role_data)

    def get_endpoint_role(
        self, endpoint_id: ID_PARAM_TYPE, role_id, **params
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /endpoint/<endpoint_id>/role/<role_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Get endpoint role by id \
        <https://docs.globus.org/api/transfer/endpoint_roles/#get_endpoint_role_by_id>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.get_endpoint_role({endpoint_id_s}, {role_id}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id_s, "role", role_id)
        return self.get(path, params=params)

    def delete_endpoint_role(
        self, endpoint_id: ID_PARAM_TYPE, role_id
    ) -> response.GlobusHTTPResponse:
        """
        ``DELETE /endpoint/<endpoint_id>/role/<role_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Delete endpoint role by id \
        <https://docs.globus.org/api/transfer/endpoint_roles/#delete_endpoint_role_by_id>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.delete_endpoint_role({endpoint_id_s}, {role_id})")
        path = self.qjoin_path("endpoint", endpoint_id_s, "role", role_id)
        return self.delete(path)

    #
    # ACLs
    #

    def endpoint_acl_list(
        self, endpoint_id: ID_PARAM_TYPE, **params
    ) -> IterableTransferResponse:
        """
        ``GET /endpoint/<endpoint_id>/access_list``

        :rtype: :class:`IterableTransferResponse
                <globus_sdk.transfer.response.IterableTransferResponse>`

        **External Documentation**

        See
        `Get list of access rules \
        <https://docs.globus.org/api/transfer/acl/#rest_access_get_list>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.endpoint_acl_list({endpoint_id_s}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id_s, "access_list")
        return IterableTransferResponse(self.get(path, params=params))

    def get_endpoint_acl_rule(
        self, endpoint_id: ID_PARAM_TYPE, rule_id, **params
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /endpoint/<endpoint_id>/access/<rule_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Get access rule by id \
        <https://docs.globus.org/api/transfer/acl/#get_access_rule_by_id>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(
            "TransferClient.get_endpoint_acl_rule(%s, %s, ...)", endpoint_id_s, rule_id
        )
        path = self.qjoin_path("endpoint", endpoint_id_s, "access", rule_id)
        return self.get(path, params=params)

    def add_endpoint_acl_rule(
        self, endpoint_id: ID_PARAM_TYPE, rule_data: Dict
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /endpoint/<endpoint_id>/access``

        :param endpoint_id: ID of endpoint to which to add the acl
        :type endpoint_id: str
        :param rule_data: A python dict representation of an ``access`` document
        :type rule_data: dict
        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> rule_data = {
        >>>   "DATA_TYPE": "access",
        >>>   "principal_type": "identity",
        >>>   "principal": identity_id,
        >>>   "path": "/dataset1/",
        >>>   "permissions": "rw",
        >>> }
        >>> result = tc.add_endpoint_acl_rule(endpoint_id, rule_data)
        >>> rule_id = result["access_id"]

        Note that if this rule is being created on a shared endpoint
        the "path" field is relative to the "host_path" of the shared endpoint.

        **External Documentation**

        See
        `Create access rule \
        <https://docs.globus.org/api/transfer/acl/#rest_access_create>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.add_endpoint_acl_rule({endpoint_id_s}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id_s, "access")
        return self.post(path, data=rule_data)

    def update_endpoint_acl_rule(
        self, endpoint_id: ID_PARAM_TYPE, rule_id, rule_data: Dict
    ) -> response.GlobusHTTPResponse:
        """
        ``PUT /endpoint/<endpoint_id>/access/<rule_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Update access rule \
        <https://docs.globus.org/api/transfer/acl/#update_access_rule>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(
            "TransferClient.update_endpoint_acl_rule(%s, %s, ...)",
            endpoint_id_s,
            rule_id,
        )
        path = self.qjoin_path("endpoint", endpoint_id_s, "access", rule_id)
        return self.put(path, data=rule_data)

    def delete_endpoint_acl_rule(
        self, endpoint_id: ID_PARAM_TYPE, rule_id
    ) -> response.GlobusHTTPResponse:
        """
        ``DELETE /endpoint/<endpoint_id>/access/<rule_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Delete access rule \
        <https://docs.globus.org/api/transfer/acl/#delete_access_rule>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(
            "TransferClient.delete_endpoint_acl_rule(%s, %s)", endpoint_id_s, rule_id
        )
        path = self.qjoin_path("endpoint", endpoint_id_s, "access", rule_id)
        return self.delete(path)

    #
    # Bookmarks
    #

    def bookmark_list(self, **params) -> IterableTransferResponse:
        """
        ``GET /bookmark_list``

        :rtype: :class:`IterableTransferResponse
                <globus_sdk.transfer.response.IterableTransferResponse>`

        **External Documentation**

        See
        `Get list of bookmarks \
        <https://docs.globus.org/api/transfer/endpoint_bookmarks/#get_list_of_bookmarks>`_
        in the REST documentation for details.
        """
        log.info(f"TransferClient.bookmark_list({params})")
        return IterableTransferResponse(self.get("bookmark_list", params=params))

    def create_bookmark(self, bookmark_data: Dict) -> response.GlobusHTTPResponse:
        """
        ``POST /bookmark``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Create bookmark \
        <https://docs.globus.org/api/transfer/endpoint_bookmarks/#create_bookmark>`_
        in the REST documentation for details.
        """
        log.info(f"TransferClient.create_bookmark({bookmark_data})")
        return self.post("bookmark", data=bookmark_data)

    def get_bookmark(
        self, bookmark_id: ID_PARAM_TYPE, **params
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /bookmark/<bookmark_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Get bookmark by id \
        <https://docs.globus.org/api/transfer/endpoint_bookmarks/#get_bookmark_by_id>`_
        in the REST documentation for details.
        """
        bookmark_id_s = utils.safe_stringify(bookmark_id)
        log.info(f"TransferClient.get_bookmark({bookmark_id_s})")
        path = self.qjoin_path("bookmark", bookmark_id_s)
        return self.get(path, params=params)

    def update_bookmark(
        self, bookmark_id: ID_PARAM_TYPE, bookmark_data: Dict
    ) -> response.GlobusHTTPResponse:
        """
        ``PUT /bookmark/<bookmark_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Update bookmark \
        <https://docs.globus.org/api/transfer/endpoint_bookmarks/#update_bookmark>`_
        in the REST documentation for details.
        """
        bookmark_id_s = utils.safe_stringify(bookmark_id)
        log.info(f"TransferClient.update_bookmark({bookmark_id_s})")
        path = self.qjoin_path("bookmark", bookmark_id_s)
        return self.put(path, data=bookmark_data)

    def delete_bookmark(
        self, bookmark_id: ID_PARAM_TYPE
    ) -> response.GlobusHTTPResponse:
        """
        ``DELETE /bookmark/<bookmark_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Delete bookmark by id\
        <https://docs.globus.org/api/transfer/endpoint_bookmarks/#delete_bookmark_by_id>`_
        in the REST documentation for details.
        """
        bookmark_id_s = utils.safe_stringify(bookmark_id)
        log.info(f"TransferClient.delete_bookmark({bookmark_id_s})")
        path = self.qjoin_path("bookmark", bookmark_id_s)
        return self.delete(path)

    #
    # Synchronous Filesys Operations
    #

    def operation_ls(
        self, endpoint_id: ID_PARAM_TYPE, **params
    ) -> IterableTransferResponse:
        """
        ``GET /operation/endpoint/<endpoint_id>/ls``

        :rtype: :class:`IterableTransferResponse
                <globus_sdk.transfer.response.IterableTransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> for entry in tc.operation_ls(ep_id, path="/~/project1/"):
        >>>     print(entry["name"], entry["type"])

        **External Documentation**

        See
        `List Directory Contents \
        <https://docs.globus.org/api/transfer/file_operations/#list_directory_contents>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.operation_ls({endpoint_id_s}, {params})")
        path = self.qjoin_path("operation/endpoint", endpoint_id_s, "ls")
        return IterableTransferResponse(self.get(path, params=params))

    def operation_mkdir(
        self, endpoint_id: ID_PARAM_TYPE, path, **params
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /operation/endpoint/<endpoint_id>/mkdir``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> tc.operation_mkdir(ep_id, path="/~/newdir/")

        **External Documentation**

        See
        `Make Directory \
        <https://docs.globus.org/api/transfer/file_operations/#make_directory>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        path = utils.safe_stringify(path)
        log.info(
            "TransferClient.operation_mkdir({}, {}, {})".format(
                endpoint_id_s, path, params
            )
        )
        resource_path = self.qjoin_path("operation/endpoint", endpoint_id_s, "mkdir")
        json_body = {"DATA_TYPE": "mkdir", "path": path}
        return self.post(resource_path, data=json_body, params=params)

    def operation_rename(
        self, endpoint_id: ID_PARAM_TYPE, oldpath, newpath, **params
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /operation/endpoint/<endpoint_id>/rename``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> tc.operation_rename(ep_id, oldpath="/~/file1.txt",
        >>>                     newpath="/~/project1data.txt")

        **External Documentation**

        See
        `Rename \
        <https://docs.globus.org/api/transfer/file_operations/#rename>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        oldpath = utils.safe_stringify(oldpath)
        newpath = utils.safe_stringify(newpath)
        log.info(
            "TransferClient.operation_rename({}, {}, {}, {})".format(
                endpoint_id_s, oldpath, newpath, params
            )
        )
        resource_path = self.qjoin_path("operation/endpoint", endpoint_id_s, "rename")
        json_body = {"DATA_TYPE": "rename", "old_path": oldpath, "new_path": newpath}
        return self.post(resource_path, data=json_body, params=params)

    def operation_symlink(
        self, endpoint_id: ID_PARAM_TYPE, symlink_target, path, **params
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /operation/endpoint/<endpoint_id>/symlink``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        The ``path`` is the name of the symlink, and the ``symlink_target`` is
        the path referenced by the symlink.

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> tc.operation_symlink(ep_id, symlink_target="/~/file1.txt",
        >>>                      path="/~/link-to-file1.txt")

        **External Documentation**

        See
        `Symlink \
        <https://docs.globus.org/api/transfer/file_operations/#symlink>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        symlink_target = utils.safe_stringify(symlink_target)
        path = utils.safe_stringify(path)
        log.info(
            "TransferClient.operation_symlink({}, {}, {}, {})".format(
                endpoint_id_s, symlink_target, path, params
            )
        )
        resource_path = self.qjoin_path("operation/endpoint", endpoint_id_s, "symlink")
        data = {
            "DATA_TYPE": "symlink",
            "symlink_target": symlink_target,
            "path": path,
        }
        return self.post(resource_path, data=data, params=params)

    #
    # Task Submission
    #

    def get_submission_id(self, **params) -> response.GlobusHTTPResponse:
        """
        ``GET /submission_id``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        Submission IDs are required to submit tasks to the Transfer service
        via the :meth:`submit_transfer <.submit_transfer>` and
        :meth:`submit_delete <.submit_delete>` methods.

        Most users will not need to call this method directly, as the
        convenience classes :class:`TransferData <globus_sdk.TransferData>`
        and :class:`DeleteData <globus_sdk.DeleteData>` will call it
        automatically if they are not passed a ``submission_id`` explicitly.

        **External Documentation**

        See
        `Get a submission id \
        <https://docs.globus.org/api/transfer/task_submit/#get_submission_id>`_
        in the REST documentation for more details.
        """
        log.info(f"TransferClient.get_submission_id({params})")
        return self.get("submission_id", params=params)

    def submit_transfer(self, data) -> response.GlobusHTTPResponse:
        """
        ``POST /transfer``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> tdata = globus_sdk.TransferData(tc, source_endpoint_id,
        >>>                                 destination_endpoint_id,
        >>>                                 label="SDK example",
        >>>                                 sync_level="checksum")
        >>> tdata.add_item("/source/path/dir/", "/dest/path/dir/",
        >>>                recursive=True)
        >>> tdata.add_item("/source/path/file.txt",
        >>>                "/dest/path/file.txt")
        >>> transfer_result = tc.submit_transfer(tdata)
        >>> print("task_id =", transfer_result["task_id"])

        The `data` parameter can be a normal Python dictionary, or
        a :class:`TransferData <globus_sdk.TransferData>` object.

        **External Documentation**

        See
        `Submit a transfer task \
        <https://docs.globus.org/api/transfer/task_submit/#submit_transfer_task>`_
        in the REST documentation for more details.
        """
        log.info("TransferClient.submit_transfer(...)")
        return self.post("/transfer", data=data)

    def submit_delete(self, data) -> response.GlobusHTTPResponse:
        """
        ``POST /delete``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> ddata = globus_sdk.DeleteData(tc, endpoint_id, recursive=True)
        >>> ddata.add_item("/dir/to/delete/")
        >>> ddata.add_item("/file/to/delete/file.txt")
        >>> delete_result = tc.submit_delete(ddata)
        >>> print("task_id =", delete_result["task_id"])

        The `data` parameter can be a normal Python dictionary, or
        a :class:`DeleteData <globus_sdk.DeleteData>` object.

        **External Documentation**

        See
        `Submit a delete task \
        <https://docs.globus.org/api/transfer/task_submit/#submit_delete_task>`_
        in the REST documentation for details.
        """
        log.info("TransferClient.submit_delete(...)")
        return self.post("/delete", data=data)

    #
    # Task inspection and management
    #

    def task_list(self, num_results=10, **params) -> PaginatedResource:
        """
        Get an iterable of task documents owned by the current user.

        ``GET /task_list``

        :param num_results: The number of tasks to fetch from the service. May be set to
            ``None`` to request the maximum allowable number of results.
            [Default: ``10``]
        :type num_results: int or none
        :param params: Any additional parameters will be passed through as query params.
        :type params: dict, optional
        :rtype: :class:`PaginatedResource
                <globus_sdk.transfer.paging.PaginatedResource>`,
                an iterable of :class:`GlobusResponse
                <globus_sdk.response.GlobusResponse>`

        **Examples**

        Fetch the default number (10) of tasks and print some basic info:

        >>> tc = TransferClient(...)
        >>> for task in tc.task_list():
        >>>     print("Task({}): {} -> {}".format(
        >>>         task["task_id"], task["source_endpoint"],
        >>>         task["destination_endpoint"]))

        **External Documentation**

        See
        `Task list \
        <https://docs.globus.org/api/transfer/task/#get_task_list>`_
        in the REST documentation for details.
        """
        log.info("TransferClient.task_list(...)")
        return PaginatedResource(
            self.get,
            "task_list",
            {"params": params},
            num_results=num_results,
            max_results_per_call=1000,
            paging_style=PaginatedResource.PAGING_STYLE_TOTAL,
        )

    def task_event_list(
        self, task_id: ID_PARAM_TYPE, num_results=10, **params
    ) -> PaginatedResource:
        r"""
        List events (for example, faults and errors) for a given Task.

        ``GET /task/<task_id>/event_list``

        :param task_id: The ID of the task to inspect.
        :type task_id: str
        :param num_results: The number of events to fetch from the service. May be set
            to ``None`` to request the maximum allowable number of results.
            [Default: ``10``]
        :type num_results: int or None
        :param params: Any additional parameters will be passed through as query params.
        :type params: dict, optional
        :rtype: :class:`PaginatedResource
                <globus_sdk.transfer.paging.PaginatedResource>`,
                an iterable of :class:`GlobusResponse
                <globus_sdk.response.GlobusResponse>`

        **Examples**

        Fetch the default number (10) of events and print some basic info:

        >>> tc = TransferClient(...)
        >>> task_id = ...
        >>> for event in tc.task_event_list(task_id):
        >>>     print("Event on Task({}) at {}:\n{}".format(
        >>>         task_id, event["time"], event["description"])

        **External Documentation**

        See
        `Get event list \
        <https://docs.globus.org/api/transfer/task/#get_event_list>`_
        in the REST documentation for details.
        """
        task_id_s = utils.safe_stringify(task_id)
        log.info(f"TransferClient.task_event_list({task_id_s}, ...)")
        path = self.qjoin_path("task", task_id_s, "event_list")
        return PaginatedResource(
            self.get,
            path,
            {"params": params},
            num_results=num_results,
            max_results_per_call=1000,
            paging_style=PaginatedResource.PAGING_STYLE_TOTAL,
        )

    def get_task(self, task_id: ID_PARAM_TYPE, **params) -> response.GlobusHTTPResponse:
        """
        ``GET /task/<task_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Get task by id \
        <https://docs.globus.org/api/transfer/task/#get_task_by_id>`_
        in the REST documentation for details.
        """
        task_id_s = utils.safe_stringify(task_id)
        log.info(f"TransferClient.get_task({task_id_s}, ...)")
        resource_path = self.qjoin_path("task", task_id_s)
        return self.get(resource_path, params=params)

    def update_task(
        self, task_id: ID_PARAM_TYPE, data: Dict, **params
    ) -> response.GlobusHTTPResponse:
        """
        ``PUT /task/<task_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Update task by id \
        <https://docs.globus.org/api/transfer/task/#update_task_by_id>`_
        in the REST documentation for details.
        """
        task_id_s = utils.safe_stringify(task_id)
        log.info(f"TransferClient.update_task({task_id_s}, ...)")
        resource_path = self.qjoin_path("task", task_id_s)
        return self.put(resource_path, data=data, params=params)

    def cancel_task(self, task_id: ID_PARAM_TYPE) -> response.GlobusHTTPResponse:
        """
        ``POST /task/<task_id>/cancel``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Cancel task by id \
        <https://docs.globus.org/api/transfer/task/#cancel_task_by_id>`_
        in the REST documentation for details.
        """
        task_id_s = utils.safe_stringify(task_id)
        log.info(f"TransferClient.cancel_task({task_id_s})")
        resource_path = self.qjoin_path("task", task_id_s, "cancel")
        return self.post(resource_path)

    def task_wait(
        self, task_id: ID_PARAM_TYPE, timeout=10, polling_interval=10
    ) -> bool:
        r"""
        Wait until a Task is complete or fails, with a time limit. If the task
        is "ACTIVE" after time runs out, returns ``False``. Otherwise returns
        ``True``.

        :param task_id: ID of the Task to wait on for completion
        :type task_id: str
        :param timeout: Number of seconds to wait in total. Minimum 1. [Default: ``10``]
        :type timeout: int, optional
        :param polling_interval: Number of seconds between queries to Globus about the
            Task status. Minimum 1. [Default: ``10``]
        :type polling_interval: int, optional

        **Examples**

        If you want to wait for a task to terminate, but want to warn every
        minute that it doesn't terminate, you could:

        >>> tc = TransferClient(...)
        >>> while not tc.task_wait(task_id, timeout=60):
        >>>     print("Another minute went by without {0} terminating"
        >>>           .format(task_id))

        Or perhaps you want to check on a task every minute for 10 minutes, and
        give up if it doesn't complete in that time:

        >>> tc = TransferClient(...)
        >>> done = tc.task_wait(task_id, timeout=600, polling_interval=60):
        >>> if not done:
        >>>     print("{0} didn't successfully terminate!"
        >>>           .format(task_id))
        >>> else:
        >>>     print("{0} completed".format(task_id))

        You could print dots while you wait for a task by only waiting one
        second at a time:

        >>> tc = TransferClient(...)
        >>> while not tc.task_wait(task_id, timeout=1, polling_interval=1):
        >>>     print(".", end="")
        >>> print("\n{0} completed!".format(task_id))
        """
        task_id_s = utils.safe_stringify(task_id)
        log.info(
            "TransferClient.task_wait({}, {}, {})".format(
                task_id_s, timeout, polling_interval
            )
        )

        # check valid args
        if timeout < 1:
            log.error(f"task_wait() timeout={timeout} is less than minimum of 1s")
            raise exc.GlobusSDKUsageError(
                "TransferClient.task_wait timeout has a minimum of 1"
            )
        if polling_interval < 1:
            log.error(
                "task_wait() polling_interval={} is less than minimum of 1s".format(
                    polling_interval
                )
            )
            raise exc.GlobusSDKUsageError(
                "TransferClient.task_wait polling_interval has a minimum of 1"
            )

        # ensure that we always wait at least one interval, even if the timeout
        # is shorter than the polling interval, by reducing the interval to the
        # timeout if it is larger
        polling_interval = min(timeout, polling_interval)

        # helper for readability
        def timed_out(waited_time):
            return waited_time > timeout

        waited_time = 0
        # doing this as a while-True loop actually makes it simpler than doing
        # while not timed_out(waited_time) because of the end condition
        while True:
            # get task, check if status != ACTIVE
            task = self.get_task(task_id_s)
            status = task["status"]
            if status != "ACTIVE":
                log.debug(
                    "task_wait(task_id={}) terminated with status={}".format(
                        task_id_s, status
                    )
                )
                return True

            # make sure to check if we timed out before sleeping again, so we
            # don't sleep an extra polling_interval
            waited_time += polling_interval
            if timed_out(waited_time):
                log.debug(f"task_wait(task_id={task_id_s}) timed out")
                return False

            log.debug(f"task_wait(task_id={task_id_s}) waiting {polling_interval}s")
            time.sleep(polling_interval)
        # unreachable -- end of task_wait

    def task_pause_info(
        self, task_id: ID_PARAM_TYPE, **params
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /task/<task_id>/pause_info``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Get task pause info \
        <https://docs.globus.org/api/transfer/task/#get_task_pause_info>`_
        in the REST documentation for details.
        """
        task_id_s = utils.safe_stringify(task_id)
        log.info(f"TransferClient.task_pause_info({task_id_s}, ...)")
        resource_path = self.qjoin_path("task", task_id_s, "pause_info")
        return self.get(resource_path, params=params)

    def task_successful_transfers(
        self, task_id: ID_PARAM_TYPE, num_results=100, **params
    ) -> PaginatedResource:
        """
        Get the successful file transfers for a completed Task.

        .. note::

            Only files that were actually transferred are included. This does
            not include directories, files that were checked but skipped as
            part of a sync transfer, or files which were skipped due to
            skip_source_errors being set on the task.

        ``GET /task/<task_id>/successful_transfers``

        :param task_id: The ID of the task to inspect.
        :type task_id: str
        :param num_results: The number of file transfer records to fetch from the
            service. May be set to ``None`` to request the maximum allowable number of
            results. [Default: ``100``]
        :type num_results: int or None, optional
        :param params: Any additional parameters will be passed through as query params.
        :type params: dict, optional
        :rtype: :class:`PaginatedResource
                <globus_sdk.transfer.paging.PaginatedResource>`,
                an iterable of :class:`GlobusResponse
                <globus_sdk.response.GlobusResponse>`

        **Examples**

        Fetch all transferred files for a task and print some basic info:

        >>> tc = TransferClient(...)
        >>> task_id = ...
        >>> for info in tc.task_successful_transfers(task_id):
        >>>     print("{} -> {}".format(
        >>>         info["source_path"], info["destination_path"]))

        **External Documentation**

        See
        `Get Task Successful Transfers\
        <https://docs.globus.org/api/transfer/task/#get_task_successful_transfers>`_
        in the REST documentation for details.
        """
        task_id_s = utils.safe_stringify(task_id)
        log.info(f"TransferClient.task_successful_transfers({task_id_s}, ...)")
        resource_path = self.qjoin_path("task", task_id_s, "successful_transfers")
        return PaginatedResource(
            self.get,
            resource_path,
            {"params": params},
            num_results=num_results,
            max_results_per_call=1000,
            paging_style=PaginatedResource.PAGING_STYLE_MARKER,
        )

    def task_skipped_errors(
        self, task_id: ID_PARAM_TYPE, num_results=100, **params
    ) -> PaginatedResource:
        """
        Get path and error information for all paths that were skipped due
        to skip_source_errors being set on a completed transfer Task.

        ``GET /task/<task_id>/skipped_errors``

        :param task_id: The ID of the task to inspect.
        :type task_id: str
        :param num_results: The number of file transfer records to fetch from the
            service. May be set to ``None`` to request the maximum allowable number of
            results. [Default: ``100``]
        :type num_results: int or None, optional
        :param params: Any additional parameters will be passed through as query params.
        :type params: dict, optional
        :rtype: :class:`PaginatedResource
                <globus_sdk.transfer.paging.PaginatedResource>`,
                an iterable of :class:`GlobusResponse
                <globus_sdk.response.GlobusResponse>`

        **Examples**

        Fetch all skipped errors for a task and print some basic info:

        >>> tc = TransferClient(...)
        >>> task_id = ...
        >>> for info in tc.task_skipped_errors(task_id):
        >>>     print("{} -> {}".format(
        >>>         info["error_code"], info["source_path"]))

        **External Documentation**

        See
        `Get Task Skipped Errors\
        <https://docs.globus.org/api/transfer/task/#get_task_skipped_errors>`_
        in the REST documentation for details.
        """
        task_id_s = utils.safe_stringify(task_id)
        log.info(
            "TransferClient.endpoint_manager_task_skipped_errors(%s, ...)", task_id_s
        )

        resource_path = self.qjoin_path("task", task_id_s, "skipped_errors")
        return PaginatedResource(
            self.get,
            resource_path,
            {"params": params},
            num_results=num_results,
            max_results_per_call=1000,
            paging_style=PaginatedResource.PAGING_STYLE_MARKER,
        )

    #
    # advanced endpoint management (requires endpoint manager role)
    #

    def endpoint_manager_monitored_endpoints(
        self, **params
    ) -> IterableTransferResponse:
        """
        Get endpoints the current user is a monitor or manager on.

        ``GET endpoint_manager/monitored_endpoints``

        :rtype: iterable of :class:`GlobusResponse
                <globus_sdk.response.GlobusResponse>`

        See
        `Get monitored endpoints \
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#get_monitored_endpoints>`_
        in the REST documentation for details.
        """
        log.info(f"TransferClient.endpoint_manager_monitored_endpoints({params})")
        path = self.qjoin_path("endpoint_manager", "monitored_endpoints")
        return IterableTransferResponse(self.get(path, params=params))

    def endpoint_manager_hosted_endpoint_list(
        self, endpoint_id: ID_PARAM_TYPE, **params
    ) -> IterableTransferResponse:
        """
        Get shared endpoints hosted on the given endpoint.

        ``GET /endpoint_manager/endpoint/<endpoint_id>/hosted_endpoint_list``

        :rtype: iterable of :class:`GlobusResponse
                <globus_sdk.response.GlobusResponse>`

        See
        `Get hosted endpoint list \
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#get_hosted_endpoint_list>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(
            f"TransferClient.endpoint_manager_hosted_endpoint_list({endpoint_id_s})"
        )
        path = self.qjoin_path(
            "endpoint_manager", "endpoint", endpoint_id_s, "hosted_endpoint_list"
        )
        return IterableTransferResponse(self.get(path, params=params))

    def endpoint_manager_get_endpoint(
        self, endpoint_id: ID_PARAM_TYPE, **params
    ) -> response.GlobusHTTPResponse:
        """
        Get endpoint details as an admin.

        ``GET /endpoint_manager/endpoint/<endpoint_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Get endpoint as admin \
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#mc_get_endpoint>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.endpoint_manager_get_endpoint({endpoint_id_s})")
        path = self.qjoin_path("endpoint_manager", "endpoint", endpoint_id_s)
        return self.get(path, params=params)

    def endpoint_manager_acl_list(
        self, endpoint_id: ID_PARAM_TYPE, **params
    ) -> IterableTransferResponse:
        """
        Get a list of access control rules on specified endpoint as an admin.

        ``GET endpoint_manager/endpoint/<endpoint_id>/access_list``

        :rtype: :class:`IterableTransferResponse
                <globus_sdk.transfer.response.IterableTransferResponse>`

        **External Documentation**

        See
        `Get endpoint access list as admin \
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#get_endpoint_access_list_as_admin>`_
        in the REST documentation for details.
        """
        endpoint_id_s = utils.safe_stringify(endpoint_id)
        log.info(
            f"TransferClient.endpoint_manager_endpoint_acl_list({endpoint_id_s}, ...)"
        )
        path = self.qjoin_path(
            "endpoint_manager", "endpoint", endpoint_id_s, "access_list"
        )
        return IterableTransferResponse(self.get(path, params=params))

    #
    # endpoint manager task methods
    #

    def endpoint_manager_task_list(self, num_results=10, **params) -> PaginatedResource:
        r"""
        Get a list of tasks visible via ``activity_monitor`` role, as opposed
        to tasks owned by the current user.

        ``GET endpoint_manager/task_list``

        :param num_results: The number of tasks to fetch from the service. May be set to
            ``None`` to request the maximum allowable number of results.
            [Default: ``10``]
        :type num_results: int or None, optional
        :param params: Any additional parameters will be passed through as query params.
        :type params: dict, optional
        :rtype: :class:`PaginatedResource
                <globus_sdk.transfer.paging.PaginatedResource>`,
                an iterable of :class:`GlobusResponse
                <globus_sdk.response.GlobusResponse>`

        **Filters**

        The following filters are supported (passed as keyword arguments in ``params``).
        For any query that doesn’t specify a filter_status that is a subset of
        ("ACTIVE", "INACTIVE"), at least one of filter_task_id or filter_endpoint is
        required.

        ====================== ================ ========================
        Query Parameter        Filter Type      Description
        ====================== ================ ========================
        filter_status          equality list    |filter_status|
        filter_task_id         equality list    |filter_task_id|
        filter_owner_id        equality         |filter_owner_id|
        filter_endpoint        equality         |filter_endpoint|
        filter_is_paused       boolean equality |filter_is_paused|
        filter_completion_time datetime range   |filter_completion_time|
        filter_min_faults      int              |filter_min_faults|
        filter_local_user      equality         |filter_local_user|
        ====================== ================ ========================

        .. |filter_status| replace::
           Comma separated list of task statuses.  Return only tasks with any of the
           specified statuses. Note that in-progress tasks will have status "ACTIVE" or
           "INACTIVE", and completed tasks will have status "SUCCEEDED" or "FAILED".

        .. |filter_task_id| replace::
           Comma separated list of task_ids, limit 50. Return only tasks with any of
           the specified ids. If any of the specified tasks do not involve an endpoint
           the user has an appropriate role for, a ``PermissionDenied`` error will be
           returned. This filter can't be combined with any other filter.  If another
           filter is passed, a ``BadRequest`` will be returned.

        .. |filter_owner_id| replace::
           A Globus Auth identity id. Limit results to tasks submitted by the specified
           identity, or linked to the specified identity, at submit time.  Returns
           ``UserNotFound`` if the identity does not exist or has never used the Globus
           Transfer service. If no tasks were submitted by this user to an endpoint the
           current user has an appropriate role on, an empty result set will be
           returned. Unless filtering for running tasks (i.e. ``filter_status`` is a
           subset of ("ACTIVE", "INACTIVE"), ``filter_endpoint`` is required when using
           ``filter_owner_id``.

        .. |filter_endpoint| replace::
           Single endpoint id or canonical name. Using canonical name is deprecated.
           Return only tasks with a matching source or destination endpoint or matching
           source or destination host endpoint.

        .. |filter_is_paused| replace::
           Return only tasks with the specified ``is_paused`` value. Requires that
           ``filter_status`` is also passed and contains a subset of "ACTIVE" and
           "INACTIVE". Completed tasks always have ``is_paused`` equal to "false" and
           filtering on their paused state is not useful and not supported.  Note that
           pausing is an async operation, and after a pause rule is inserted it will
           take time before the is_paused flag is set on all affected tasks. Tasks
           paused by id will have the ``is_paused`` flag set immediately.

        .. |filter_completion_time| replace::
           Start and end date-times separated by a comma. Each datetime should be
           specified as a string in ISO 8601 format: ``YYYY-MM-DDTHH:MM:SS``, where the
           "T" separating date and time is literal, with optional \+/-HH:MM for
           timezone.  If no timezone is specified, UTC is assumed, or a trailing "Z" can
           be specified to make UTC explicit. A space can be used between the date and
           time instead of a space.  A blank string may be used for either the start or
           end (but not both) to indicate no limit on that side.  Returns only complete
           tasks with ``completion_time`` in the specified range. If the end date is
           blank, it will also include all active tasks, since they will complete some
           time in the future.

        .. |filter_min_faults| replace::
           Minimum number of cumulative faults, inclusive.  Return only tasks with
           ``faults >= N``, where N is the filter value.  Use ``filter_min_faults=1`` to
           find all tasks with at least one fault.  Note that many errors are not fatal
           and the task may still be successful even if ``faults >= 1``.

        .. |filter_local_user| replace::
           A valid username for the target system running the endpoint, as a utf8
           encoded string. Requires that ``filter_endpoint`` is also set. Return only
           tasks that have successfully fetched the local user from the endpoint, and
           match the values of ``filter_endpoint`` and ``filter_local_user`` on the
           source or on the destination.

        **Examples**

        Fetch the default number (10) of tasks and print some basic info:

        >>> tc = TransferClient(...)
        >>> for task in tc.endpoint_manager_task_list(filter_status="ACTIVE"):
        >>>     print("Task({}): {} -> {}\n  was submitted by\n  {}".format(
        >>>         task["task_id"], task["source_endpoint"],
        >>>         task["destination_endpoint"], task["owner_string"]))

        Do that same operation on *all* tasks visible via ``activity_monitor``
        status:

        >>> tc = TransferClient(...)
        >>> for task in tc.endpoint_manager_task_list(
        >>>     num_results=None, filter_status="ACTIVE"
        >>> ):
        >>>     print("Task({}): {} -> {}\n  was submitted by\n  {}".format(
        >>>         task["task_id"], task["source_endpoint"],
        >>>         task["destination_endpoint"], task["owner_string"]))

        **External Documentation**

        See
        `Advanced Endpoint Management: Get tasks \
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#get_tasks>`_
        in the REST documentation for details.
        """
        log.info("TransferClient.endpoint_manager_task_list(...)")
        path = self.qjoin_path("endpoint_manager", "task_list")
        return PaginatedResource(
            self.get,
            path,
            {"params": params},
            num_results=num_results,
            max_results_per_call=1000,
            paging_style=PaginatedResource.PAGING_STYLE_LAST_KEY,
        )

    def endpoint_manager_get_task(self, task_id: ID_PARAM_TYPE, **params):
        """
        Get task info as an admin. Requires activity monitor effective role on
        the destination endpoint of the task.

        ``GET /endpoint_manager/task/<task_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Get task as admin \
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#get_task>`_
        in the REST documentation for details.
        """
        task_id_s = utils.safe_stringify(task_id)
        log.info(f"TransferClient.endpoint_manager_get_task({task_id_s}, ...)")
        path = self.qjoin_path("endpoint_manager", "task", task_id_s)
        return self.get(path, params=params)

    def endpoint_manager_task_event_list(
        self, task_id: ID_PARAM_TYPE, num_results=10, **params
    ) -> PaginatedResource:
        """
        List events (for example, faults and errors) for a given task as an
        admin. Requires activity monitor effective role on the destination
        endpoint of the task.

        ``GET /task/<task_id>/event_list``

        :param task_id: The ID of the task to inspect.
        :type task_id: str
        :param num_results: The number of events to fetch from the service. May be set
            to ``None`` to request the maximum allowable number of results.
            [Default: ``10``]
        :type num_results: int or None, optional
        :param params: Any additional parameters will be passed through as query params.
        :type params: dict, optional
        :rtype: :class:`PaginatedResource
                <globus_sdk.transfer.paging.PaginatedResource>`,
                an iterable of :class:`GlobusResponse
                <globus_sdk.response.GlobusResponse>`

        **External Documentation**

        See
        `Get task events as admin \
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#get_task_events>`_
        in the REST documentation for details.
        """
        task_id_s = utils.safe_stringify(task_id)
        log.info(f"TransferClient.endpoint_manager_task_event_list({task_id_s}, ...)")
        path = self.qjoin_path("endpoint_manager", "task", task_id_s, "event_list")
        return PaginatedResource(
            self.get,
            path,
            {"params": params},
            num_results=num_results,
            max_results_per_call=1000,
            paging_style=PaginatedResource.PAGING_STYLE_TOTAL,
        )

    def endpoint_manager_task_pause_info(
        self, task_id: ID_PARAM_TYPE, **params
    ) -> response.GlobusHTTPResponse:
        """
        Get details about why a task is paused as an admin. Requires activity
        monitor effective role on the destination endpoint of the task.

        ``GET /endpoint_manager/task/<task_id>/pause_info``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Get task pause info as admin \
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#get_task_pause_info_as_admin>`_
        in the REST documentation for details.
        """
        task_id_s = utils.safe_stringify(task_id)
        log.info(f"TransferClient.endpoint_manager_task_pause_info({task_id_s}, ...)")
        path = self.qjoin_path("endpoint_manager", "task", task_id_s, "pause_info")
        return self.get(path, params=params)

    def endpoint_manager_task_successful_transfers(
        self, task_id: ID_PARAM_TYPE, num_results=100, **params
    ) -> PaginatedResource:
        """
        Get the successful file transfers for a completed Task as an admin.

        ``GET /endpoint_manager/task/<task_id>/successful_transfers``

        :param task_id: The ID of the task to inspect.
        :type task_id: str
        :param num_results: The number of file transfer records to fetch from the
            service. May be set to ``None`` to request the maximum allowable number of
            results. [Default: ``100``]
        :type num_results: int or None, optional
        :param params: Any additional parameters will be passed through as query params.
        :type params: dict, optional
        :rtype: :class:`PaginatedResource
                <globus_sdk.transfer.paging.PaginatedResource>`,
                an iterable of :class:`GlobusResponse
                <globus_sdk.response.GlobusResponse>`

        **External Documentation**

        See
        `Get task successful transfers as admin\
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#get_task_successful_transfers_as_admin>`_
        in the REST documentation for details.
        """
        task_id_s = utils.safe_stringify(task_id)
        log.info(
            "TransferClient.endpoint_manager_task_successful_transfers(%s, ...)",
            task_id_s,
        )

        resource_path = self.qjoin_path(
            "endpoint_manager", "task", task_id_s, "successful_transfers"
        )
        return PaginatedResource(
            self.get,
            resource_path,
            {"params": params},
            num_results=num_results,
            max_results_per_call=1000,
            paging_style=PaginatedResource.PAGING_STYLE_MARKER,
        )

    def endpoint_manager_task_skipped_errors(
        self, task_id: ID_PARAM_TYPE, num_results=100, **params
    ) -> PaginatedResource:
        """
        Get skipped errors for a completed Task as an admin.

        ``GET /endpoint_manager/task/<task_id>/skipped_errors``

        :param task_id: The ID of the task to inspect.
        :type task_id: str
        :param num_results: The number of skipped error records to fetch from the
            service. May be set to ``None`` to request the maximum allowable number of
            results. [Default: ``100``]
        :type num_results: int or None, optional
        :param params: Any additional parameters will be passed through as query params.
        :type params: dict, optional
        :rtype: :class:`PaginatedResource
                <globus_sdk.transfer.paging.PaginatedResource>`,
                an iterable of :class:`GlobusResponse
                <globus_sdk.response.GlobusResponse>`

        **External Documentation**

        See
        `Get task skipped errors as admin\
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#get_task_skipped_errors_as_admin>`_
        in the REST documentation for details.
        """
        task_id_s = utils.safe_stringify(task_id)
        log.info(
            f"TransferClient.endpoint_manager_task_skipped_errors({task_id_s}, ...)"
        )

        resource_path = self.qjoin_path(
            "endpoint_manager", "task", task_id_s, "skipped_errors"
        )
        return PaginatedResource(
            self.get,
            resource_path,
            {"params": params},
            num_results=num_results,
            max_results_per_call=1000,
            paging_style=PaginatedResource.PAGING_STYLE_MARKER,
        )

    def endpoint_manager_cancel_tasks(
        self, task_ids: Iterable[ID_PARAM_TYPE], message, **params
    ) -> response.GlobusHTTPResponse:
        """
        Cancel a list of tasks as an admin. Requires activity manager effective
        role on the task(s) source or destination endpoint(s).

        ``POST /endpoint_manager/admin_cancel``

        :param task_ids: List of task ids to cancel.
        :type task_ids: iterable of str
        :param message: Message given to all users who's tasks have been canceled.
        :type message: str
        :param params: Any additional parameters will be passed through as query params.
        :type params: dict, optional
        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Cancel tasks as admin \
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#admin_cancel>`_
        in the REST documentation for details.
        """
        str_task_ids = [utils.safe_stringify(i) for i in task_ids]
        message = utils.safe_stringify(message)
        log.info(
            f"TransferClient.endpoint_manager_cancel_tasks({str_task_ids}, {message})"
        )
        data = {"message": utils.safe_stringify(message), "task_id_list": str_task_ids}
        path = self.qjoin_path("endpoint_manager", "admin_cancel")
        return self.post(path, data=data, params=params)

    def endpoint_manager_cancel_status(
        self, admin_cancel_id, **params
    ) -> response.GlobusHTTPResponse:
        """
        Get the status of an an admin cancel (result of
        endpoint_manager_cancel_tasks).

        ``GET /endpoint_manager/admin_cancel/<admin_cancel_id>``

        :param admin_cancel_id: The ID of the the cancel job to inspect.
        :type admin_cancel_id: str
        :param params: Any additional parameters will be passed through as query params.
        :type params: dict, optional
        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Get cancel status by id \
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#get_cancel_status_by_id>`_
        in the REST documentation for details.
        """
        log.info(f"TransferClient.endpoint_manager_cancel_status({admin_cancel_id})")
        path = self.qjoin_path("endpoint_manager", "admin_cancel", admin_cancel_id)
        return self.get(path, params=params)

    def endpoint_manager_pause_tasks(
        self, task_ids: Iterable[ID_PARAM_TYPE], message, **params
    ) -> response.GlobusHTTPResponse:
        """
        Pause a list of tasks as an admin. Requires activity manager effective
        role on the task(s) source or destination endpoint(s).

        ``POST /endpoint_manager/admin_pause``

        :param task_ids: List of task ids to pause.
        :type task_ids: iterable of str
        :param message: Message given to all users who's tasks have been paused.
        :type message: str
        :param params: Any additional parameters will be passed through as query params.
        :type params: dict, optional
        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Pause tasks as admin \
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#pause_tasks_as_admin>`_
        in the REST documentation for details.
        """
        str_task_ids = [utils.safe_stringify(i) for i in task_ids]
        message = utils.safe_stringify(message)
        log.info(
            f"TransferClient.endpoint_manager_pause_tasks({str_task_ids}, {message})"
        )
        data = {
            "message": utils.safe_stringify(message),
            "task_id_list": str_task_ids,
        }
        path = self.qjoin_path("endpoint_manager", "admin_pause")
        return self.post(path, data=data, params=params)

    def endpoint_manager_resume_tasks(
        self, task_ids: Iterable[ID_PARAM_TYPE], **params
    ) -> response.GlobusHTTPResponse:
        """
        Resume a list of tasks as an admin. Requires activity manager effective
        role on the task(s) source or destination endpoint(s).

        ``POST /endpoint_manager/admin_resume``

        :param task_ids: List of task ids to resume.
        :type task_ids: iterable of str
        :param params: Any additional parameters will be passed through as query params.
        :type params: dict, optional
        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Resume tasks as admin \
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#resume_tasks_as_admin>`_
        in the REST documentation for details.
        """
        str_task_ids = [utils.safe_stringify(i) for i in task_ids]
        log.info(f"TransferClient.endpoint_manager_resume_tasks({str_task_ids})")
        data = {"task_id_list": str_task_ids}
        path = self.qjoin_path("endpoint_manager", "admin_resume")
        return self.post(path, data=data, params=params)

    #
    # endpoint manager pause rule methods
    #

    def endpoint_manager_pause_rule_list(
        self, filter_endpoint: Optional[ID_PARAM_TYPE] = None, **params
    ) -> IterableTransferResponse:
        """
        Get a list of pause rules on endpoints that the current user has the
        activity monitor effective role on.

        ``GET /endpoint_manager/pause_rule_list``

        :param filter_endpoint: An endpoint ID. Limit results to rules on endpoints
            hosted by this endpoint. Must be activity monitor on this endpoint, not just
            the hosted endpoints.
        :type filter_endpoint: str
        :param params: Any additional parameters will be passed through as query params.
        :type params: dict, optional
        :rtype: :class:`IterableTransferResponse
                <globus_sdk.transfer.response.IterableTransferResponse>`

        **External Documentation**

        See
        `Get pause rules \
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#get_pause_rules>`_
        in the REST documentation for details.
        """
        log.info("TransferClient.endpoint_manager_pause_rule_list(...)")
        path = self.qjoin_path("endpoint_manager", "pause_rule_list")
        if filter_endpoint is not None:
            params["filter_endpoint"] = utils.safe_stringify(filter_endpoint)
        return IterableTransferResponse(self.get(path, params=params))

    def endpoint_manager_create_pause_rule(self, data) -> response.GlobusHTTPResponse:
        """
        Create a new pause rule. Requires the activity manager effective role
        on the endpoint defined in the rule.

        ``POST /endpoint_manager/pause_rule``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> rule_data = {
        >>>   "DATA_TYPE": "pause_rule",
        >>>   "message": "Message to users explaining why tasks are paused",
        >>>   "endpoint_id": "339abc22-aab3-4b45-bb56-8d40535bfd80",
        >>>   "identity_id": None,  # affect all users on endpoint
        >>>   "start_time": None  # start now
        >>> }
        >>> create_result = tc.endpoint_manager_create_pause_rule(ep_data)
        >>> rule_id = create_result["id"]

        **External Documentation**

        See
        `Create pause rule \
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#create_pause_rule>`_
        in the REST documentation for details.
        """
        log.info("TransferClient.endpoint_manager_create_pause_rule(...)")
        path = self.qjoin_path("endpoint_manager", "pause_rule")
        return self.post(path, data=data)

    def endpoint_manager_get_pause_rule(
        self, pause_rule_id, **params
    ) -> response.GlobusHTTPResponse:
        """
        Get an existing pause rule by ID. Requires the activity manager
        effective role on the endpoint defined in the rule.

        ``GET /endpoint_manager/pause_rule/<pause_rule_id>``

        :param pause_rule_id: ID of pause rule to get.
        :type pause_rule_id: str
        :param params: Any additional parameters will be passed through as query params.
        :type params: dict, optional
        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Get pause rule \
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#get_pause_rule>`_
        in the REST documentation for details.
        """
        pause_rule_id = utils.safe_stringify(pause_rule_id)
        log.info(f"TransferClient.endpoint_manager_get_pause_rule({pause_rule_id})")
        path = self.qjoin_path("endpoint_manager", "pause_rule", pause_rule_id)
        return self.get(path, params=params)

    def endpoint_manager_update_pause_rule(
        self, pause_rule_id, data
    ) -> response.GlobusHTTPResponse:
        """
        Update an existing pause rule by ID. Requires the activity manager
        effective role on the endpoint defined in the rule.
        Note that non update-able fields in data will be ignored.

        ``PUT /endpoint_manager/pause_rule/<pause_rule_id>``

        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> rule_data = {
        >>>   "message": "Update to pause, reads are now allowed.",
        >>>   "pause_ls": False,
        >>>   "pause_task_transfer_read": False
        >>> }
        >>> update_result = tc.endpoint_manager_update_pause_rule(ep_data)

        **External Documentation**

        See
        `Update pause rule \
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#update_pause_rule>`_
        in the REST documentation for details.
        """
        pause_rule_id = utils.safe_stringify(pause_rule_id)
        log.info(f"TransferClient.endpoint_manager_update_pause_rule({pause_rule_id})")
        path = self.qjoin_path("endpoint_manager", "pause_rule", pause_rule_id)
        return self.put(path, data=data)

    def endpoint_manager_delete_pause_rule(
        self, pause_rule_id, **params
    ) -> response.GlobusHTTPResponse:
        """
        Delete an existing pause rule by ID. Requires the user to see the
        "editible" field of the rule as True. Any tasks affected by this rule
        will no longer be once it is deleted.

        ``DELETE /endpoint_manager/pause_rule/<pause_rule_id>``

        :param pause_rule_id: The ID of the pause rule to delete.
        :type pause_rule_id: str
        :param params: Any additional parameters will be passed through as query params.
        :type params: dict, optional
        :rtype: :class:`TransferResponse
                <globus_sdk.transfer.response.TransferResponse>`

        **External Documentation**

        See
        `Delete pause rule \
        <https://docs.globus.org/api/transfer/advanced_endpoint_management/#delete_pause_rule>`_
        in the REST documentation for details.
        """
        pause_rule_id = utils.safe_stringify(pause_rule_id)
        log.info(f"TransferClient.endpoint_manager_delete_pause_rule({pause_rule_id})")
        path = self.qjoin_path("endpoint_manager", "pause_rule", pause_rule_id)
        return self.delete(path, params=params)
