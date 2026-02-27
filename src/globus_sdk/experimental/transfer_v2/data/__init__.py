"""
Data helper classes for constructing Transfer v2 API documents. All classes should
be Payload types, so they can be passed seamlessly to
:class:`TransferClient <globus_sdk.TransferClient>` methods without conversion.
"""

from .tunnel_data import CreateTunnelData

__all__ = ("CreateTunnelData",)
