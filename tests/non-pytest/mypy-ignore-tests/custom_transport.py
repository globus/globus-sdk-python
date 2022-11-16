from globus_sdk.transport import RequestsTransport


# customize the status code tuples
# make sure mypy does not reject these changes for updating the tuple sizes
class CustomRetryStatusTransport(RequestsTransport):
    RETRY_AFTER_STATUS_CODES = (503,)
    TRANSIENT_ERROR_STATUS_CODES = (500,)
    EXPIRED_AUTHORIZATION_STATUS_CODES = (401, 403)
