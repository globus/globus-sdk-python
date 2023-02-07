#!/usr/bin/env python
"""
Meant to run in the context of a PR GitHub Actions workflow from the repo root
"""
import argparse
import glob
import json
import os
import subprocess
import typing as t
import urllib.error
import urllib.request

CHANGELOG_D = os.path.dirname(__file__)


def get_pr_number(commit_sha: str) -> t.Optional[str]:
    req = urllib.request.Request(
        "https://api.github.com/repos/globus/globus-sdk-python/"
        f"commits/{commit_sha}/pulls"
    )
    req.add_header("Accept", "application/vnd.github.v3+json")

    try:
        response = urllib.request.urlopen(req)
    except urllib.error.URLError:
        return None

    data = json.load(response)
    if not (isinstance(data, list) and len(data) > 0):
        return None
    prdata = data[0]
    if not (isinstance(prdata, dict) and "number" in prdata):
        return None
    return str(prdata["number"])


def update_file(fname: str, pr_num: t.Optional[str]) -> None:
    with open(fname) as f:
        content = f.read()

    if pr_num:
        content = content.replace(":pr:`NUMBER`", f":pr:`{pr_num}`")
    else:
        content = content.replace("(:pr:`NUMBER`)", "")
        content = "\n".join([line.rstrip() for line in content.splitlines()]) + "\n"

    with open(fname, "w") as f:
        f.write(content)


def get_commit(fname: str) -> str:
    return subprocess.run(
        ["git", "log", "-n", "1", "--pretty=format:%H", "--", fname],
        capture_output=True,
        check=True,
    ).stdout.decode("utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Update PR number in a changelog fragment"
    )
    parser.add_argument("FILENAME", help="file to check and update", nargs="?")
    args = parser.parse_args()

    if args.FILENAME:
        files = [args.FILENAME]
    else:
        files = glob.glob(os.path.join(CHANGELOG_D, "*.rst"))

    for filename in files:
        print(f"updating {filename}")
        commit = get_commit(filename)
        print(f"  commit={commit}")
        pr_num = get_pr_number(commit)
        print(f"  PR={pr_num}")
        update_file(filename, pr_num)


if __name__ == "__main__":
    main()
