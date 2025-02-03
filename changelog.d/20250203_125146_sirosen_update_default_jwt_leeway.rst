Changed
~~~~~~~

- The SDK now defaults JWT leeway to 300 seconds when decoding ``id_token``\s;
  the previous leeway was 0.5 seconds. Users should find that they are much
  less prone to validation errors when working in VMs or other scenarios which
  can cause significant clock drift. (:pr:`NUMBER`)
