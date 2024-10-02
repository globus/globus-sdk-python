.. _login_flow_managers:

Login Flow Managers
===================

.. currentmodule:: globus_sdk.login_flows

This page provides references for the LoginFlowManager abstract class and some concrete
implementations.

A login flow manager is a class responsible for driving a user through a login flow,
with the ultimate goal of obtaining tokens. The tokens are required to make
requests against any Globus services.

Interface
---------

.. autoclass:: LoginFlowManager
    :members:

Command Line
------------

As the name might suggest, a CommandLineLoginFlowManager drives user logins through
the command line (stdin/stdout). When run, the manager will print a URL to the console
then prompt a user to navigate to that URL and enter the resulting auth code
back into the terminal.

Example Code:

.. code-block:: pycon

    >>> from globus_sdk import NativeAppAuthClient
    >>> from globus_sdk.scopes import TransferScopes
    >>> from globus_sdk.login_flows import CommandLineLoginFlowManager

    >>> login_client = NativeAppAuthClient(client_id=client_id)
    >>> manager = CommandLineLoginFlowManager(login_client)
    >>>
    >>> token_response = manager.run_login_flow(
    ...     GlobusAuthorizationParameters(required_scopes=[TransferScopes.all])
    ... )
    Please authenticate with Globus here:
    -------------------------------------
    https://auth.globus.org/v2/oauth2/authorize?cli...truncated...
    -------------------------------------

    Enter the resulting Authorization Code here:

.. autoclass:: CommandLineLoginFlowManager
    :members:
    :member-order: bysource
    :show-inheritance:

Local Server
------------

A LocalServerLoginFlowManager drives more automated, but less portable, login flows
compared with its command line counterpart. When run, rather than printing the
authorization URL, the manager will open it in the user's default browser. Alongside
this, the manager will start a local web server to receive the auth code upon completion
of the login flow.

This provides a more user-friendly login experience as there is no manually copy/pasting
of links and codes. It also requires however that the python process be running in an
environment with access to a supported browser. As such, this flow is not suitable for
headless environments (e.g., while ssh-ed into a cluster node).

.. note::

   This login manager is only supported for native clients.


Example Usage:

.. code-block:: pycon

    >>> from globus_sdk import NativeAppAuthClient
    >>> from globus_sdk.scopes import TransferScopes
    >>> from globus_sdk.login_flows import LocalServerLoginFlowManager

    >>> login_client = NativeAppAuthClient(client_id=client_id)
    >>> manager = LocalServerLoginFlowManager(login_client)
    >>>
    >>> token_response = manager.run_login_flow(
    ...     GlobusAuthorizationParameters(required_scopes=[TransferScopes.all])
    ... )

.. autoclass:: LocalServerLoginFlowManager
    :members:
    :member-order: bysource
    :show-inheritance:

.. autoexception:: LocalServerLoginError

.. autoexception:: LocalServerEnvironmentalLoginError
