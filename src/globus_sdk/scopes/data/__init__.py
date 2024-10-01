from .auth import AuthScopes
from .compute import ComputeScopes
from .flows import FlowsScopes, SpecificFlowScopeBuilder
from .gcs import GCSCollectionScopeBuilder, GCSEndpointScopeBuilder
from .groups import GroupsScopes, NexusScopes
from .search import SearchScopes
from .timers import TimersScopes
from .transfer import TransferScopes

__all__ = (
    "AuthScopes",
    "ComputeScopes",
    "FlowsScopes",
    "SpecificFlowScopeBuilder",
    "GCSEndpointScopeBuilder",
    "GCSCollectionScopeBuilder",
    "GroupsScopes",
    "NexusScopes",
    "SearchScopes",
    "TimersScopes",
    "TransferScopes",
)
