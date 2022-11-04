#!/bin/bash
# Connect to the sqlite chain address DB

DB_PATH=$(python -c 'from ethecycle.chain_addresses.db import *;print_chain_addresses_db_path()')
sqlite3 $DB_PATH
