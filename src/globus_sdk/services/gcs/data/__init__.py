from .collection import (
    CollectionDocument,
    CollectionPolicies,
    GoogleCloudStorageCollectionPolicies,
    GuestCollectionDocument,
    MappedCollectionDocument,
    POSIXCollectionPolicies,
    POSIXStagingCollectionPolicies,
)
from .endpoint import EndpointDocument
from .role import GCSRoleDocument
from .storage_gateway import (
    ActiveScaleStoragePolicies,
    AzureBlobStoragePolicies,
    BlackPearlStoragePolicies,
    BoxStoragePolicies,
    CephStoragePolicies,
    GoogleCloudStoragePolicies,
    GoogleDriveStoragePolicies,
    HPSSStoragePolicies,
    IrodsStoragePolicies,
    OneDriveStoragePolicies,
    POSIXStagingStoragePolicies,
    POSIXStoragePolicies,
    S3StoragePolicies,
    StorageGatewayDocument,
    StorageGatewayPolicies,
)
from .user_credential import UserCredentialDocument

__all__ = (
    # endpoint documents
    "EndpointDocument",
    # collection documents
    "MappedCollectionDocument",
    "GuestCollectionDocument",
    "CollectionDocument",
    # collection document second-order helpers
    "CollectionPolicies",
    "POSIXCollectionPolicies",
    "POSIXStagingCollectionPolicies",
    "GoogleCloudStorageCollectionPolicies",
    # role document
    "GCSRoleDocument",
    # storage gateway document
    "StorageGatewayDocument",
    # storage gateway document second-order helpers
    "StorageGatewayPolicies",
    "POSIXStoragePolicies",
    "POSIXStagingStoragePolicies",
    "BlackPearlStoragePolicies",
    "BoxStoragePolicies",
    "CephStoragePolicies",
    "GoogleDriveStoragePolicies",
    "GoogleCloudStoragePolicies",
    "OneDriveStoragePolicies",
    "AzureBlobStoragePolicies",
    "S3StoragePolicies",
    "ActiveScaleStoragePolicies",
    "IrodsStoragePolicies",
    "HPSSStoragePolicies",
    # user credential document
    "UserCredentialDocument",
)
