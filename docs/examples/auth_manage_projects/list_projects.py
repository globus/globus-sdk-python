import globus_sdk

# tutorial client ID
# we recommend replacing this with your own client for any production use-cases
CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"


def main() -> None:
    with (
        globus_sdk.UserApp("list-projects-example", client_id=CLIENT_ID) as app,
        globus_sdk.AuthClient(
            app_scopes=[globus_sdk.AuthClient.scopes.manage_projects], app=app
        ) as auth_client,
    ):
        for project in auth_client.get_projects():
            print(f"name: {project['display_name']}")
            print(f"id: {project['id']}")
            print()


if __name__ == "__main__":
    main()
