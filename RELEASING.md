# RELEASING

## Prereqs

- Make sure you have a pypi account
- Setup your credentials for [twine](https://github.com/pypa/twine) (the pypi upload tool)
- Make sure you have a gpg key setup for use with git.
  [git-scm.com guide for detail](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)

## Procedure

- Update the version in `src/globus_sdk/version.py`
- `make prepare-release` to update version and changelog
- Add and commit with `git commit -m 'Bump version and changelog for release'`
- `make release` to build, publish, and tag
- Create a GitHub release with a copy of the changelog
