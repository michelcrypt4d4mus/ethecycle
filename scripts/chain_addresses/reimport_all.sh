#!/bin/bash
# Drop DB, recreate, and import all chain address data sources.

python -c 'from ethecycle.chain_addresses.importers import rebuild_chain_addresses_db; rebuild_chain_addresses_db()'
