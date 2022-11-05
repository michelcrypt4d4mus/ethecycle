from os import path

from ethecycle.config import Config
from ethecycle.util.neo4j_helper import execute_cypher_query

from tests.test_load_transactions import CYPHERQL_QUERY

TXN_CSV = path.join(path.dirname(__file__), 'file_fixtures', 'test_txns.csv')


def test_execute_cypher_query():
    result = execute_cypher_query(CYPHERQL_QUERY)
    assert result.startswith('txn_count')
