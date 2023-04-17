from __future__ import annotations

import abc
import typing as t

from globus_sdk import utils
from globus_sdk._types import UUIDLike

from ._common import (
    DatatypeCallback,
    DocumentWithInducedDatatype,
    VersionTuple,
    ensure_datatype,
)

#
# NOTE -- on the organization of arguments in this module --
#
# The arguments to each collection type are defined explicitly for good type annotations
# and documentation.
# However, it's easy for things to get out of sync or different between the various
# locations, so we need to impose some order on things to make comparisons easy.
#
# Complicating this, there are some arguments to specific types which aren't shared
# by the common base.
#
# The rule and rationale used is as follows:
# - DATA_TYPE is special, and always first
# - next, the common optional arguments (shared by all)
# - after that, the specific optional arguments for this type/subtype
# - 'additional_fields' is special, and always last
#
# within those listings of common and specific arguments, the following ordering is
# maintained:
# - strings, sorted alphabetically
# - string lists, sorted alphabetically
# - bools, sorted alphabetically
# - dicts and other types, sorted alphabetically
#
# This makes it possible to do side-by-side comparison of common arguments, to ensure
# that they are all present and accounted-for in all contexts, and allows us to compare
# definition lists for param docs and arguments against usage sites to ensure that all
# arguments which are passed are actually used
#


def _user_message_length_callback(
    obj: DocumentWithInducedDatatype,
) -> VersionTuple | None:
    if (
        "user_message" in obj
        and isinstance(obj["user_message"], str)
        and len(obj["user_message"]) > 64
    ):
        return (1, 7, 0)
    return None


