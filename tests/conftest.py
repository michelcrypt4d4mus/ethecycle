from os import environ, path, pardir, remove

import pytest

from ethecycle.chain_addresses.address_db import drop_and_recreate_tables
from ethecycle.util.filesystem_helper import PROJECT_ROOT_DIR


@pytest.fixture(scope='session', autouse=True)
def reset_database():
    drop_and_recreate_tables()
