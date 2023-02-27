# RELEASING

## Prereqs

- Make sure you have a pypi account
- Setup your credentials for [twine](https://github.com/pypa/twine) (the pypi upload tool)
- Make sure you have a gpg key setup for use with git.
  [git-scm.com guide for detail](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)
- Make sure `$EDITOR` is set

## Procedure

- Make sure your repo is on `main` and up to date; `git checkout main; git pull`
- Read `changelog.d/` and decide if the release is MINOR or PATCH
- Update the version in `src/globus_sdk/version.py`
- Update version and changelog; `make prepare-release`
- Add changed files;
    `git add changelog.d/ docs/changelog.rst src/globus_sdk/version.py`
- Commit; `git commit -m 'Bump version and changelog for release'`
- Push to main; `git push origin main`
- Tag the release; `make tag-release`
    _This will run a workflow to publish to test-pypi_
- Create a GitHub release with a copy of the changelog
    _This will run a workflow to publish to pypi_
