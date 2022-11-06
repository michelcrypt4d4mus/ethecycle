#!/bin/bash
# Should be run from *inside* the container to get a copy of the chain address DB *out of* the container.

cp "$CHAIN_ADDRESS_DATA_DIR/chain_addresses_sqlite.db" scripts/docker/container_files/
