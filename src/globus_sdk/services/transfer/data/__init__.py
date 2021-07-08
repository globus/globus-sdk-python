"""
Data helper classes for constructing Transfer API documents. All classes should
be PayloadWrapper types, so they can be passed seamlessly to
:class:`TransferClient <globus_sdk.TransferClient>` methods without
conversion.
"""

from .delete_data import DeleteData
from .transfer_data import TransferData

__all__ = ("TransferData", "DeleteData")
