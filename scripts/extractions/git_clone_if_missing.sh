#!/bin/bash
# Takes a git repo URL as $1, optional dirname for checkout as $2.
# If repo doesn't exist in $TOKEN_DATA_REPO_PARENT_DIR it will be checked out.

REPO_URL=$1
REPO_DIR=$2

if [[ -z $REPO_DIR ]]; then
    REPO_DIR=${REPO_URL##*/}
    REPO_DIR=${REPO_DIR%\.git}
fi

REPO_FULL_PATH="$TOKEN_DATA_REPO_PARENT_DIR/$REPO_DIR"

if [[ ! -d "$REPO_FULL_PATH" ]]; then
    echo "$REPO_URL is not checked out; cloning..."
    pushd "$TOKEN_DATA_REPO_PARENT_DIR"
    git clone $REPO_URL
    popd
else
    echo "$REPO_URL is already checked out."
fi

echo "$REPO_FULL_PATH"
