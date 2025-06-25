from .auth import AuthScopes
from .compute import ComputeScopes
from .flows import FlowsScopes, SpecificFlowScopes
from .gcs import GCSCollectionScopes, GCSEndpointScopes
from .groups import GroupsScopes, NexusScopes
from .search import SearchScopes
from .timers import TimersScopes
from .transfer import TransferScopes

__all__ = (
    "AuthScopes",
    "ComputeScopes",
    "FlowsScopes",
    "SpecificFlowScopes",
    "GCSEndpointScopes",
    "GCSCollectionScopes",
    "GroupsScopes",
    "NexusScopes",
    "SearchScopes",
    "TimersScopes",
    "TransferScopes",
)
