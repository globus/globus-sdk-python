Manage Globus Auth Projects
===========================

List Projects via the Auth API
------------------------------

The following is a very small and simple script using the Globus Auth Developer
APIs.

It uses the tutorial client ID from the :ref:`tutorials <tutorials>`.

.. literalinclude:: list_projects.py
    :caption: ``list_projects.py`` [:download:`download <list_projects.py>`]
    :language: python


List, Create, and Delete Projects via the Auth API
--------------------------------------------------

.. warning::

    The following script has destructive capabilities.

    Deleting projects may be harmful to your production applications.
    Only delete with care.

The following example builds upon the earlier example by offering multiple
features: List, Create, and Delete.

Argument parsing allows for an action to be selected, which is then executed by
calling the appropriate function.

Because Delete requires authentication under a session policy, we set
the ``auto_redrive_gares`` configuration, which handles unsatisfied auth
requirements. If a policy failure is encountered, the code will prompt the user
to login again to satisfy the policy and then reexecute the desired activity.

.. literalinclude:: manage_projects.py
    :caption: ``manage_projects.py`` [:download:`download <manage_projects.py>`]
    :language: python
