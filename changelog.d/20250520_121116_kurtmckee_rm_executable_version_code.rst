Breaking Changes
~~~~~~~~~~~~~~~~

- The SDK version is no longer available in ``globus_sdk.version.__version__``.

  Packages that want to query the SDK version must use ``importlib.metadata``:

  ..  code-block:: python

        import importlib.metadata

        GLOBUS_SDK_VERSION = importlib.metadata.distribution("globus_sdk").version
