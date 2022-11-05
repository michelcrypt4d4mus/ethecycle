#!/bin/bash
# Generate files required for initial container setup.

SCRIPT_PATH=$(dirname -- "$(readlink -f -- "$0";)";)
NEO4J_ENV_FILE="$SCRIPT_PATH/neo4j/.env.neo4j"

ssh-keygen -f "$SCRIPT_PATH/container_files/id_ed25519" -t ed25519 -C -q -N ""
cp "$NEO4J_ENV_FILE.example" "$NEO4J_ENV_FILE"
