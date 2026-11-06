import globus_sdk
from globus_sdk.paging import Paginator

tc = globus_sdk.TransferClient()


# return type should be IterableTransferResponse
# confirm that it is not altered by the decorator
r: globus_sdk.IterableTransferResponse = tc.task_list()
i: int = tc.task_list()  # type: ignore [assignment]
tc.task_list(limit=10, offset=100, filter="hi")
tc.task_list(limit="hi")  # type: ignore [arg-type]

# too many positional args is 'call-arg'
# we also will trigger arg type because `str` does not match the first kwarg (limit)
# of type `int`
tc.task_list("foo")  # type: ignore [call-arg,arg-type]


# the same basic should hold for a Paginator.wrap'ed variant
# but the return type should be a paginator of responses
paginated_call = Paginator.wrap(tc.task_list)
paged_r: Paginator[globus_sdk.IterableTransferResponse] = paginated_call()
i = paginated_call()  # type: ignore [assignment]
paginated_call(limit=10, offset=100, filter="hi")
paginated_call(limit="hi")  # type: ignore [arg-type]

# see note above on non-paginated case for why these ignores are correct
paginated_call("foo")  # type: ignore [call-arg,arg-type]
