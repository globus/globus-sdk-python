Changed
~~~~~~~

- When parsing GAREs using ``to_gare`` and ``to_gares``, the root document is
  now considered a possible location for a GARE when subdocument errors are
  present on a ``GlobusAPIError`` object. Previously, the root document would
  only be considered in the absence of subdocument errors. (:pr:`NUMBER`)