class CollectionDocument(utils.PayloadWrapper, abc.ABC):
    """
    This is the base class for :class:`~.MappedCollectionDocument` and
    :class:`~.GuestCollectionDocument`.

    Parameters common to both of those are defined and documented here.

    :param data_type: Explicitly set the ``DATA_TYPE`` value for this collection.
        Normally ``DATA_TYPE`` is deduced from the provided parameters and should not be
        set. To maximize compatibility with different versions of GCS, only set this
        value when necessary.
    :type data_type: str, optional

    :param collection_base_path: The location of the collection on its underlying
        storage. For a mapped collection, this is an absolute path on the storage system
        named by the ``storage_gateway_id``. For a guest collection, this is a path
        relative to the value of the ``root_path`` attribute on the mapped collection
        identified by the ``mapped_collection_id``. This parameter is optional for
        updates but required when creating a new collection.
    :type collection_base_path: str, optional
    :param contact_email: Email address of the support contact for the collection
    :type contact_email: str, optional
    :param contact_info: Other contact information for the collection, e.g. phone number
        or mailing address
    :type contact_info: str, optional
    :param default_directory: Default directory when using the collection
    :type default_directory: str, optional
    :param department: The department which operates the collection
    :type department: str, optional
    :param description: A text description of the collection
    :type description: str, optional
    :param display_name: Friendly name for the collection
    :type display_name: str, optional
    :param identity_id: The Globus Auth identity which acts as the owner of the
        collection
    :type identity_id: str or UUID, optional
    :param info_link: Link for more info about the collection
    :type info_link: str, optional
    :param organization: The organization which maintains the collection
    :type organization: str, optional
    :param user_message: A message to display to users when interacting with this
        collection
    :type user_message: str, optional
    :param user_message_link: A link to additional messaging for users when interacting
        with this collection
    :type user_message_link: str, optional

    :param keywords: A list of keywords used to help searches for the collection
    :type keywords: iterable of str, optional

    :param disable_verify: Disable verification checksums on transfers to and from this
        collection
    :type disable_verify: bool, optional
    :param enable_https: Enable or disable HTTPS support (requires a managed endpoint)
    :type enable_https: bool, optional
    :param force_encryption: When set to True, all transfers to and from the collection
        are always encrypted
    :type force_encryption: bool, optional
    :param force_verify: Force verification checksums on transfers to and from this
        collection
    :type force_verify: bool, optional
    :param public: If True, the collection will be visible to other Globus users
    :type public: bool, optional

    :param additional_fields: Additional data for inclusion in the collection document
    :type additional_fields: dict, optional
    """

    DATATYPE_BASE: str = "collection"
    DATATYPE_VERSION_IMPLICATIONS: dict[str, tuple[int, int, int]] = {
        "guest_auth_policy_id": (1, 6, 0),
        "disable_anonymous_writes": (1, 5, 0),
        "force_verify": (1, 4, 0),
        "sharing_users_allow": (1, 2, 0),
        "sharing_users_deny": (1, 2, 0),
        "enable_https": (1, 1, 0),
        "user_message": (1, 1, 0),
        "user_message_link": (1, 1, 0),
    }
    DATATYPE_VERSION_CALLBACKS: tuple[DatatypeCallback, ...] = (
        _user_message_length_callback,
    )

    def __init__(
        self,
        *,
        # data_type
        data_type: str | None = None,
        # strs
        collection_base_path: str | None = None,
        contact_email: str | None = None,
        contact_info: str | None = None,
        default_directory: str | None = None,
        department: str | None = None,
        description: str | None = None,
        display_name: str | None = None,
        identity_id: UUIDLike | None = None,
        info_link: str | None = None,
        organization: str | None = None,
        user_message: str | None = None,
        user_message_link: str | None = None,
        # str lists
        keywords: t.Iterable[str] | None = None,
        # bools
        disable_verify: bool | None = None,
        enable_https: bool | None = None,
        force_encryption: bool | None = None,
        force_verify: bool | None = None,
        public: bool | None = None,
        # additional fields
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self["collection_type"] = self.collection_type
        self._set_optstrs(
            DATA_TYPE=data_type,
            collection_base_path=collection_base_path,
            contact_email=contact_email,
            contact_info=contact_info,
            default_directory=default_directory,
            department=department,
            description=description,
            display_name=display_name,
            identity_id=identity_id,
            info_link=info_link,
            organization=organization,
            user_message=user_message,
            user_message_link=user_message_link,
        )
        self._set_optstrlists(
            keywords=keywords,
        )
        self._set_optbools(
            disable_verify=disable_verify,
            enable_https=enable_https,
            force_encryption=force_encryption,
            force_verify=force_verify,
            public=public,
        )
        if additional_fields is not None:
            self.update(additional_fields)

    @property
    @abc.abstractmethod
    def collection_type(self) -> str:
        raise NotImplementedError


class MappedCollectionDocument(CollectionDocument):
    """
    An object used to represent a Mapped Collection for creation or update operations.
    The initializer supports all writable fields on Mapped Collections but does not
    include read-only fields like ``id``.

    Because these documents may be used for updates, no fields are strictly required.
    However, GCS will require the following fields for creation:

    - ``storage_gateway_id``
    - ``collection_base_path``

    All parameters for :class:`~.CollectionDocument` are supported in addition to the
    parameters below.

    :param storage_gateway_id: The ID of the storage gateway which hosts this mapped
        collection. This parameter is required when creating a collection.
    :type storage_gateway_id: str or UUID, optional

    :param domain_name: DNS name of the virtual host serving this collection
    :type domain_name: str, optional
    :param guest_auth_policy_id: Globus Auth policy ID to set on a mapped collection
        which is then inherited by its guest collections.
    :type guest_auth_policy_id: UUID or str, optional

    :param sharing_users_allow: Connector-specific usernames allowed to create guest
        collections
    :type sharing_users_allow: iterable of str, optional
    :param sharing_users_deny: Connector-specific usernames forbidden from creating
        guest collections
    :type sharing_users_deny: iterable of str, optional

    :param allow_guest_collections: Enable or disable creation and use of Guest
        Collections on this Mapped Collection
    :type allow_guest_collections: bool, optional
    :param disable_anonymous_writes: Allow anonymous write ACLs on Guest Collections
        attached to this Mapped Collection. This option is only usable on non
        high-assurance collections
    :type disable_anonymous_writes: bool, optional

    :param policies: Connector-specific collection policies
    :type policies: dict, optional
    :param sharing_restrict_paths: A PathRestrictions document
    :type sharing_restrict_paths: dict, optional
    """

    @property
    def collection_type(self) -> str:
        return "mapped"

    def __init__(
        self,
        *,
        # data type
        data_type: str | None = None,
        # > common args start <
        # strs
        collection_base_path: str | None = None,
        contact_email: str | None = None,
        contact_info: str | None = None,
        default_directory: str | None = None,
        department: str | None = None,
        description: str | None = None,
        display_name: str | None = None,
        identity_id: UUIDLike | None = None,
        info_link: str | None = None,
        organization: str | None = None,
        user_message: str | None = None,
        user_message_link: str | None = None,
        # str lists
        keywords: t.Iterable[str] | None = None,
        # bools
        disable_verify: bool | None = None,
        enable_https: bool | None = None,
        force_encryption: bool | None = None,
        force_verify: bool | None = None,
        public: bool | None = None,
        # > common args end <
        # > specific args start <
        # strs
        domain_name: str | None = None,
        guest_auth_policy_id: UUIDLike | None = None,
        storage_gateway_id: UUIDLike | None = None,
        # str lists
        sharing_users_allow: t.Iterable[str] | None = None,
        sharing_users_deny: t.Iterable[str] | None = None,
        sharing_restrict_paths: dict[str, t.Any] | None = None,
        # bools
        allow_guest_collections: bool | None = None,
        disable_anonymous_writes: bool | None = None,
        # dicts
        policies: (CollectionPolicies | dict[str, t.Any] | None) = None,
        # > specific args end <
        # additional fields
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__(
            # data type
            data_type=data_type,
            # strings
            collection_base_path=collection_base_path,
            contact_email=contact_email,
            contact_info=contact_info,
            default_directory=default_directory,
            department=department,
            description=description,
            display_name=display_name,
            identity_id=identity_id,
            info_link=info_link,
            organization=organization,
            user_message=user_message,
            user_message_link=user_message_link,
            # bools
            disable_verify=disable_verify,
            enable_https=enable_https,
            force_encryption=force_encryption,
            force_verify=force_verify,
            public=public,
            # str lists
            keywords=keywords,
            # additional fields
            additional_fields=additional_fields,
        )
        self._set_optstrs(
            domain_name=domain_name,
            guest_auth_policy_id=guest_auth_policy_id,
            storage_gateway_id=storage_gateway_id,
        )
        self._set_optstrlists(
            sharing_users_allow=sharing_users_allow,
            sharing_users_deny=sharing_users_deny,
        )
        self._set_optbools(
            allow_guest_collections=allow_guest_collections,
            disable_anonymous_writes=disable_anonymous_writes,
        )
        self._set_value("sharing_restrict_paths", sharing_restrict_paths)
        self._set_value("policies", policies, callback=dict)
        ensure_datatype(self)


class GuestCollectionDocument(CollectionDocument):
    """
    An object used to represent a Guest Collection for creation or update operations.
    The initializer supports all writable fields on Guest Collections but does not
    include read-only fields like ``id``.

    Because these documents may be used for updates, no fields are strictly required.
    However, GCS will require the following fields for creation:

    - ``mapped_collection_id``
    - ``user_credential_id``
    - ``collection_base_path``

    All parameters for :class:`~.CollectionDocument` are supported in addition to the
    parameters below.

    :param mapped_collection_id: The ID of the mapped collection which hosts this guest
        collection
    :type mapped_collection_id: str or UUID
    :param user_credential_id: The ID of the User Credential which is used to access
        data on this collection. This credential must be owned by the collection’s
        ``identity_id``.
    :type user_credential_id: str or UUID
    """

    @property
    def collection_type(self) -> str:
        return "guest"

    def __init__(
        self,
        *,
        # data type
        data_type: str | None = None,
        # > common args start <
        # strs
        collection_base_path: str | None = None,
        contact_email: str | None = None,
        contact_info: str | None = None,
        default_directory: str | None = None,
        department: str | None = None,
        description: str | None = None,
        display_name: str | None = None,
        identity_id: UUIDLike | None = None,
        info_link: str | None = None,
        organization: str | None = None,
        user_message: str | None = None,
        user_message_link: str | None = None,
        # str lists
        keywords: t.Iterable[str] | None = None,
        # bools
        disable_verify: bool | None = None,
        enable_https: bool | None = None,
        force_encryption: bool | None = None,
        force_verify: bool | None = None,
        public: bool | None = None,
        # > common args end <
        # > specific args start <
        mapped_collection_id: UUIDLike | None = None,
        user_credential_id: UUIDLike | None = None,
        # > specific args end <
        # additional fields
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__(
            # data type
            data_type=data_type,
            # strings
            collection_base_path=collection_base_path,
            contact_email=contact_email,
            contact_info=contact_info,
            default_directory=default_directory,
            department=department,
            description=description,
            display_name=display_name,
            identity_id=identity_id,
            info_link=info_link,
            organization=organization,
            user_message=user_message,
            user_message_link=user_message_link,
            # bools
            disable_verify=disable_verify,
            enable_https=enable_https,
            force_encryption=force_encryption,
            force_verify=force_verify,
            public=public,
            # str lists
            keywords=keywords,
            # additional fields
            additional_fields=additional_fields,
        )
        self._set_optstrs(
            mapped_collection_id=mapped_collection_id,
            user_credential_id=user_credential_id,
        )
        ensure_datatype(self)


class CollectionPolicies(utils.PayloadWrapper, abc.ABC):
    """
    This is the abstract base type for Collection Policies documents to use as the
    ``policies`` parameter when creating a MappedCollectionDocument.
    """


class POSIXCollectionPolicies(CollectionPolicies):
    """
    Convenience class for constructing a Posix Collection Policy
    document to use as the `policies` parameter when creating a
    CollectionDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param sharing_groups_allow: POSIX groups which are allowed to create guest
        collections.
    :type sharing_groups_allow: iterable of str, optional
    :param sharing_groups_deny: POSIX groups which are not allowed to create guest
        collections.
    :type sharing_groups_deny: iterable of str, optional
    :param additional_fields: Additional data for inclusion in the policy document
    :type additional_fields: dict, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "posix_collection_policies#1.0.0",
        sharing_groups_allow: None | str | t.Iterable[str] = None,
        sharing_groups_deny: None | str | t.Iterable[str] = None,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(DATA_TYPE=DATA_TYPE)
        self._set_optstrlists(
            sharing_groups_allow=sharing_groups_allow,
            sharing_groups_deny=sharing_groups_deny,
        )
        if additional_fields is not None:
            self.update(additional_fields)


class POSIXStagingCollectionPolicies(CollectionPolicies):
    """
    Convenience class for constructing a Posix Staging Collection Policy
    document to use as the ``policies`` parameter when creating a
    CollectionDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param sharing_groups_allow: POSIX groups which are allowed to create guest
        collections.
    :type sharing_groups_allow: iterable of str, optional
    :param sharing_groups_deny: POSIX groups which are not allowed to create guest
        collections.
    :type sharing_groups_deny: iterable of str, optional
    :param additional_fields: Additional data for inclusion in the policy document
    :type additional_fields: dict, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "posix_staging_collection_policies#1.0.0",
        sharing_groups_allow: None | str | t.Iterable[str] = None,
        sharing_groups_deny: None | str | t.Iterable[str] = None,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(DATA_TYPE=DATA_TYPE)
        self._set_optstrlists(
            sharing_groups_allow=sharing_groups_allow,
            sharing_groups_deny=sharing_groups_deny,
        )
        if additional_fields is not None:
            self.update(additional_fields)


class GoogleCloudStorageCollectionPolicies(CollectionPolicies):
    """
    Convenience class for constructing a Google Cloud Storage Collection Policy
    document to use as the ``policies`` parameter when creating a CollectionDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param project: Google Cloud Platform project ID that is used by this collection
    :type project: str, optional
    :param additional_fields: Additional data for inclusion in the policy document
    :type additional_fields: dict, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "google_cloud_storage_collection_policies#1.0.0",
        project: str | None = None,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(DATA_TYPE=DATA_TYPE, project=project)
        if additional_fields is not None:
            self.update(additional_fields)
