Changed
~~~~~~~

- The mechanisms of token data validation inside of ``GlobusApp`` are now more
  modular and extensible. The ``ValidatingTokenStorage`` class does not define
  built-in validation behaviors, but instead contains a list of validator
  objects, which can be extended and otherwise altered. (:pr:`1061`)

  - These changes allow more validation criteria around token data to be
    handled within the ``ValidatingTokenStorage``. This changes error behaviors
    to avoid situations in which multiple errors are raised serially by
    different layers of GlobusApp.
