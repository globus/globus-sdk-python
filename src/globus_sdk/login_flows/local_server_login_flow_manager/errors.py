class LocalServerLoginError(Exception):
    """An error raised during a LocalServerLoginFlowManager's run."""


class LocalServerEnvironmentalLoginError(LocalServerLoginError):
    """
    Error raised when a local server login flow fails to start due to incompatible
    environment conditions (e.g., a remote session or text-only browser).
    """
