"""
Import the modules from the lazy import table in "all" possible orders. This ensures
that there cannot be any user-triggerable import cycles.

Note that testing all permutations is infeasibly expensive.

This is kept in the non-pytest dir because it may be written in pytest but it is not
part of the normal testsuite.
"""

import itertools
import os
import subprocess
import sys

import pytest

import globus_sdk
from globus_sdk._internal.lazy_import import find_source_module

PYTHON_BINARY = os.environ.get("GLOBUS_TEST_PY", sys.executable)

MODULE_NAMES = sorted(
    {
        find_source_module("globus_sdk", "__init__.pyi", attr).lstrip(".")
        for attr in globus_sdk.__all__
        if not attr.startswith("_")
    }
)


@pytest.mark.parametrize(
    "first_module, second_module", itertools.permutations(MODULE_NAMES, 2)
)
def test_import_pairwise(first_module, second_module):
    command = (
        f"from globus_sdk.{first_module} import *; "
        f"from globus_sdk.{second_module} import *"
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


@pytest.mark.parametrize("first_module", MODULE_NAMES)
def test_import_all_each_first(first_module):
    command = f"from globus_sdk.{first_module} import *; " + "; ".join(
        f"from globus_sdk.{mod} import *" for mod in MODULE_NAMES if mod != first_module
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
