.. _tutorials:

Tutorials
=========

.. _getting_started:

These tutorials cover basic usage of the Globus SDK.

They takes you through a simple step-by-step flow for registering your
application, and then using that registered application to login and
interact with services.

.. toctree::
    :caption: Tutorials
    :maxdepth: 1

    register_app
    minimal_app

Quickstart
----------

For the smallest self-contained example, here's the final example from the
"Minimal App" tutorial:

.. literalinclude:: tutorial_recap.py
    :caption: ``tutorial_recap.py`` [:download:`download <tutorial_recap.py>`]
    :language: python

*This example is complete. It should run without errors "as is".*

We recommend following the tutorial doc for an explanation!

Legacy Tutorial
---------------

The original SDK tutorial is still available as a separate document.
It should only be used for reference for authors who are trying to understand
older projects which predate :class:`GlobusApp`.

.. toctree::
    :caption: Legacy Tutorial
    :maxdepth: 1

    legacy_tutorial
