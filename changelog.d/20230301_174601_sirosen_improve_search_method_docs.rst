* ``SearchClient.update_entry`` and ``SearchClient.create_entry`` are
  officially deprecated. These APIs are aliases of ``SearchClient.ingest``, but
  their existence has caused confusion. Users are encouraged to switch to
  ``SearchClient.ingest`` instead (:pr:`NUMBER`)
