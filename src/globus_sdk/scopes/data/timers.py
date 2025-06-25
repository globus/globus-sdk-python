from ..collection import StaticScopeCollection, _url_scope


class _TimersScopes(StaticScopeCollection):
    resource_server = "524230d7-ea86-4a52-8312-86065a9e0417"

    timer = _url_scope(resource_server, "timer")


TimersScopes = _TimersScopes()
