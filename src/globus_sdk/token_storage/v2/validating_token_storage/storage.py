from __future__ import annotations

import typing as t

import globus_sdk

from ..base import TokenStorage
from ..token_data import TokenStorageData
from .context import TokenValidationContext
from .errors import MissingTokenError
from .validators import TokenDataValidator


class ValidatingTokenStorage(TokenStorage):
    """
    A special token storage which provides token data validation hooks.

    See :class:`TokenDataValidator` for details on hook specifics.

    See :class:`TokenStorage` for common interface details.

    :param token_storage: A proxy token storage for this class to pass through store,
        get, and remove requests to.
    :param validators: A collection of validation hooks to call.

    :ivar str | None identity_id: The primary identity ID of the entity which granted
        tokens, if known.
    """

    def __init__(
        self,
        token_storage: TokenStorage,
        *,
        validators: t.Iterable[TokenDataValidator] = (),
    ) -> None:
        self.token_storage = token_storage
        self.validators: list[TokenDataValidator] = list(validators)
        self.identity_id = _identity_id_from_token_data(
            token_storage.get_token_data_by_resource_server()
        )
        super().__init__(namespace=token_storage.namespace)

    def _make_context(
        self, token_data_by_resource_server: t.Mapping[str, TokenStorageData]
    ) -> TokenValidationContext:
        """
        Build a TokenValidationContext object and potentially update the stored
        ``identity_id`` information in this ValidatingTokenStorage.

        Importantly, this records ``self.identity_id`` into the ``prior_identity_id``
        slot before applying this update.
        """
        context = TokenValidationContext(
            prior_identity_id=self.identity_id,
            token_data_identity_id=_identity_id_from_token_data(
                token_data_by_resource_server
            ),
        )

        if self.identity_id is None:
            self.identity_id = context.token_data_identity_id

        return context

    def store_token_data_by_resource_server(
        self, token_data_by_resource_server: t.Mapping[str, TokenStorageData]
    ) -> None:
        """
        :param token_data_by_resource_server: A dict of TokenStorageData objects
            indexed by their resource server
        """
        context = self._make_context(token_data_by_resource_server)
        for validator in self.validators:
            validator.before_store(token_data_by_resource_server, context)

        self.token_storage.store_token_data_by_resource_server(
            token_data_by_resource_server
        )

    def get_token_data(self, resource_server: str) -> TokenStorageData:
        """
        :param resource_server: A resource server with cached token data.
        :returns: The token data for the given resource server.
        :raises: :exc:`MissingTokenError` if the underlying ``TokenStorage`` does not
            have any token data for the given resource server.
        """
        token_data = self.token_storage.get_token_data(resource_server)
        if token_data is None:
            msg = f"No token data for {resource_server}"
            raise MissingTokenError(msg, resource_server=resource_server)

        token_data_by_resource_server = {token_data.resource_server: token_data}
        context = self._make_context(token_data_by_resource_server)

        for validator in self.validators:
            validator.after_retrieve(token_data_by_resource_server, context)

        return token_data

    def get_token_data_by_resource_server(self) -> dict[str, TokenStorageData]:
        token_data_by_resource_server = (
            self.token_storage.get_token_data_by_resource_server()
        )
        context = self._make_context(token_data_by_resource_server)
        for validator in self.validators:
            validator.after_retrieve(token_data_by_resource_server, context)
        return token_data_by_resource_server

    def remove_token_data(self, resource_server: str) -> bool:
        """
        :param resource_server: The resource server string to remove token data for
        """
        return self.token_storage.remove_token_data(resource_server)

    def _extract_identity_id(
        self, token_response: globus_sdk.OAuthTokenResponse
    ) -> str | None:
        """
        Override determination of the identity_id for a token response.

        When handling a refresh token, use the stored identity ID if possible.
        Otherwise, call the inner token storage's method of lookup.
        """
        if isinstance(token_response, globus_sdk.OAuthRefreshTokenResponse):
            return self.identity_id
        else:
            return self.token_storage._extract_identity_id(token_response)


def _identity_id_from_token_data(
    token_data_by_resource_server: t.Mapping[str, TokenStorageData],
) -> str | None:
    """
    Read token data by resource server and return the ``identity_id`` value
    which was produced.

    :param token_data_by_resource_server: The token data to read for identity_id.

    :raises ValueError: if there is inconsistent ``identity_id`` information
    """
    token_data_identity_ids: set[str] = {
        token_data.identity_id
        for token_data in token_data_by_resource_server.values()
        if token_data.identity_id is not None
    }

    if len(token_data_identity_ids) == 0:
        return None
    elif len(token_data_identity_ids) == 1:
        return token_data_identity_ids.pop()
    else:
        raise ValueError(
            "token_data_by_resource_server contained TokenStorageData objects with "
            f"different identity_id values: {token_data_identity_ids}"
        )
