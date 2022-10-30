#!/bin/bash
# Get a bash shell on neo4j container. Container will be launched if not currently running.

SCRIPT_PATH=$(dirname -- "$(readlink -f -- "$0";)";)
. $SCRIPT_PATH/neo4j_container_helper.sh

run_on_neo4j_container bash -l
