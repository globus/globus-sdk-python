
.. py:currentmodule:: globus_sdk.experimental.consents

Consents
========

The Consents model provides a data model for loading consent information polled from
Globus Auth's ``get_consents`` API.

Consents are modeled as a ``ConsentForest`` full of ``ConsentTrees`` containing related
``Consents``. These consents detail a path of authorization grants that have been
provided by a user to client applications for token grants under certain scoped
contexts.

Reference
=========

.. autoclass:: ConsentForest
   :members:

.. autoclass:: ConsentTree
   :members:

.. autoclass:: Consent
   :members:

.. autoexception:: ConsentParseError

.. autoexception:: ConsentTreeConstructionError

