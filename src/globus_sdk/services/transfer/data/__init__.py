"""
Data helper classes for constructing Transfer API documents. All classes should
be Payload types, so they can be passed seamlessly to
:class:`TransferClient <globus_sdk.TransferClient>` methods without conversion.
"""

# CreateTunnelData has been moved to experimental.transfer_v2 but is
# provided here for backwards compatibility
from globus_sdk.experimental.transfer_v2.data import CreateTunnelData

from .delete_data import DeleteData
from .transfer_data import TransferData

__all__ = ("TransferData", "DeleteData", "CreateTunnelData")
