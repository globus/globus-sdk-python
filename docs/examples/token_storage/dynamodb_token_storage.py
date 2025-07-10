from __future__ import annotations

import argparse
import time
import typing as t

import boto3

import globus_sdk
from globus_sdk.token_storage import StorageAdapter

CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
tablename = "example-globus-tokenstorage"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--create",
    action="store_true",
)

boto_client = boto3.client("dynamodb")
auth_client = globus_sdk.NativeAppAuthClient(CLIENT_ID)


class DynamoDBStorageAdapter(StorageAdapter):
    def __init__(self, client, tablename: str, namespace: str = "DEFAULT") -> None:
        """
        :param client: A boto3 DyanmoDB client to use
        :param tablename: The name of the dynamodb table to use
        :param namespace: A namespace for all keys within this storage.
            Setting up explicit namespacing allows for multiple storage
            adapters for multiple users or applications to share a table.
        """
        self.client = client
        self.tablename = tablename
        self.namespace = namespace

    def _compute_key(self, resource_server: str) -> str:
        """
        Compute the 'token_data_id' used for storage and retrieval
        vis-a-vis a specific resource_server/namespace combination.

        This is defined as a simple delimited string which starts with the
        namespace given.

        Globus keys tokens by the ``resource_server`` string, but also has
        additional context about which user and application were being
        used. For the storage adapter, we will need to use namespacing to
        separate users.

        Consider setting ``namespace`` to a value like a user ID or a
        combination of user ID and authentication context.
        """
        return f"{self.namespace}:{resource_server}"

    def store(self, token_response: globus_sdk.OAuthTokenResponse) -> None:
        for resource_server, token_data in token_response.by_resource_server.items():
            key = self._compute_key(resource_server)
            dynamo_item = {
                "token_data_id": {"S": key},
                "resource_server": {"S": resource_server},
                "access_token": {"S": token_data["access_token"]},
                "refresh_token": {"S": token_data["refresh_token"]},
                "expires_at_seconds": {"N": str(token_data["expires_at_seconds"])},
                "scope": {"S": token_data["scope"]},
            }
            # avoid setting `refresh_token` if it is null (meaning the
            # login flow used access tokens only)
            if token_data["refresh_token"] is None:
                del dynamo_item["refresh_token"]

            self.client.put_item(TableName=self.tablename, Item=dynamo_item)

    def get_token_data(self, resource_server: str) -> dict[str, t.Any] | None:
        key = self._compute_key(resource_server)

        wrapped_item = self.client.get_item(
            TableName=self.tablename,
            Key={"token_data_id": {"S": key}},
            ConsistentRead=True,
        )
        if "Item" not in wrapped_item:
            return None

        dynamo_item = wrapped_item["Item"]
        return {
            "resource_server": dynamo_item["resource_server"]["S"],
            "access_token": dynamo_item["access_token"]["S"],
            "refresh_token": dynamo_item.get("refresh_token", {"S": None})["S"],
            "expires_at_seconds": int(dynamo_item["expires_at_seconds"]["N"]),
            "scope": dynamo_item["scope"]["S"],
        }


def create_table():
    # create a table with a key of "token_data_id"
    # this is a nonspecific string key which we will compute
    #
    # the relationship of "token_data_id" to the token will be explained below
    boto_client.create_table(
        TableName=tablename,
        KeySchema=[{"AttributeName": "token_data_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "token_data_id", "AttributeType": "S"}],
        BillingMode="PROVISIONED",
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    print(f"'{tablename}' create in progress.")

    # poll status until the table is "ACTIVE"
    print("Waiting for active status (Ctrl+C to cancel)...", end="", flush=True)
    status = None
    while status != "ACTIVE":
        time.sleep(1)
        try:
            r = boto_client.describe_table(TableName=tablename)
        except boto_client.exceptions.ResourceNotFoundException:
            continue
        print(".", end="", flush=True)
        status = r["Table"]["TableStatus"]
    print("ok")


def do_login_flow(storage: StorageAdapter):
    auth_client.oauth2_start_flow(
        requested_scopes=globus_sdk.GroupsClient.scopes.view_my_groups_and_memberships,
        refresh_tokens=True,
    )
    authorize_url = auth_client.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")
    auth_code = input("Please enter the code here: ").strip()
    tokens = auth_client.oauth2_exchange_code_for_tokens(auth_code)
    storage.store(tokens)
    return tokens.by_resource_server[globus_sdk.GroupsClient.resource_server]


def group_list(storage: StorageAdapter):
    tokens = storage.get_token_data(globus_sdk.GroupsClient.resource_server)
    if tokens is None:
        tokens = do_login_flow(storage)

    authorizer = globus_sdk.RefreshTokenAuthorizer(
        tokens["refresh_token"],
        auth_client,
        access_token=tokens["access_token"],
        expires_at=tokens["expires_at_seconds"],
        on_refresh=storage.store,
    )
    groups_client = globus_sdk.GroupsClient(authorizer=authorizer)
    print("ID,Name,Type,Session Enforcement,Roles")
    for group in groups_client.get_my_groups():
        # parse the group to get data for output
        if group.get("enforce_session"):
            session_enforcement = "strict"
        else:
            session_enforcement = "not strict"
        roles = ",".join({m["role"] for m in group["my_memberships"]})

        print(
            ",".join(
                [
                    group["id"],
                    group["name"],
                    group["group_type"],
                    session_enforcement,
                    roles,
                ]
            )
        )


if __name__ == "__main__":
    args = parser.parse_args()
    if args.create:
        create_table()
    else:
        storage = DynamoDBStorageAdapter(boto_client, tablename)
        group_list(storage)
