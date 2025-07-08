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
        # most of the SDK should not pull in 'requests', making the parts which do
        # not handle request sending easy to use without the perf penalty from
        # requests/urllib3
        "authorizers",
        "config",
        "gare",
        "local_endpoint",
        "login_flows",
        "paging",
        "response",
        "scopes",
        "token_storage",
        # the top-level of the 'exc' subpackage (but not necessarily its contents)
        # should similarly be standalone, for exception handlers
        "exc",
        # internal components and utilities are a special case:
        # failing to ensure that these avoid 'requests' can make it more difficult
        # to ensure that the main parts (above) do not transitively pick it up
        "_internal.classprop",
        "_internal.guards",
        "_internal.remarshal",
        "_missing",
        "_serializable",
        "_types",
        "_utils",
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
