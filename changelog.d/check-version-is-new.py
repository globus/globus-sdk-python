#!/usr/bin/env python
"""
Check if the version number in the source is already present as a changelog header.
"""

import os
import re
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    # Older Python versions
    import tomli as tomllib

PATTERN_FORMAT = "^v{version}\\s+\\({date}\\)$"
CHANGELOG_D = os.path.dirname(__file__)
REPO_ROOT = os.path.dirname(CHANGELOG_D)


def parse_version():
    with open(os.path.join(REPO_ROOT, "pyproject.toml"), "rb") as f:
        pyproject = tomllib.load(f)

    return pyproject["project"]["version"]


def get_header_re(version):
    version = re.escape(version)
    return PATTERN_FORMAT.format(version=version, date=r"\d{4}-\d{2}-\d{2}")


def changelog_has_version(version):
    pattern = get_header_re(version)
    with open(os.path.join(REPO_ROOT, "changelog.rst")) as f:
        return bool(re.search(pattern, f.read(), flags=re.MULTILINE))


def main():
    version = parse_version()
    if changelog_has_version(version):
        print(f"version {version} appears in the changelog already!")
        sys.exit(1)
    else:
        print(f"version check OK ({version} is a new version number)")
    sys.exit(0)


if __name__ == "__main__":
    main()
