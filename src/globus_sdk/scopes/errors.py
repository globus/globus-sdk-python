class ScopeParseError(ValueError):
    """The error raised if scope parsing fails."""


class ScopeCycleError(ScopeParseError):
    """The error raised if scope parsing discovers a cycle."""
