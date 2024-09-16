"""
Test that various modules do not rely on `requests` at import-time.

This means that these modules are safe to import in highly latency-sensitive
applications like globus-cli.
"""

import os
import subprocess
import sys

import pytest

PYTHON_BINARY = os.environ.get("GLOBUS_TEST_PY", sys.executable)


@pytest.mark.parametrize(
    "module_name",
    (
        # experimental modules
        "experimental",
        "experimental.scope_parser",
        # parts which are expected to be standalone
        "scopes",
        "gare",
        "config",
        # the top-level of the 'exc' subpackage (but not necessarily its contents)
        "exc",
        # internal bits and bobs
        "_guards",
        "_types",
        "utils",
        "version",
    ),
)
def test_module_does_not_require_requests(module_name):
    command = (
        f"import globus_sdk.{module_name}; "
        "import sys; assert 'requests' not in sys.modules"
    )
    proc = subprocess.Popen(
        f'{PYTHON_BINARY} -c "{command}"',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    status = proc.wait()
    assert status == 0, str(proc.communicate())
    proc.stdout.close()
    proc.stderr.close()
