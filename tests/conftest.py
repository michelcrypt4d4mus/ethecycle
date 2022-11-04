import pytest


@pytest.fixture
def txn_csv():
    return path.join(path.dirname(__file__), 'file_fixtures', 'test_txns.csv')
