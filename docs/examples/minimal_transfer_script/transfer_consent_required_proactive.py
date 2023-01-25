import argparse

import globus_sdk
from globus_sdk.scopes import TransferScopes

parser = argparse.ArgumentParser()
parser.add_argument("SRC")
parser.add_argument("DST")
args = parser.parse_args()

CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
auth_client = globus_sdk.NativeAppAuthClient(CLIENT_ID)


# we will need to do the login flow potentially twice, so define it as a
# function
#
# we default to using the Transfer "all" scope, but it is settable here
# look at the ConsentRequired handler below for how this is used
def login_and_get_transfer_client(*, scopes=TransferScopes.all):
    # note that 'requested_scopes' can be a single scope or a list
    # this did not matter in previous examples but will be leveraged in
    # this one
    auth_client.oauth2_start_flow(requested_scopes=scopes)
    authorize_url = auth_client.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")

    auth_code = input("Please enter the code here: ").strip()
    tokens = auth_client.oauth2_exchange_code_for_tokens(auth_code)
    transfer_tokens = tokens.by_resource_server["transfer.api.globus.org"]

    # return the TransferClient object, as the result of doing a login
    return globus_sdk.TransferClient(
        authorizer=globus_sdk.AccessTokenAuthorizer(transfer_tokens["access_token"])
    )


# get an initial client to try with, which requires a login flow
transfer_client = login_and_get_transfer_client()

# now, try an ls on the source and destination to see if ConsentRequired
# errors are raised
consent_required_scopes = []


def check_for_consent_required(target):
    try:
        transfer_client.operation_ls(target, path="/")
    # catch all errors and discard those other than ConsentRequired
    # e.g. ignore PermissionDenied errors as not relevant
    except globus_sdk.TransferAPIError as err:
        if err.info.consent_required:
            consent_required_scopes.extend(err.info.consent_required.required_scopes)


check_for_consent_required(args.SRC)
check_for_consent_required(args.DST)

# the block above may or may not populate this list
# but if it does, handle ConsentRequired with a new login
if consent_required_scopes:
    print(
        "One of your endpoints requires consent in order to be used.\n"
        "You must login a second time to grant consents.\n\n"
    )
    transfer_client = login_and_get_transfer_client(scopes=consent_required_scopes)

# from this point onwards, the example is exactly the same as the reactive
# case, including the behavior to retry on ConsentRequiredErrors. This is
# not obvious, but there are cases in which it is necessary -- for example,
# if a user consents at the start, but the process of building task_data is
# slow, they could revoke their consent before the submission step
#
# in the common case, a single submission with no retry would suffice

task_data = globus_sdk.TransferData(
    source_endpoint=args.SRC, destination_endpoint=args.DST
)
task_data.add_item(
    "/share/godata/file1.txt",  # source
    "/~/example-transfer-script-destination.txt",  # dest
)


def do_submit(client):
    task_doc = client.submit_transfer(task_data)
    task_id = task_doc["task_id"]
    print(f"submitted transfer, task_id={task_id}")


try:
    do_submit(transfer_client)
except globus_sdk.TransferAPIError as err:
    if not err.info.consent_required:
        raise
    print(
        "Encountered a ConsentRequired error.\n"
        "You must login a second time to grant consents.\n\n"
    )
    transfer_client = login_and_get_transfer_client(
        scopes=err.info.consent_required.required_scopes
    )
    do_submit(transfer_client)
