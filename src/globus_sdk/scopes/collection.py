from __future__ import annotations

import abc
import typing as t

from .representation import Scope


class ScopeCollection(abc.ABC):
    """
    The common base for scope collections.

    ScopeCollections act as namespaces with attribute access to get scopes.

    They can also be iterated to get all of their defined scopes and provide
    the appropriate resource_server string for use in OAuth2 flows.
    """

    @property
    @abc.abstractmethod
    def resource_server(self) -> str: ...

    @abc.abstractmethod
    def __iter__(self) -> t.Iterator[Scope]: ...


class StaticScopeCollection(ScopeCollection):
    """
    A static scope collection is a data container which provides various scopes
    as class attributes.

    ``resource_server`` must be available as a class attribute.
    """

    resource_server: t.ClassVar[str]

    def __iter__(self) -> t.Iterator[Scope]:
        for view in (vars(self).values(), vars(self.__class__).values()):
            for value in view:
                if isinstance(value, Scope):
                    yield value


class DynamicScopeCollection(ScopeCollection):
    """
    The base type for dynamic scope collections, where the resource server is
    variable.

    The default implementation takes the resource server as the only init-time
    parameter.

    :param resource_server: The resource_server to use for all scopes attached
        to this scope collection.
    """

    # DynamicScopeCollection classes are expected to provide
    # the scope names which they provide as a classvar
    # these are often properties for dynamic computation
    _scope_names: t.ClassVar[tuple[str, ...]]

    def __init__(self, resource_server: str) -> None:
        self._resource_server = resource_server

    def __iter__(self) -> t.Iterator[Scope]:
        for name in self._scope_names:
            value = getattr(self, name)
            if isinstance(value, Scope):
                yield value

    @property
    def resource_server(self) -> str:
        return self._resource_server


def _urn_scope(resource_server: str, scope_name: str) -> Scope:
    """
    Convert a short name + resource server string to a scope, in the Globus
    Auth URN format.

    Example Usage:

    >>> _urn_scope("transfer.api.globus.org", "all")
    Scope('urn:globus:auth:scope:transfer.api.globus.org:all')

    :param resource_server: The resource server string.
    :param scope_name: The short name for the scope.
    """
    return Scope(f"urn:globus:auth:scope:{resource_server}:{scope_name}")


def _url_scope(resource_server: str, scope_name: str) -> Scope:
    """
    Convert a short name + resource server string to a scope, in the Globus
    Auth URL format.

    Example Usage:

    >>> _url_scope("actions.globus.org", "hello_world")
    Scope('https://auth.globus.org/scopes/actions.globus.org/hello_world')

    :param resource_server: The resource server string.
    :param scope_name: The short name for the scope.
    """
    return Scope(f"https://auth.globus.org/scopes/{resource_server}/{scope_name}")
