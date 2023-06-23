# RELEASING

## Prereqs

- Make sure you have a gpg key setup for use with git.
  [git-scm.com guide for detail](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)

## Procedure

- Make sure your repo is on `main` and up to date

```
git checkout main
git pull
```

- Read `changelog.d/` and decide if the release is MINOR or PATCH
- Update the version in `src/globus_sdk/version.py`
- Update metadata and changelog, then verify changes in `changelog.rst`

```
make prepare-release
$EDITOR changelog.rst
```

- Add and commit changed files, then push to `main`

```
git add changelog.d/ docs/changelog.rst src/globus_sdk/version.py
git commit -m 'Bump version and changelog for release'
git push origin main
```

- Tag the release. _This will run a workflow to publish to test-pypi._

```
make tag-release
```

- Create a GitHub release with a copy of the changelog. _This will run a workflow to publish to pypi._

Generate the release body by running
```
./scripts/changelog2md.py
```

The name of the GitHub release should be `v$SDK_VERSION`.
