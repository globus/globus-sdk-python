# RELEASING

## Prereqs

- Make sure you have a gpg key setup for use with git.
  [git-scm.com guide for detail](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)

## Procedure

- Make sure your repo is on `main` and up to date;
    `git checkout main; git pull`

- Read `changelog.d/` and decide if the release is MINOR or PATCH

- (optional) Set the version in the `SDK_VERSION` env var, for use in the
  following steps. `SDK_VERSION=...`

- Decide on the new version number and create a branch;
   `git checkout -b release-$SDK_VERSION`

- Update the version in `pyproject.toml`

- Update metadata and changelog, then verify changes in `changelog.rst`

```
make prepare-release
$EDITOR changelog.rst
```

- Add changed files;
    `git add changelog.d/ changelog.rst pyproject.toml`

- Commit; `git commit -m 'Bump version and changelog for release'`

- Push the release branch; `git push -u origin release-$SDK_VERSION`

- Open a PR for review;
    `gh pr create --base main --title "Release v$SDK_VERSION"`

- After any changes and approval, merge the PR, checkout `main`, and pull;
    `git checkout main; git pull`

- Tag the release; `make tag-release`
    _This will run a workflow to publish to test-pypi._

- Create a GitHub release with a copy of the changelog.
    _This will run a workflow to publish to pypi._

Generate the release body by running
```
./scripts/changelog2md.py
```
or create the release via the GitHub CLI
```
./scripts/changelog2md.py | \
  gh release create $SDK_VERSION --title "v$SDK_VERSION" --notes-file -
```

- Send an email announcement to the Globus Discuss list with highlighted
  changes and a link to the GitHub release page.
  (If the Globus CLI is releasing within a short interval,
  combine both announcements into a single email notice.)
