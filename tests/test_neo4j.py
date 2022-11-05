import pytest

from ethecycle.neo4j import Neo4j

QUERY = "MATCH ()-[txn]->() RETURN COUNT(txn)"
PATH_QUERY = "MATCH p=(w)-[txn]->()-[txn2]->() RETURN p, w, txn, txn2 LIMIT 10"


@pytest.fixture(scope='session')
def neo4j_db():
    neo4j_conn = Neo4j()
    yield neo4j_conn
    neo4j_conn.close()


def test_query_results_df(neo4j_db):
    assert neo4j_db.query_results_df(QUERY).at[0, 'COUNT(txn)'] == 5000


def test_query_results(neo4j_db):
    assert neo4j_db.query_results(QUERY)[0]['COUNT(txn)'] == 5000


def test_query_single_result(neo4j_db):
    assert neo4j_db.query_single_result(QUERY) == 5000


def test_query_result_graph(neo4j_db):
    result = neo4j_db.query_result_graph(PATH_QUERY)
