#!/usr/bin/env python
"""
Extract the last changelog section from the full changelog contents, convert ReST and
sphinx-issues syntaxes to GitHub-flavored Markdown, and print the results.
"""

import pathlib
import re
import typing as t

REPO_ROOT = pathlib.Path(__file__).parent.parent
CHANGELOG_PATH = REPO_ROOT / "docs" / "changelog.rst"

CHANGELOG_MARKER_PATTERN = re.compile(r"^\.\. _changelog-\d+\.\d+\.\d+:$", re.MULTILINE)
UNDERLINE_PATTERN = re.compile(r"\-+")

SPHINX_ISSUES_PR_PATTERN = re.compile(r":pr:`(\d+)`")
SPHINX_ISSUES_ISSUE_PATTERN = re.compile(r":issue:`(\d+)`")
SPHINX_ISSUES_USER_PATTERN = re.compile(r":user:`([^`]+)`")


def iter_changelog_chunks(changelog_content: str) -> t.Iterator[str]:
    # first one precedes the first changelog
    chunks = CHANGELOG_MARKER_PATTERN.split(changelog_content)[1:]
    yield from chunks


def get_last_changelog(changelog_content: str) -> t.Iterator[str]:
    latest_changes = next(iter_changelog_chunks(changelog_content))
    lines = latest_changes.split("\n")
    idx = 0
    while idx < len(lines) and UNDERLINE_PATTERN.fullmatch(lines[idx]) is None:
        idx += 1
    lines = lines[idx + 1 :]
    while lines[0] == "":
        lines.pop(0)
    while lines[-1] == "":
        lines.pop()
    yield from lines


def convert_rst_to_md(lines: t.Iterator[str]) -> t.Iterator[str]:
    for line in lines:
        updated = line
        updated = SPHINX_ISSUES_PR_PATTERN.sub(r"#\1", updated)
        updated = SPHINX_ISSUES_ISSUE_PATTERN.sub(r"#\1", updated)
        updated = SPHINX_ISSUES_USER_PATTERN.sub(r"@\1", updated)
        updated = updated.replace("``", "`")
        yield updated


def main():
    full_changelog = CHANGELOG_PATH.read_text()

    for line in convert_rst_to_md(get_last_changelog(full_changelog)):
        print(line)


if __name__ == "__main__":
    main()
