from os import environ, path
from typing import Optional

import sqllex as sx

from ethecycle.util.filesystem_helper import PROJECT_ROOT_DIR, TOKEN_DATA_REPO_PARENT_DIR

if 'INVOKED_BY_PYTEST' in environ:
    DB_DIR = PROJECT_ROOT_DIR.joinpath('tests').joinpath('file_fixtures')
else:
    DB_DIR = TOKEN_DATA_REPO_PARENT_DIR

CHAIN_ADDRESSES_DB_FILE_NAME = 'chain_addresses.db'
CHAIN_ADDRESSES_DB_PATH = path.join(DB_DIR, CHAIN_ADDRESSES_DB_FILE_NAME)

# Not for direct use. Access the DB through methods in wallet_db.py
# TODO: maybe instantiate without the connection? there's an arg for that i think...
_db: Optional[sx.SQLite3x] = None
