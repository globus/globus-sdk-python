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

- Update the version in `src/globus_sdk/version.py`

- Update metadata and changelog, then verify changes in `changelog.rst`

```
make prepare-release
$EDITOR changelog.rst
```

- Add changed files;
    `git add changelog.d/ changelog.rst src/globus_sdk/version.py`

- Commit; `git commit -m 'Bump version and changelog for release'`

- Push the release branch; `git push -u origin release-$SDK_VERSION`

- Open a PR for review;
    `gh pr create --base main --title "Release v$SDK_VERSION" --label "no-news-is-good-news"`
    _The `no-news-is-good-news` label is required for release PRs._

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
  See [Appendix A](#appendix-a-email-template) for an optional email template.

- Ensure the 4.x-dev branch is updated with the latest changes from main
  by creating a PR:
    ```
    git checkout 4.x-dev
    git pull
    git checkout -b merge-main-to-4x-dev-$(date +%Y%m%d)
    git merge origin/main
    # Resolve any conflicts if they occur
    git push -u origin merge-main-to-4x-dev-$(date +%Y%m%d)
    gh pr create --base 4.x-dev --title "Merge main into 4.x-dev" \
      --body "Merging latest changes from main branch into 4.x-dev"
    ```
    After the PR is reviewed and merged, the 4.x-dev branch will be updated.

## Publish Pre-release 4.x packages to PyPi

Pre-release packages for the 4.x branch follow a similar process to main releases with some key differences:

### Prerequisites

- Make sure you have a gpg key setup for use with git.
- Ensure the 4.x-dev branch is up to date with latest changes from main (see merge process above)

### Pre-release Procedure

- Make sure your repo is on `4.x-dev` and up to date;
    `git checkout 4.x-dev; git pull`

- Check the current version in `pyproject.toml` and decide on the next pre-release version
  (e.g., if current is `4.0.0a2`, next would be `4.0.0a3`)

- (optional) Set the version in the `SDK_VERSION` env var, for use in the
  following steps. `SDK_VERSION=4.0.0a3`

- Create a release branch;
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

- Open a PR for review against the `4.x-dev` branch;
    `gh pr create --base 4.x-dev --title "Release v$SDK_VERSION" --label "no-news-is-good-news"`
    _The `no-news-is-good-news` label is required for release PRs._

- After any changes and approval, merge the PR, checkout `4.x-dev`, and pull;
    `git checkout 4.x-dev; git pull`

- Tag the release; `make tag-release`
    _This will run a workflow to publish to test-pypi._

- Create a GitHub release with a copy of the changelog.
    _This will run a workflow to publish to pypi._

  **Important:** For pre-releases, ensure you check the "Set as a pre-release" checkbox in
  the GitHub UI, or use the `--prerelease` flag with the CLI:

```
./scripts/changelog2md.py | \
  gh release create $SDK_VERSION --title "v$SDK_VERSION" --notes-file - --prerelease
```

## Appendix A: Email Template

When announcing a release on the Globus Discuss list (discuss@globus.org), use the following template:

**Subject:** Globus Python SDK v[VERSION]

**Body:**
```
I'm pleased to announce the release of a new version of the Globus Python SDK!

v[VERSION] Release Notes

[Insert output from ./scripts/changelog2md.py here]

GitHub Release: https://github.com/globus/globus-sdk-python/releases/tag/[VERSION]
PyPI: https://pypi.org/project/globus-sdk/[VERSION]
Documentation: https://globus-sdk-python.readthedocs.io
```

**Note:** The release notes content can be generated by running `./scripts/changelog2md.py`.
