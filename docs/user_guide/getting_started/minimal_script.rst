.. currentmodule:: globus_sdk

.. _minimal_script_tutorial:

How to Create A Minimal Script
==============================

This is a basic tutorial in the use of the Globus SDK.

You can jump right in by using the ``CLIENT_ID`` seen in the example code blocks below!
That is the ID of the tutorial client, which lets you get started quickly and easily.

When you are ready to create your own application, follow
:ref:`How to Register an App in Globus Auth <tutorial_register_app>` and use
its ``CLIENT_ID`` in the rest of the tutorial to get your own app setup.

For readers who prefer to start with complete working examples, jump ahead to the
:ref:`example scripts <minimal_script_complete_examples>` at the end before reviewing
the doc.

Define your App Object
----------------------

Accessing Globus APIs as a user requires that you login to your new app and get
it tokens, credentials providing access the service.

The SDK provides a construct which represents an application. A
:class:`GlobusApp` is an object which can respond to requests for new or
existing tokens and store those tokens (by default, in ``~/.globus/app/``).

:class:`UserApp` is the type of :class:`GlobusApp` used for human user,
login-driven scenarios -- this is always the right type of application object
to use when you want to interact with services using your own account.

Start by defining an application object using :class:`UserApp`:

.. code-block:: python

    import globus_sdk

    # this is the tutorial client ID
    # replace this string with your ID for production use
    CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"

    # create your app
    my_app = globus_sdk.UserApp("my-user-app", client_id=CLIENT_ID)


.. note::

    The default behavior for a :class:`UserApp` is to do a CLI-based login flow.
    This behavior, and more, can be disabled or customized in numerous ways.

    For the full menu of options, look at the documentation about :ref:`Using a
    GlobusApp! <using_globus_app>`

Access the APIs via Clients
---------------------------

Once you have an app defined, you can use it with client objects to access
various Globus APIs.

When you attempt to interact with a service using an app-bound service client,
the app will automatically prompt you to login if valid credentials are
unavailable.

Start by defining the client object:

.. code-block:: python

    groups_client = globus_sdk.GroupsClient(app=my_app)

And now you can use it to perform some simple interaction, like listing
your groups:

.. code-block:: python

    # call out to the Groups service to get a listing
    my_groups = groups_client.get_my_groups()

    # print in CSV format
    print("ID,Name,Roles")
    for group in my_groups:
        roles = "|".join({m["role"] for m in group["my_memberships"]})
        print(",".join([group["id"], f'"{group["name"]}"', roles]))

When ``groups_client.get_my_groups()`` runs in the example above, the SDK
will prompt you to login.

.. _minimal_script_complete_examples:

Summary: Complete Examples
--------------------------

For ease of use, here are a set of examples.

One of them is exactly the same as the tutorial steps above, in a single block.

The next is a version of the tutorial which leverages the context manager
interfaces of the app and client to do cleanup.
This is slightly more verbose, but such usage is recommended because it ensures
resources associated with the client and app are properly closed.

The final example includes an explicit login step, so you can control when that
login flow happens!
Like the previous example, it uses the context manager style to ensure proper cleanup.

*These examples are complete. They should run without errors "as is".*

..  tab-set::

    ..  tab-item:: Tutorial Recap

        .. literalinclude:: list_groups.py
            :caption: ``list_groups.py`` [:download:`download <list_groups.py>`]
            :language: python

    ..  tab-item:: With Context Managers

        This example is the same as the tutorial, but does safer resource cleanup.

        .. literalinclude:: list_groups_improved.py
            :caption: ``list_groups_improved.py`` [:download:`download <list_groups_improved.py>`]
            :language: python

    ..  tab-item:: Explicit ``login()`` Step

        This example is very similar to the tutorial, but uses a separate login
        step.

        .. literalinclude:: list_groups_with_login.py
            :caption: ``list_groups_with_login.py`` [:download:`download <list_groups_with_login.py>`]
            :language: python
