#!/bin/bash
# Takes a git repo URL as $1, optional dirname for checkout as $2.
# If repo doesn't exist in $TOKEN_DATA_REPO_PARENT_DIR it will be checked out.
# TODO: prolly should be reimplemented in python...

REPO_URL=$1
REPO_DIR=$2

if [[ -z $REPO_DIR ]]; then
    REPO_DIR=${REPO_URL##*/}
    REPO_DIR=${REPO_DIR%\.git}
fi

REPO_FULL_PATH="$TOKEN_DATA_REPO_PARENT_DIR/$REPO_DIR"

if [[ ! -d "$REPO_FULL_PATH" ]]; then
    echo "$REPO_URL is not checked out; cloning..." >&2
    pushd "$TOKEN_DATA_REPO_PARENT_DIR" >> /dev/null
    git clone $REPO_URL >&2
    popd >> /dev/null
else
    echo "$REPO_URL is already checked out." >&2
fi

echo "$REPO_FULL_PATH"
