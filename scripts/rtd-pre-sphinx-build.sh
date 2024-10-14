#!/bin/bash

case "$READTHEDOCS_VERSION_TYPE" in
    external)  # PR builds
        ;;
    branch | tag | unknown)
        echo "not a PR build, exiting"
        exit 0
        ;;
    *)
        echo "unrecognized build type"
        exit 1
        ;;
esac

if [ -z "$(find changelog.d -name '*.rst')" ]; then
    echo "no changes visible in changelog.d/"
    echo "exiting without running 'scriv collect'"
    exit 0
fi

SDK_VERSION=$(grep '^__version__' src/globus_sdk/version.py | cut -d '"' -f2)
DEV_VERSION="${SDK_VERSION}-pr-${READTHEDOCS_VERSION_NAME}"

scriv collect --keep --version "$DEV_VERSION" -v DEBUG
