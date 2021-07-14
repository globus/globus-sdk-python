class GlobusError(Exception):
    """
    Root of the Globus Exception hierarchy.
    Stub class.
    """


class GlobusSDKUsageError(GlobusError, ValueError):
    """
    A ``GlobusSDKUsageError`` may be thrown in cases in which the SDK
    detects that it is being used improperly.

    These errors typically indicate that some contract regarding SDK usage
    (e.g. required order of operations) has been violated.
    """
