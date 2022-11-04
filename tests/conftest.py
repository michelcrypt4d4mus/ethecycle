from os import path

import pytest


@pytest.fixture
def txn_csv():
    return path.join(path.dirname(__file__), 'file_fixtures', 'test_txns.csv')


@pytest.fixture(autouse=True, scope='session')
def prep_db():
    """TODO: Insert test lookups into DB"""
    pass
