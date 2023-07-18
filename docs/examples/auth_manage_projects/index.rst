Manage Globus Auth Projects
===========================

.. note::

    The following scripts, when run, may leave tokens in a JSON file in
    your home directory. Be sure to delete these tokens after use.

List Projects via the Auth API
------------------------------

The following is a very small and simple script using the Globus Auth Developer
APIs.

It uses the tutorial client ID from the :ref:`tutorial <tutorial>`.
For simplicity, the script will prompt for login on each use.

.. literalinclude:: list_projects.py
    :caption: ``list_projects.py`` [:download:`download <list_projects.py>`]
    :language: python


List and Create Projects via the Auth API
-----------------------------------------

The next example builds upon the earlier example by offering a pair of
features, List and Create.

Argument parsing allows for an action to be selected, which is then executed by
calling the appropriate function.

.. literalinclude:: list_and_create_projects.py
    :caption: ``list_and_create_projects.py`` [:download:`download <list_and_create_projects.py>`]
    :language: python


List, Create, and Delete Projects via the Auth API
--------------------------------------------------

.. warning::

    The following script has destructive capabilities.

    Deleting projects may be harmful to your production applications.
    Only delete with care.

The following example expands upon the former by adding delete functionality.

Because Delete requires authentication under a session policy, the login code
grows here to include a storage adapter (with data kept in
``~/.sdk-manage-projects.json``). If a policy failure is encountered, the code
will prompt the user to login again to satisfy the policy and then reexecute
the desired activity.

As a result, this example is significantly more complex, but it still follows
the same basic pattern as above.

.. literalinclude:: manage_projects.py
    :caption: ``manage_projects.py`` [:download:`download <manage_projects.py>`]
    :language: python
