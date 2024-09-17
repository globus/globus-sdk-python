Changed
~~~~~~~

- Globus Auth Requirements errors are no longer ``experimental``. They have
  been moved to the ``globus_sdk.gare`` module and the primary document type
  has been renamed from ``GlobusAuthRequirementsError`` to ``GARE``. (:pr:`NUMBER`)

  - The functions provided by this interface have also been renamed to use
    ``gare`` in their naming: ``to_gare``, ``is_gare``, ``has_gares``, and
    ``to_gares`` are now all available. The older names are available as
    aliases from the ``experimental`` namespace.
