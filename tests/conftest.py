from os import path

import pytest

from ethecycle.models.wallet import Wallet


@pytest.fixture
def txn_csv():
    return path.join(path.dirname(__file__), 'file_fixtures', 'test_txns.csv')


@pytest.fixture(autouse=True, scope='session')
def prep_db():
    """Pre-loads DB objects"""
    Wallet.chain_addresses()
