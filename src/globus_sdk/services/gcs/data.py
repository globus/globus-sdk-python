import abc
from typing import Any, Callable, Dict, Iterable, Optional, Tuple

from globus_sdk import utils
from globus_sdk.types import UUIDLike

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
# - 'additional_fileds' is special, and always last
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

    DATATYPE_VERSION_IMPLICATIONS: Dict[str, Tuple[int, int, int]] = {
        "disable_anonymous_writes": (1, 5, 0),
        "force_verify": (1, 4, 0),
        "sharing_users_allow": (1, 2, 0),
        "sharing_users_deny": (1, 2, 0),
        "enable_https": (1, 1, 0),
        "user_message": (1, 1, 0),
        "user_message_link": (1, 1, 0),
    }

    def __init__(
        self,
        *,
        # data_type
        data_type: Optional[str] = None,
        # strs
        collection_base_path: Optional[str] = None,
        contact_email: Optional[str] = None,
        contact_info: Optional[str] = None,
        default_directory: Optional[str] = None,
        department: Optional[str] = None,
        description: Optional[str] = None,
        display_name: Optional[str] = None,
        identity_id: Optional[UUIDLike] = None,
        info_link: Optional[str] = None,
        organization: Optional[str] = None,
        user_message: Optional[str] = None,
        user_message_link: Optional[str] = None,
        # str lists
        keywords: Optional[Iterable[str]] = None,
        # bools
        disable_verify: Optional[bool] = None,
        enable_https: Optional[bool] = None,
        force_encryption: Optional[bool] = None,
        force_verify: Optional[bool] = None,
        public: Optional[bool] = None,
        # additional fields
        additional_fields: Optional[Dict[str, Any]] = None,
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

    def _deduce_datatype_version(self) -> str:
        max_deduced_version = (1, 0, 0)
        for fieldname, version in self.DATATYPE_VERSION_IMPLICATIONS.items():
            if fieldname not in self:
                continue
            if version > max_deduced_version:
                max_deduced_version = version
        return ".".join(str(x) for x in max_deduced_version)

    def _ensure_datatype(self) -> None:
        if "DATA_TYPE" not in self:
            self["DATA_TYPE"] = f"collection#{self._deduce_datatype_version()}"

    def _set_value(
        self, key: str, val: Any, callback: Optional[Callable[[Any], Any]] = None
    ) -> None:
        if val is not None:
            self[key] = callback(val) if callback else val

    def _set_optstrs(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            self._set_value(k, v, callback=str)

    def _set_optstrlists(self, **kwargs: Optional[Iterable[Any]]) -> None:
        for k, v in kwargs.items():
            self._set_value(k, v, callback=lambda x: list(utils.safe_strseq_iter(x)))

    def _set_optbools(self, **kwargs: Optional[bool]) -> None:
        for k, v in kwargs.items():
            self._set_value(k, v, callback=bool)


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
        data_type: Optional[str] = None,
        # > common args start <
        # strs
        collection_base_path: Optional[str] = None,
        contact_email: Optional[str] = None,
        contact_info: Optional[str] = None,
        default_directory: Optional[str] = None,
        department: Optional[str] = None,
        description: Optional[str] = None,
        display_name: Optional[str] = None,
        identity_id: Optional[UUIDLike] = None,
        info_link: Optional[str] = None,
        organization: Optional[str] = None,
        user_message: Optional[str] = None,
        user_message_link: Optional[str] = None,
        # str lists
        keywords: Optional[Iterable[str]] = None,
        # bools
        disable_verify: Optional[bool] = None,
        enable_https: Optional[bool] = None,
        force_encryption: Optional[bool] = None,
        force_verify: Optional[bool] = None,
        public: Optional[bool] = None,
        # > common args end <
        # > specific args start <
        storage_gateway_id: Optional[UUIDLike] = None,
        # strs
        domain_name: Optional[str] = None,
        # str lists
        sharing_users_allow: Optional[Iterable[str]] = None,
        sharing_users_deny: Optional[Iterable[str]] = None,
        sharing_restrict_paths: Optional[Dict[str, Any]] = None,
        # bools
        allow_guest_collections: Optional[bool] = None,
        disable_anonymous_writes: Optional[bool] = None,
        # dicts
        policies: Optional[Dict[str, Any]] = None,
        # > specific args end <
        # additional fields
        additional_fields: Optional[Dict[str, Any]] = None,
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
            storage_gateway_id=storage_gateway_id,
            domain_name=domain_name,
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
        self._set_value("policies", policies)
        self._ensure_datatype()


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
        data_type: Optional[str] = None,
        # > common args start <
        # strs
        collection_base_path: Optional[str] = None,
        contact_email: Optional[str] = None,
        contact_info: Optional[str] = None,
        default_directory: Optional[str] = None,
        department: Optional[str] = None,
        description: Optional[str] = None,
        display_name: Optional[str] = None,
        identity_id: Optional[UUIDLike] = None,
        info_link: Optional[str] = None,
        organization: Optional[str] = None,
        user_message: Optional[str] = None,
        user_message_link: Optional[str] = None,
        # str lists
        keywords: Optional[Iterable[str]] = None,
        # bools
        disable_verify: Optional[bool] = None,
        enable_https: Optional[bool] = None,
        force_encryption: Optional[bool] = None,
        force_verify: Optional[bool] = None,
        public: Optional[bool] = None,
        # > common args end <
        # > specific args start <
        mapped_collection_id: Optional[UUIDLike] = None,
        user_credential_id: Optional[UUIDLike] = None,
        # > specific args end <
        # additional fields
        additional_fields: Optional[Dict[str, Any]] = None,
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
        self._ensure_datatype()


class GCSRoleDocument(utils.PayloadWrapper):
    """
    Convenience class for constructing a Role document
    to use as the `data` parameter to `create_role`

    :param DATA_TYPE: Versioned document type.
    :type DATA_TYPE: str
    :param collection: Collection ID for the collection the role will apply to.
        This value is omitted when creating an endpoint
        role or when creating role definitions when creating collections.
    :type collection: str or UUID, optional
    :param principal: Auth identity or group id URN. Should be in the format
        urn:globus:auth:[identity|group]:{uuid of identity or group}
    :type principal: str, optional
    :param role: Role assigned to the principal. Known values are owner,
        administrator, access_manager, activity_manager, and activity_monitor
    :type role: str, optional
    """

    def _set_value(
        self, key: str, val: Any, callback: Optional[Callable[[Any], Any]] = None
    ) -> None:
        if val is not None:
            self[key] = callback(val) if callback else val

    def _set_optstrs(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            self._set_value(k, v, callback=str)

    def __init__(
        self,
        DATA_TYPE: str = "role#1.0.0",
        collection: Optional[UUIDLike] = None,
        principal: Optional[str] = None,
        role: Optional[str] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(
            DATA_TYPE=DATA_TYPE,
            collection=collection,
            principal=principal,
            role=role,
        )
        if additional_fields is not None:
            self.update(additional_fields)
