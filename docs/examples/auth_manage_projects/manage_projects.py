import argparse

import globus_sdk

# tutorial client ID
# we recommend replacing this with your own client for any production use-cases
CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"


def get_auth_client(app: globus_sdk.GlobusApp) -> globus_sdk.AuthClient:
    return globus_sdk.AuthClient(
        app_scopes=[
            globus_sdk.AuthClient.scopes.manage_projects,
            globus_sdk.AuthClient.scopes.openid,
            globus_sdk.AuthClient.scopes.email,
        ],
        app=app,
    )


def create_project(app: globus_sdk.GlobusApp, name: str) -> None:
    with get_auth_client(app) as auth_client:
        userinfo = auth_client.userinfo()
        print(
            auth_client.create_project(
                name, contact_email=userinfo["email"], admin_ids=userinfo["sub"]
            )
        )


def delete_project(app: globus_sdk.GlobusApp, project_id: str) -> None:
    with get_auth_client(app) as auth_client:
        print(auth_client.delete_project(project_id))


def list_projects(app: globus_sdk.GlobusApp) -> None:
    with get_auth_client(app) as auth_client:
        for project in auth_client.get_projects():
            print(f"name: {project['display_name']}")
            print(f"id: {project['id']}")
            print()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["create", "delete", "list"])
    parser.add_argument("-p", "--project-id", help="Project ID for delete")
    parser.add_argument("-n", "--name", help="Project name for create")
    args = parser.parse_args()

    with globus_sdk.UserApp(
        "manage-projects-example",
        client_id=CLIENT_ID,
        # we set 'auto_redrive_gares', so that any authentication policy errors will
        # trigger an automatic second login
        config=globus_sdk.GlobusAppConfig(auto_redrive_gares=True),
    ) as app:
        if args.action == "create":
            if args.name is None:
                parser.error("create requires --name")
            create_project(app, args.name)
        elif args.action == "delete":
            if args.project_id is None:
                parser.error("delete requires --project-id")
            delete_project(app, args.project_id)
        elif args.action == "list":
            list_projects(app)
        else:
            raise NotImplementedError()


if __name__ == "__main__":
    main()
