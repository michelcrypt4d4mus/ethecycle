#!/bin/bash

# Two files of interest in the whole repo that are not SQL (and thus very hard to parse):
#     ./spellbook/deprecated-dune-v1-abstractions/prices/bsc/coinpaprika.yaml
#     ./spellbook/deprecated-dune-v1-abstractions/prices/ethereum/coinpaprika.yaml

GIT_CLONE_IF_MISSING="$(dirname $0)/git_clone_if_missing.sh"
REPO_DIR=$($GIT_CLONE_IF_MISSING https://github.com/ltvm/spellbook.git)
rm -fr $REPO_DIR/.git
