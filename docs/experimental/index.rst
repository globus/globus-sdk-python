.. experimental_root:

Globus SDK Experimental Components
==================================

.. warning::

    The ``experimental`` module contains new "unstable" interfaces. These interfaces
    are subject to breaking changes.

    **Use at your own risk.**


Experimental Construct Lifecycle
--------------------------------

A construct is added in the ``experimental`` module when we, the maintainers,
are not sufficiently confident that it represents the best possible interface for the
underlying functionality. This frequently occurs when we have a design which shows
promise but would like to solicit feedback from the community before committing to it.

Once an interface has been evaluated and proven to be sufficiently coherent, we will
"stabilize" it, moving it to an appropriate section in the main module and leaving
behind an alias in the requisite experimental module to minimize import breakage. These
aliases will persist until the next major version release of the SDK (e.g., v3 -> v4).


Service Client Lifecycle
------------------------

A service client is added in the ``experimental`` module when the service
functionality it provides an interface to in Beta or under active development
and may experience changes in that could break the interfaces in the SDK.

Once the service has moved out of active development the service client
will be moved into the main services module leaving behind an alias in the
experimental module to minimize import breakage. These aliases will persist
until the next major version release of the SDK (e.g., v3 -> v4).
