#!/usr/bin/env python
"""
Extract a changelog section from the full changelog contents, convert ReST and
sphinx-issues syntaxes to GitHub-flavored Markdown, and print the results.

Defaults to selecting the most recent (topmost) changelog section.
Can alternatively provide output for a specific version with `--target`.
e.g.

    ./scripts/changelog2md.py --target 3.20.0
"""

import argparse
import pathlib
import re
import typing as t

REPO_ROOT = pathlib.Path(__file__).parent.parent
CHANGELOG_PATH = REPO_ROOT / "docs" / "changelog.rst"

CHANGELOG_ANCHOR_PATTERN = re.compile(r"^\.\. _changelog-\d+\.\d+\.\d+:$", re.MULTILINE)
CHANGELOG_HEADER_PATTERN = re.compile(r"^v(\d+\.\d+\.\d+).*$", re.MULTILINE)

H2_RST_PATTERN = re.compile(r"-+")
H3_RST_PATTERN = re.compile(r"~+")

SPHINX_ISSUES_PR_PATTERN = re.compile(r":pr:`(\d+)`")
SPHINX_ISSUES_ISSUE_PATTERN = re.compile(r":issue:`(\d+)`")
SPHINX_ISSUES_USER_PATTERN = re.compile(r":user:`([^`]+)`")


def iter_changelog_chunks(changelog_content: str) -> t.Iterator[str]:
    # first one precedes the first changelog
    chunks = CHANGELOG_ANCHOR_PATTERN.split(changelog_content)[1:]
    yield from chunks


def _trim_empty_lines(lines: list[str]) -> None:
    while lines[0] == "":
        lines.pop(0)
    while lines[-1] == "":
        lines.pop()


def get_last_changelog(changelog_content: str) -> list[str]:
    latest_changes = next(iter_changelog_chunks(changelog_content))
    lines = latest_changes.split("\n")
    idx = 0
    while idx < len(lines) and H2_RST_PATTERN.fullmatch(lines[idx]) is None:
        idx += 1
    lines = lines[idx + 1 :]
    _trim_empty_lines(lines)
    return lines


def _iter_target_section(target: str, changelog_content: str) -> t.Iterator[str]:
    started = False
    for line in changelog_content.split("\n"):
        if not started:
            if m := CHANGELOG_HEADER_PATTERN.match(line):
                if m.group(1) == target:
                    started = True
            continue
        if CHANGELOG_ANCHOR_PATTERN.fullmatch(line):
            return
        if H2_RST_PATTERN.fullmatch(line):
            continue
        yield line


def get_changelog_section(target: str, changelog_content: str) -> list[str]:
    lines = list(_iter_target_section(target, changelog_content))
    _trim_empty_lines(lines)
    return lines


def convert_rst_to_md(lines: list[str]) -> t.Iterator[str]:
    skip = False
    for i, line in enumerate(lines):
        if skip:
            skip = False
            continue

        try:
            peek = lines[i + 1]
        except IndexError:
            peek = None

        updated = line

        if peek is not None and H3_RST_PATTERN.fullmatch(peek):
            skip = True
            updated = f"## {updated}"

        updated = SPHINX_ISSUES_PR_PATTERN.sub(r"#\1", updated)
        updated = SPHINX_ISSUES_ISSUE_PATTERN.sub(r"#\1", updated)
        updated = SPHINX_ISSUES_USER_PATTERN.sub(r"@\1", updated)
        updated = updated.replace("``", "`")
        yield updated


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--target", "-t", help="A target version to use. Defaults to latest."
    )
    args = parser.parse_args()

    full_changelog = CHANGELOG_PATH.read_text()

    if args.target:
        changelog_section = get_changelog_section(args.target, full_changelog)
    else:
        changelog_section = get_last_changelog(full_changelog)

    for line in convert_rst_to_md(changelog_section):
        print(line)


if __name__ == "__main__":
    main()
