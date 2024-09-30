class GlobusError(Exception):
    """
    Root of the Globus Exception hierarchy.
    """


class GlobusSDKUsageError(GlobusError, ValueError):
    """
    A ``GlobusSDKUsageError`` may be thrown in cases in which the SDK
    detects that it is being used improperly.

    These errors typically indicate that some contract regarding SDK usage
    (e.g. required order of operations) has been violated.
    """


class ValidationError(GlobusError, ValueError):
    """
    A ``ValidationError`` may be raised when the SDK is instructed to handle or
    parse data which can be seen to be invalid without an external service
    interaction.

    These errors typically do not indicate a usage error similar to
    ``GlobusSDKUsageError``, but rather that the data is invalid.
    """
