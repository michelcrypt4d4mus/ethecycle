from os import environ, path
from typing import Optional

import sqllex as sx

from ethecycle.config import Config
from ethecycle.util.filesystem_helper import PROJECT_ROOT_DIR, CHAIN_ADDRESS_DATA_DIR

CHAIN_ADDRESSES_DB_FILE_NAME = 'chain_addresses_sqlite.db'
CHAIN_ADDRESSES_DB_PATH = path.join(CHAIN_ADDRESS_DATA_DIR, CHAIN_ADDRESSES_DB_FILE_NAME)


# Not for direct use. Access the DB through methods in wallet_db.py
# TODO: maybe instantiate without the connection? there's an arg for that i think...
_db: Optional[sx.SQLite3x] = None


def print_chain_addresses_db_path() -> None:
    print(CHAIN_ADDRESSES_DB_PATH)
