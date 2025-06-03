#!/usr/bin/env python
from __future__ import annotations

import functools
import glob
import os
import pathlib
import re
import sys
import typing as t

REPO_ROOT = pathlib.Path(__file__).parent.parent

_ALL_NAME_PATTERN = re.compile(r'\s+"(\w+)",?')

PACKAGE_LOCS_TO_SCAN = (
    "globus_sdk/__init__.pyi",
    "globus_sdk/login_flows/",
    "globus_sdk/gare/",
    "globus_sdk/globus_app/",
    "globus_sdk/scopes/",
    "globus_sdk/response.py",
    "globus_sdk/_testing/",
)

DEPRECATED_NAMES = {
    "ComputeFunctionDocument",
    "ComputeFunctionMetadata",
}


def load_docs() -> dict[str, str]:
    all_docs = {}
    for file in glob.glob("docs/**/*.rst", recursive=True):
        with open(file) as f:
            all_docs[file] = f.read()
    return all_docs


def iter_all_documented_names() -> t.Iterable[str]:
    # names under these directives
    #
    #   .. autoclass:: <name>
    #   .. autoclass:: <name>(<args>)
    #   .. autofunction:: <name>
    #   .. autoexception:: <name>
    #   .. autodata:: <name>
    autodoc_pattern = re.compile(
        r"""
        ^\.\.\s+auto(?:class|function|exception|data)::\s+ # auto-directive (uncaptured)
        (?:\w+\.)*(\w+)(?:\(.*\))?$                        # symbol name (captured)
        """,
        flags=re.MULTILINE | re.X,
    )
    # names under these directives
    #
    #   .. class:: <name>
    #   .. py:data:: <name>
    pydoc_pattern = re.compile(
        r"""
        ^\.\.\s+(?:py:data|class)::\s+ # directive
        (?:\w+\.)*(\w+)(?:\(.*\))?$    # symbol name (captured)
        """,
        flags=re.MULTILINE | re.X,
    )
    for data in load_docs().values():
        for match in autodoc_pattern.finditer(data):
            yield match.group(1)
        for match in pydoc_pattern.finditer(data):
            yield match.group(1)


@functools.lru_cache
def all_documented_names() -> frozenset[str]:
    return frozenset(iter_all_documented_names())


def is_documented(name: str) -> bool:
    return name in all_documented_names()


def get_names_from_all_list(file_path: str) -> list[str]:
    with open(f"src/{file_path}") as fp:
        contents = fp.readlines()

    names: list[str] = []
    found_all = False
    for line in contents:
        if found_all:
            if line.strip() == ")":
                break
            # Extract the actual symbol from the line.
            # i.e., '  "Foo",\n' -> 'Foo'
            name_match = _ALL_NAME_PATTERN.match(line)
            if name_match is not None:
                names.append(name_match.group(1))
        else:
            if line.strip() == "__all__ = (":
                found_all = True
            else:
                continue
    return [n for n in names if not n.startswith("_")]


def ensure_exports_are_documented() -> bool:
    success = True
    used_deprecations = set()
    for loc in PACKAGE_LOCS_TO_SCAN:
        if loc.endswith("/"):
            loc = f"{loc}/__init__.py"
        for name in get_names_from_all_list(loc):
            if name in DEPRECATED_NAMES:
                used_deprecations.add(name)
                continue
            if not is_documented(name):
                print(f"'src/{loc}::{name}' was not found in doc directives")
                success = False
    if unused_deprecations := (DEPRECATED_NAMES - used_deprecations):
        print(f"unused deprecations: {unused_deprecations}")
        success = False
    return success


if __name__ == "__main__":
    os.chdir(REPO_ROOT)
    if not ensure_exports_are_documented():
        exit(1)
    sys.exit(0)
