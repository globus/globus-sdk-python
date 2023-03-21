import uuid

from globus_sdk import TransferClient, TransferData

# simple usage, ok
tc = TransferClient()
TransferData(tc, "srcep", "destep")

# can set sync level
TransferData(tc, "srcep", "destep", sync_level=1)
TransferData(tc, "srcep", "destep", sync_level="exists")
# unknown int values are allowed
TransferData(tc, "srcep", "destep", sync_level=100)
# unknown str values are rejected (Literal)
TransferData(tc, "srcep", "destep", sync_level="sizes")  # type: ignore[arg-type]

# TransferData.add_filter_rule
tdata = TransferData(tc, uuid.UUID(), uuid.UUID())
tdata.add_filter_rule("*.tgz")
tdata.add_filter_rule("*.tgz", method="exclude")
tdata.add_filter_rule("*.tgz", type="file")
# bad values rejected (Literal)
tdata.add_filter_rule("*.tgz", type="files")  # type: ignore[arg-type]
tdata.add_filter_rule("*.tgz", method="unclude")  # type: ignore[arg-type]
