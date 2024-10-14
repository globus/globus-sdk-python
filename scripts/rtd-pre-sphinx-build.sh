#!/bin/bash

VERSION=$(grep '^__version__' src/globus_sdk/version.py | cut -d '"' -f2)

case "$READTHEDOCS_VERSION_TYPE" in
    external)
        echo "detected PR build"
        VERSION="${VERSION}-pr-${READTHEDOCS_VERSION_NAME}"
        ;;
    branch)
        case "${READTHEDOCS_VERSION_NAME}" in
            latest)
                echo "detected 'latest' branch build"
                VERSION="${VERSION}-dev"
                ;;
            *)
                echo "detected non-'latest' branch build"
                echo "exiting(ok)..."
                exit 0
                ;;
        esac
        ;;
    tag | unknown)
        echo "not a PR or branch build"
        echo "exiting(ok)..."
        exit 0
        ;;
    *)
        echo "unrecognized build type"
        echo "exiting(fail)..."
        exit 1
        ;;
esac
echo "detection succeeded: VERSION=${VERSION}"

if [ -z "$(find changelog.d -name '*.rst')" ]; then
    echo "no changes visible in changelog.d/"
    echo "exiting without running 'scriv collect'"
    exit 0
fi

scriv collect --keep --version "$VERSION" -v DEBUG
