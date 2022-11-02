#!/bin/bash
# Import data scraped from Dune Analytics dashboards.

python -c 'from ethecycle.data.chain_addresses.importers import rebuild_chain_addresses_db; rebuild_chain_addresses_db()'
