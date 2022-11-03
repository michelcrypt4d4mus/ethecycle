from os import environ
from typing import Optional

import sqllex as sx

from ethecycle.util.filesystem_helper import DB_DIR, PROJECT_ROOT_DIR
from ethecycle.util.string_constants import *

# TODO: code smell
if 'INVOKED_BY_PYTEST' in environ:
    DB_DIR = PROJECT_ROOT_DIR.joinpath('tests').joinpath('file_fixtures')

CHAIN_ADDRESSES_DB_FILE_NAME = 'chain_addresses.db'
CHAIN_ADDRESSES_DB_PATH = str(DB_DIR.joinpath(CHAIN_ADDRESSES_DB_FILE_NAME))

# Not for direct use. Access the DB through methods in wallet_db.py
# TODO: maybe instantiate without the connection? there's an arg for that i think...
_db: Optional[sx.SQLite3x] = None
