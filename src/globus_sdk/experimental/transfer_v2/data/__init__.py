"""
Data helper classes for constructing Transfer v2 API documents. All classes should
be Payload types, so they can be passed seamlessly to
:class:`TransferClient <globus_sdk.TransferClient>` methods without conversion.
"""

from .bookmark_documents import BookmarkCreateDocument, BookmarkUpdateDocument
from .tunnel_documents import TunnelCreateDocument, TunnelUpdateDocument

__all__ = (
    "BookmarkCreateDocument",
    "BookmarkUpdateDocument",
    "TunnelCreateDocument",
    "TunnelUpdateDocument",
)
