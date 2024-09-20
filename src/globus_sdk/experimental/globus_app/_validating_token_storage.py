from __future__ import annotations

import typing as t

import globus_sdk
from globus_sdk.tokenstorage import TokenStorage, TokenStorageData

from ._identity_id_reader import IdentityIDReader
from .errors import MissingTokenError

# before_store validators take (validating_token_storage, token_data_by_resource_server)
# and may have any return type
BeforeStoreValidatorT = t.Callable[
    ["ValidatingTokenStorage", t.Mapping[str, TokenStorageData]], t.Any
]
# after_retreive validators take (validating_token_storage, token_data)
# and may have any return type
AfterRetrieveValidatorT = t.Callable[
    ["ValidatingTokenStorage", TokenStorageData], t.Any
]


class ValidatingTokenStorage(TokenStorage):
    """
    A ValidatingTokenStorage wraps another TokenStorage and applies validators when
    storing and retrieving tokens.

    ValidatingTokenStorage is not concerned with the actual storage location of tokens
    but rather validating that they meet requirements.

    :param token_storage: The token storage being wrapped.
    :param before_store_validators: An iterable of validators to use before storing
        token data. These take the full ``{resource_server: token_data}`` mapping and
        raise errors if validation fails.
    :param after_retrieve_validators: An iterable of validators to use after retrieving
        token data. These take the individual ``token_data`` may raise errors if
        validation fails.
    """

    def __init__(
        self,
        token_storage: TokenStorage,
        *,
        before_store_validators: t.Iterable[BeforeStoreValidatorT] = (),
        after_retrieve_validators: t.Iterable[AfterRetrieveValidatorT] = (),
    ) -> None:
        self.token_storage = token_storage
        self.before_store_validators: list[BeforeStoreValidatorT] = list(
            before_store_validators
        )
        self.after_retrieve_validators: list[AfterRetrieveValidatorT] = list(
            after_retrieve_validators
        )
        self._identity_id_reader = IdentityIDReader()
        self._identity_id_reader.read_token_storage(token_storage)
        super().__init__(namespace=token_storage.namespace)

    @property
    def identity_id(self) -> str | None:
        """
        The identity_id associated with the token data stored in this
        ValidatingTokenStorage.
        """
        return self._identity_id_reader.identity_id

    def store_token_data_by_resource_server(
        self, token_data_by_resource_server: t.Mapping[str, TokenStorageData]
    ) -> None:
        """
        :param token_data_by_resource_server: A dict of TokenStorageData objects
            indexed by their resource server
        """
        for validator in self.before_store_validators:
            validator(self, token_data_by_resource_server)

        self._identity_id_reader.read_token_data_by_resource_server(
            token_data_by_resource_server
        )
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

        for validator in self.after_retrieve_validators:
            validator(self, token_data)

        return token_data

    def get_token_data_by_resource_server(self) -> dict[str, TokenStorageData]:
        all_data = self.token_storage.get_token_data_by_resource_server()
        for token_data in all_data.values():
            for validator in self.after_retrieve_validators:
                validator(self, token_data)
        return all_data

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
