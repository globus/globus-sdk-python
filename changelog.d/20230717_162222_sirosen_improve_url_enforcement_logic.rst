Changed
~~~~~~~

- The enforcement logic for URLs in ``BaseClient`` instantiation has been
  improved to only require that ``service_name`` be set if ``base_url`` is not
  provided. (:pr:`NUMBER`)

  - This change primarily impacts subclasses, which no longer need to set the
    ``service_name`` class variable if they ensure that the ``base_url`` is
    always passed with a non-null value.

  - Direct instantiation of ``BaseClient`` is now possible, although not
    recommended for most use-cases.
