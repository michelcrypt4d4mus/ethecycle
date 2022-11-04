#!/bin/bash
# Connect to the sqlite chain address DB

DB_PATH=$(python -c 'from ethecycle.chain_addresses.db import *;print(CHAIN_ADDRESSES_DB_PATH)')
sqlite3 $DB_PATH
