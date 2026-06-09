# binding for dumps/loads which prefers orjson if it's available
import json

from globus_sdk._internal import orjson_compat

JSONDecodeError = json.JSONDecodeError

if orjson_compat.ORJSON_AVAILABLE:

    def dumps(data):
        return orjson_compat.dumps(data).decode()

    loads = orjson_compat.loads
else:
    dumps = json.dumps
    loads = json.loads
