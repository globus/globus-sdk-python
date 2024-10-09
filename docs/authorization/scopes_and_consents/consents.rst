
.. py:currentmodule:: globus_sdk.scopes.consents

Consents
========

The Consents model provides a data model for loading consent information polled from
Globus Auth's ``get_consents`` API.

Consents are modeled as a ``ConsentForest`` full of ``ConsentTrees`` containing related
``Consents``. These consents detail a path of authorization grants that have been
provided by a user to client applications for token grants under certain scoped
contexts.

While the consent model classes themselves are exposed here in ``globus_sdk.scopes.consents``,
most objects are actually loaded from a :meth:`globus_sdk.AuthClient.get_consents` response, using the attached :meth:`globus_sdk.GetConsentsResponse.to_forest()` method:

.. code-block:: python

    import globus_sdk
    from globus_sdk.scopes.consents import ConsentForest

    my_identity_id = ...
    client = globus_sdk.AuthClient(...)
    response = client.get_consents(my_identity_id)

    consent_forest: ConsentForest = response.to_forest()

Reference
---------

.. autoclass:: ConsentForest
   :members:

.. autoclass:: ConsentTree
   :members:

.. autoclass:: Consent
   :members:

.. autoexception:: ConsentParseError

.. autoexception:: ConsentTreeConstructionError

