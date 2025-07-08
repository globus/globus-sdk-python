from __future__ import annotations

import copy
import typing as t

from globus_sdk._internal.remarshal import list_map, listify, strseq_listify
from globus_sdk._missing import MISSING, MissingType
from globus_sdk._payload import AbstractGlobusPayload, GlobusPayload
from globus_sdk._types import UUIDLike

from ._common import DatatypeCallback, ensure_datatype


class StorageGatewayDocument(GlobusPayload):
    """
    Convenience class for constructing a Storage Gateway document
    to use as the `data` parameter to ``create_storage_gateway`` or
    ``update_storage_gateway``

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :param display_name: Name of the Storage Gateway
    :param connector_id: UUID of the connector type that this Storage Gateway interacts
        with.
    :param identity_mappings: A list of IdentityMapping objects which are applied to
        user identities to attempt to determine what accounts are available for access.
    :param policies: Connector specific storage policies. It is recommended that
        you use one of the policy helper classes (e.g. `POSIXStoragePolicies`
        if you are using the POSIX connector) to create these.
    :param allowed_domains: List of allowed domains. Users creating credentials or
        collections on this Storage Gateway must have an identity in one of these
        domains.
    :param restrict_paths: Path restrictions within this Storage Gateway. Private.
    :param high_assurance: Flag indicating if the Storage Gateway requires high
        assurance features.
    :param authentication_timeout_mins: Timeout (in minutes) during which a user is
        required to have authenticated in a session to access this storage gateway.
    :param users_allow:  List of connector-specific usernames allowed to access this
        Storage Gateway. Private.
    :param users_deny: List of connector-specific usernames denied access to this
        Storage Gateway. Private.
    :param process_user: Local POSIX user the GridFTP server should run as when
        accessing this Storage Gateway.
    :param load_dsi_module: Name of the DSI module to load by the GridFTP server when
        accessing this Storage Gateway.
    :param require_mfa: Flag indicating that the Storage Gateway requires multi-factor
        authentication. Only usable on high assurance Storage Gateways.

    :param additional_fields: Additional data for inclusion in the Storage Gateway
        document
    """

    DATATYPE_BASE: str = "storage_gateway"
    DATATYPE_VERSION_IMPLICATIONS: dict[str, tuple[int, int, int]] = {
        "require_mfa": (1, 1, 0),
    }
    DATATYPE_VERSION_CALLBACKS: tuple[DatatypeCallback, ...] = ()

    def __init__(
        self,
        DATA_TYPE: str | MissingType = MISSING,
        display_name: str | MissingType = MISSING,
        connector_id: UUIDLike | MissingType = MISSING,
        root: str | MissingType = MISSING,
        identity_mappings: t.Iterable[dict[str, t.Any]] | MissingType = MISSING,
        policies: StorageGatewayPolicies | dict[str, t.Any] | MissingType = MISSING,
        allowed_domains: t.Iterable[str] | MissingType = MISSING,
        high_assurance: bool | MissingType = MISSING,
        require_mfa: bool | MissingType = MISSING,
        authentication_timeout_mins: int | MissingType = MISSING,
        users_allow: t.Iterable[str] | MissingType = MISSING,
        users_deny: t.Iterable[str] | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self["DATA_TYPE"] = DATA_TYPE
        self["display_name"] = display_name
        self["connector_id"] = connector_id
        self["root"] = root
        self["allowed_domains"] = strseq_listify(allowed_domains)
        self["users_allow"] = strseq_listify(users_allow)
        self["users_deny"] = strseq_listify(users_deny)
        self["high_assurance"] = high_assurance
        self["require_mfa"] = require_mfa
        self["authentication_timeout_mins"] = authentication_timeout_mins
        self["identity_mappings"] = listify(identity_mappings)
        self["policies"] = policies
        self.update(additional_fields or {})
        ensure_datatype(self)


class StorageGatewayPolicies(AbstractGlobusPayload):
    """
    This is the abstract base type for Storage Policies documents to use as the
    ``policies`` parameter when creating a StorageGatewayDocument.

    Several fields on policy documents are marked as ``Private``. This means that they
    are not visible except to admins and owners of the storage gateway.
    """


class POSIXStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a POSIX Storage Policy document
    to use as the ``policies`` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :param groups_allow: List of POSIX group IDs allowed to access this Storage
        Gateway. Private.
    :param groups_deny: List of POSIX group IDs denied access this Storage
        Gateway. Private.
    :param additional_fields: Additional data for inclusion in the policy document
    """

    def __init__(
        self,
        DATA_TYPE: str = "posix_storage_policies#1.0.0",
        groups_allow: t.Iterable[str] | MissingType = MISSING,
        groups_deny: t.Iterable[str] | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self["DATA_TYPE"] = DATA_TYPE
        self["groups_allow"] = strseq_listify(groups_allow)
        self["groups_deny"] = strseq_listify(groups_deny)
        self.update(additional_fields or {})


class POSIXStagingStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a POSIX Staging Storage Policy document
    to use as the ``policies`` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :param groups_allow: List of POSIX group IDs allowed to access this Storage
        Gateway. Private.
    :param groups_deny: List of POSIX group IDs denied access this Storage
        Gateway. Private.
    :param stage_app: Path to the stage app. Private.
    :param environment: A mapping of variable names to values to set in the environment
        when executing the ``stage_app``. Private.
    :param additional_fields: Additional data for inclusion in the policy document
    """

    def __init__(
        self,
        DATA_TYPE: str = "posix_staging_storage_policies#1.0.0",
        groups_allow: t.Iterable[str] | MissingType = MISSING,
        groups_deny: t.Iterable[str] | MissingType = MISSING,
        stage_app: str | MissingType = MISSING,
        environment: t.Iterable[dict[str, str]] | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self["DATA_TYPE"] = DATA_TYPE
        self["stage_app"] = stage_app
        self["groups_allow"] = strseq_listify(groups_allow)
        self["groups_deny"] = strseq_listify(groups_deny)
        # make shallow copies of all the dicts passed
        self["environment"] = list_map(environment, copy.copy)
        self.update(additional_fields or {})


class BlackPearlStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a BlackPearl Storage Policy document
    to use as the ``policies`` parameter when creating a StorageGatewayDocument.

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :param s3_endpoint: The URL of the S3 endpoint of the BlackPearl appliance to use to
        access collections on this Storage Gateway.
    :param bp_access_id_file: Path to the file which provides mappings from usernames
        within the configured identity domain to the ID and secret associated with the
        user's BlackPearl account
    :param additional_fields: Additional data for inclusion in the policy document
    """

    def __init__(
        self,
        DATA_TYPE: str = "blackpearl_storage_policies#1.0.0",
        s3_endpoint: str | MissingType = MISSING,
        bp_access_id_file: str | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self["DATA_TYPE"] = DATA_TYPE
        self["s3_endpoint"] = s3_endpoint
        self["bp_access_id_file"] = bp_access_id_file
        self.update(additional_fields or {})


class BoxStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a Box Storage Policy document
    to use as the ``policies`` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :param enterpriseID: Identifies which Box Enterprise this Storage Gateway is
        authorized to access. Private.
    :param boxAppSettings: Values that the Storage Gateway uses to identify and
        authenticate with the Box API. Private.
    :param additional_fields: Additional data for inclusion in the policy document
    """

    def __init__(
        self,
        DATA_TYPE: str = "box_storage_policies#1.0.0",
        enterpriseID: str | MissingType = MISSING,
        boxAppSettings: dict[str, t.Any] | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self["DATA_TYPE"] = DATA_TYPE
        self["enterpriseID"] = enterpriseID
        self["boxAppSettings"] = boxAppSettings
        self.update(additional_fields or {})


class CephStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a Ceph Storage Policy document
    to use as the `policies` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :param s3_endpoint: URL of the S3 API endpoint
    :param s3_buckets: List of buckets not owned by the collection owner that will be
        shown in the root of collections created at the base of this Storage Gateway.
    :param ceph_admin_key_id: Administrator key id used to authenticate with the ceph
        admin service to obtain user credentials. Private.
    :param ceph_admin_secret_key: Administrator secret key used to authenticate with the
        ceph admin service to obtain user credentials. Private.
    :param additional_fields: Additional data for inclusion in the policy document
    """

    def __init__(
        self,
        DATA_TYPE: str = "ceph_storage_policies#1.0.0",
        s3_endpoint: str | MissingType = MISSING,
        s3_buckets: t.Iterable[str] | MissingType = MISSING,
        ceph_admin_key_id: str | MissingType = MISSING,
        ceph_admin_secret_key: str | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self["DATA_TYPE"] = DATA_TYPE
        self["s3_endpoint"] = s3_endpoint
        self["ceph_admin_key_id"] = ceph_admin_key_id
        self["ceph_admin_secret_key"] = ceph_admin_secret_key
        self["s3_buckets"] = strseq_listify(s3_buckets)
        self.update(additional_fields or {})


class GoogleDriveStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a Google Drive Storage Policy document
    to use as the `policies` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :param client_id: Client ID registered with the Google Application console to access
        Google Drive. Private.
    :param secret: Secret created to access access Google Drive with the client_id in
        this policy. Private.
    :param user_api_rate_quota: User API Rate quota associated with this client ID.
    :param additional_fields: Additional data for inclusion in the policy document
    """

    def __init__(
        self,
        DATA_TYPE: str = "google_drive_storage_policies#1.0.0",
        client_id: str | MissingType = MISSING,
        secret: str | MissingType = MISSING,
        user_api_rate_quota: int | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self["DATA_TYPE"] = DATA_TYPE
        self["client_id"] = client_id
        self["secret"] = secret
        self["user_api_rate_quota"] = user_api_rate_quota
        self.update(additional_fields or {})


class GoogleCloudStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a Google Cloud Storage Policy document
    to use as the `policies` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :param client_id: Client ID registered with the Google Application console to
        access Google Drive. Private.
    :param secret: Secret created to access access Google Drive with the client_id in
        this policy. Private.
    :param service_account_key: Credentials for use with service account auth, read
        from a Google-provided json file. Private.
    :param buckets: The list of Google Cloud Storage buckets which the Storage
        Gateway is allowed to access, as well as the list of buckets that will be
        shown in root level directory listings. If this list is unset, bucket
        access is unrestricted and all non public credential accessible buckets
        will be shown in root level directory listings. The value is a list of
        bucket names.
    :param projects: The list of Google Cloud Storage projects which the
        Storage Gateway is allowed to access. If this list is unset, project access
        is unrestricted.  The value is a list of project id strings.
    :param additional_fields: Additional data for inclusion in the policy document
    """

    def __init__(
        self,
        DATA_TYPE: str = "google_cloud_storage_policies#1.0.0",
        client_id: str | MissingType = MISSING,
        secret: str | MissingType = MISSING,
        service_account_key: dict[str, t.Any] | MissingType = MISSING,
        buckets: t.Iterable[str] | MissingType = MISSING,
        projects: t.Iterable[str] | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self["DATA_TYPE"] = DATA_TYPE
        self["client_id"] = client_id
        self["secret"] = secret
        self["buckets"] = strseq_listify(buckets)
        self["projects"] = strseq_listify(projects)
        self["service_account_key"] = service_account_key
        self.update(additional_fields or {})


class OneDriveStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a OneDrive Storage Policy document
    to use as the `policies` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :param client_id: Client ID registered with the MS Application console to
        access OneDrive. Private.
    :param secret: Secret created to access access MS with the client_id in
        this policy. Private.
    :param tenant: MS Tenant ID from which to allow user logins. Private.
    :param user_api_rate_limit: User API Rate limit associated with this client ID.
    :param additional_fields: Additional data for inclusion in the policy document
    """

    def __init__(
        self,
        DATA_TYPE: str = "onedrive_storage_policies#1.0.0",
        client_id: str | MissingType = MISSING,
        secret: str | MissingType = MISSING,
        tenant: str | MissingType = MISSING,
        user_api_rate_limit: int | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self["DATA_TYPE"] = DATA_TYPE
        self["client_id"] = client_id
        self["secret"] = secret
        self["tenant"] = tenant
        self["user_api_rate_limit"] = user_api_rate_limit
        self.update(additional_fields or {})


class AzureBlobStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a Azure Blob Storage Policy document
    to use as the `policies` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :param client_id: Client ID registered with the MS Application console to
        access Azure Blob Private.
    :param secret: Secret created to access access MS with the client_id in
        this policy. Private.
    :param tenant: MS Tenant ID from which to allow user logins. Private.
    :param account: Azure Storage account. Private.
    :param auth_type: Auth type: user, service_principal or user_service_principal
    :param adls: ADLS support enabled or not. Private.
    :param additional_fields: Additional data for inclusion in the policy document
    """

    def __init__(
        self,
        DATA_TYPE: str = "azure_blob_storage_policies#1.0.0",
        client_id: str | MissingType = MISSING,
        secret: str | MissingType = MISSING,
        tenant: str | MissingType = MISSING,
        account: str | MissingType = MISSING,
        auth_type: str | MissingType = MISSING,
        adls: bool | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self["DATA_TYPE"] = DATA_TYPE
        self["client_id"] = client_id
        self["secret"] = secret
        self["tenant"] = tenant
        self["account"] = account
        self["auth_type"] = auth_type
        self["adls"] = adls
        self.update(additional_fields or {})


class S3StoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a Google Cloud Storage Policy document
    to use as the `policies` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :param s3_endpoint: URL of the S3 API endpoint
    :param s3_buckets: List of buckets not owned by the collection owner that
        will be shown in the root of collections created at the base of this
        Storage Gateway.
    :param s3_user_credential_required: Flag indicating if a Globus User must
        register a user credential in order to create a Guest Collection on this
        Storage Gateway.
    :param additional_fields: Additional data for inclusion in the policy document
    """

    def __init__(
        self,
        DATA_TYPE: str = "s3_storage_policies#1.0.0",
        s3_endpoint: str | MissingType = MISSING,
        s3_buckets: t.Iterable[str] | MissingType = MISSING,
        s3_user_credential_required: bool | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self["DATA_TYPE"] = DATA_TYPE
        self["s3_endpoint"] = s3_endpoint
        self["s3_user_credential_required"] = s3_user_credential_required
        self["s3_buckets"] = strseq_listify(s3_buckets)
        self.update(additional_fields or {})


class ActiveScaleStoragePolicies(S3StoragePolicies):
    """
    The ActiveScale Storage Policy is an alias for the S3 Storage Policy.
    It even uses S3 policy DATA_TYPE.
    """


class IrodsStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing an iRODS Storage Policy document
    to use as the `policies` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :param irods_environment_file: Path to iRODS environment file on the endpoint
    :param irods_authentication_file: Path to iRODS authentication file on the endpoint
    :param additional_fields: Additional data for inclusion in the policy document
    """

    def __init__(
        self,
        DATA_TYPE: str = "irods_storage_policies#1.0.0",
        irods_environment_file: str | MissingType = MISSING,
        irods_authentication_file: str | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self["DATA_TYPE"] = DATA_TYPE
        self["irods_environment_file"] = irods_environment_file
        self["irods_authentication_file"] = irods_authentication_file
        self.update(additional_fields or {})


class HPSSStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a HPSS Storage Policy document
    to use as the `policies` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :param authentication_mech: Authentication mechanism to use with HPSS.
    :param authenticator: Authentication credentials to use with HPSS.
    :param uda_checksum_support: Flag indicating whether checksums should be
        stored in metadata.
    :param additional_fields: Additional data for inclusion in the policy document
    """

    def __init__(
        self,
        DATA_TYPE: str = "hpss_storage_policies#1.0.0",
        authentication_mech: str | MissingType = MISSING,
        authenticator: str | MissingType = MISSING,
        uda_checksum_support: bool | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__()
        self["DATA_TYPE"] = DATA_TYPE
        self["authentication_mech"] = authentication_mech
        self["authenticator"] = authenticator
        self["uda_checksum_support"] = uda_checksum_support
        self.update(additional_fields or {})
