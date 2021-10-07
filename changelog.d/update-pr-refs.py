#!/usr/bin/env python
"""
Meant to run in the context of a PR GitHub Actions workflow from the repo root
"""
import glob
import os

PR_NUMBER = os.environ["PR_NUMBER"]


def update_file(fname):
    with open(fname) as f:
        content = f.read()

    content.replace(":pr:`NUMBER`", f":pr:`{PR_NUMBER}`")

    with open(fname, "w") as f:
        f.write(content)


def main():
    for fname in glob.glob("changelog.d/*.rst"):
        update_file(fname)


if __name__ == "__main__":
    main()
