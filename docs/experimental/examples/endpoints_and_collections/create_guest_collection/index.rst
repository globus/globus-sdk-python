
Creating a Guest Collection
===========================

Within the Globus Ecosystem, data is managed through the abstraction of *Collections*.
The example included on this page demonstrate how to create specifically a
*Guest Collection* using the Globus Python SDK. Guest collections, formerly known as
"Shares", are collections which provide access to a subdirectory of an existing
collection through a particular user or client's local permissions.

Guest collections are a great way to set up data automation. They may be scoped down
to a particular directory within an existing "Mapped Collection" and don't implicitly
inherit the same authorization timeout requirements as their parent Mapped Collection.
Once created, they can be shared to other users/entities, in effect giving another
entity access, through you, to some underlying data.

.. Warning::

    While guest collections don't implicitly inherit their parent mapped collection's
    authorization timeout in some cases they do or alternatively may be disabled
    entirely. This is a decision made by the endpoint owner, not Globus.

    Because requirements can vary so drastically between endpoints, we recommend
    consulting with the particular endpoint's documentation and/or owner to determine
    whether guest collections provide the desired level of access with the desired
    minimization of authorization.

.. Note::

    The scripts reference a globus hosted "tutorial" mapped collection. This is just
    to provide as simple of a functioning example out of the box as possible.

    For actual application, replace the IDs with the relevant collection and
    storage gateway IDs.


.. tab-set::

    .. tab-item:: User-owned Collection

        This script demonstrates how to create a guest collection owned by a human.

        It will prompt the user to authenticate through a browser and authorize the
        script to act on their behalf.

        .. literalinclude:: create_guest_collection_user_owned.py
            :caption: ``create_guest_collection_user_owned.py`` [:download:`download <create_guest_collection_user_owned.py>`]
            :language: python


    .. tab-item:: Client-owned Collection

        This script demonstrates how to create a guest collection owned by a client
        (i.e. a service account).

        It will automatically request and use client access tokens based on the supplied
        client ID and secret.

        .. literalinclude:: create_guest_collection_client_owned.py
            :caption: ``create_guest_collection_client_owned.py`` [:download:`download <create_guest_collection_client_owned.py>`]
            :language: python
