# test typing interactions with __getattr__-based lazy imports
import globus_sdk

# ensure that a valid name is treated as valid
globus_sdk.TransferClient
# but an invalid name is not!
globus_sdk.TRansferClient  # type: ignore[attr-defined]
