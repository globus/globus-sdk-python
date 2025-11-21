.. _userguide_coalesce_gares:

Coalescing Requirements Errors
==============================

A common pattern for applications which want to provide the best possible
user experience is to defer raising errors until all discoverable issues are
identified.
Instead of immediately, eagerly raising an error, the application can provide a
superior interface by collecting all of the errors at once and presenting them
to the user to resolve.

In the context of Globus Auth applications, this can manifest as multiple
interactions -- direct or indirect -- which produce  Globus Auth Requirements
Errors (represented in the SDK as the :class:`globus_sdk.gare.GARE` class).
Each :class:`globus_sdk.gare.GARE` can be resolved by a separate login flow, but
for an application which collects 3 ``GARE``\s, this would mean asking the user
to login 3 times in a row!

Applications which collect multiple such errors want to present the user with
the fewest possible login flows.
Unfortunately, ``GARE``\s are capable of expressing constraints which cannot be
safely merged into a single login flow -- requirements may be mutually exclusive,
or they may overlap in ill-defined ways.
Merging or "coalescing" ``GARE``\s is difficult to define in the general case,
but if you have more knowledge of your applications' requirements, you may be
able to do more than is generally safe.

In this doc, we'll share some theoretical cases of ``GARE``\s which

- definitely can be merged together safely
- definitely cannot be merged together safely
- possibly can be merged together

For readers who prefer to start with complete working examples, jump ahead
to the :ref:`example script <userguide_coalesce_gares_example>` which shows a
simple and safe merge procedure -- although it might not simplify all possible
combinations.

GAREs Which Can Safely Merge
----------------------------

Two of the fields in a ``GARE`` are arrays of values which are always combined
with "and" semantics.
As a result, they can always be safely combined with array concatenation.
These fields are:

- ``required_scopes``
- ``session_required_policies``

Additionally, a key field to handle is the ``code``.
Although services may use other values in practice, there are only two
well-defined values for the ``code`` string:

There are currently two supported values for the code field:

- ``ConsentRequired``: indicates that the user must consent to additional scopes
  in order to authorize the resource server(s) to complete the requested action.
- ``AuthorizationRequired``: indicates that this is a Globus Auth Requirements
  Error that is not more specifically described by any other code.

Because ``AuthorizationRequired`` is generic, it can always be safely used for
a ``GARE`` produced from other requirements.

As long as there are no other fields, a pair of ``GARE``\s with these
safe-to-merge fields can be combined.

Safe Merge Example
^^^^^^^^^^^^^^^^^^

For example,

.. code-block:: json

    {
      "code": "ConsentRequired",
      "authorization_parameters": {
        "required_scopes": ["foo"]
      }
    }

and

.. code-block:: json

    {
      "code": "AuthorizationRequired",
      "authorization_parameters": {
        "required_scopes": ["bar"],
        "session_required_policies": [
          "f2047039-2f07-4f13-b21b-b2edf7f9d329",
          "2fc6d9a3-9322-48a1-ad39-5dcf63a593a7"
        ]
      }
    }

can safely merge into

.. code-block:: json

    {
      "code": "AuthorizationRequired",
      "authorization_parameters": {
        "required_scopes": ["foo", "bar"],
        "session_required_policies": [
          "f2047039-2f07-4f13-b21b-b2edf7f9d329",
          "2fc6d9a3-9322-48a1-ad39-5dcf63a593a7"
        ]
      }
    }

GAREs Which Cannot Safely Merge
-------------------------------

There are no strictly defined merge semantics for any of the fields in
``GARE``\s, but in particular we can see problems when trying to merge
together ``session_required_single_domain``.

This field expresses the idea that a user must have an identity from *one of*
the listed domains, meaning it uses "or" semantics.
However, two separate ``GARE``\s naturally communicate "and" semantics, so
merging two such lists together produces an incorrect result.

Unsafe Merge Example
^^^^^^^^^^^^^^^^^^^^

For example,

.. code-block:: json

    {
      "code": "AuthorizationRequired",
      "authorization_parameters": {
        "session_required_single_domain": ["umich.edu"]
      }
    }

and

.. code-block:: json

    {
      "code": "AuthorizationRequired",
      "authorization_parameters": {
        "session_required_single_domain": ["stanford.edu"]
      }
    }

cannot merge together!

As a pair, these documents express
"the user must have an in-session ``umich.edu`` identity" **and**
"the user must have an in-session ``stanford.edu`` identity".

If we combine them into

.. code-block:: json

    {
      "code": "AuthorizationRequired",
      "authorization_parameters": {
        "session_required_single_domain": ["umich.edu", "stanford.edu"]
      }
    }

we accidentally express the idea that
"the user must have an in-session ``umich.edu`` identity" **or**
"the user must have an in-session ``stanford.edu`` identity".

We have accidentally transformed the "and" into an "or"!

GAREs Which Can Safely Merge *Sometimes*
----------------------------------------

Some fields in ``GARE``\s cannot be merged without some decision being made.
For example, ``session_message`` is a string message to display to the user.
When combining two ``GARE``\s with distinct messages, how should the result be
formulated? Should the messages be joined with some separator? Should a new
message be composed?

There is no strictly correct answer. However! An application which is, itself,
replacing the ``session_message`` can safely ignore this conflict because
it was planning to change the message anyway.

Maybe Safe Merge Example
^^^^^^^^^^^^^^^^^^^^^^^^

For example,

.. code-block:: json

    {
      "code": "ConsentRequired",
      "authorization_parameters": {
        "session_message": "You need authorization for Service Foo!",
        "required_scopes": ["foo"]
      }
    }

and

.. code-block:: json

    {
      "code": "ConsentRequired",
      "authorization_parameters": {
        "session_message": "You need authorization for Service Bar!",
        "required_scopes": ["bar"]
      }
    }

Could be combined into

.. code-block:: json

    {
      "code": "ConsentRequired",
      "authorization_parameters": {
        "session_message": "You need to authorize use of Services Foo and Bar.",
        "required_scopes": ["foo", "bar"]
      }
    }

This is safe because ``session_message`` is known to be non-semantic for the
purpose of authorizing the user.

.. _userguide_coalesce_gares_example:

Summary: Complete Example
-------------------------

Even knowing that ``GARE``\s cannot be safely combined in many cases, as
established in the introduction above, doing so is highly desirable for some
applications.

This example merges together these documents, represented as
:class:`globus_sdk.gare.GARE` objects, only in cases which are defined to
be safe. If a ``session_message`` or ``prompt`` value is supplied, it will
be used and will allow the ``GARE``\s to merge more aggressively.

.. literalinclude:: coalesce_gares.py
    :caption: ``coalesce_gares.py`` [:download:`download <coalesce_gares.py>`]
    :language: python

.. note::

    This example discards extra fields, which a ``GARE`` may store, but which
    are not part of the format specification.
