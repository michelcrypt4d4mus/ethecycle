from os import path
from subprocess import CalledProcessError, check_output

from ethecycle.config import Config
from ethecycle.util.neo4j_helper import execute_cypher_query, _execute_shell_cmd_on_neo4j_container

TXN_CSV = path.join(path.dirname(__file__), 'file_fixtures', 'test_txns.csv')
CYPHERQL_QUERY="""MATCH ()-[txn]->() RETURN COUNT(txn) AS txn_count"""
TEST_ENV_CANARY = 'cat /data/.keep_data'


def test_neo4j_load():
    _run_with_args('-d', TXN_CSV)


def _run_with_args(*args) -> str:
    if not Config.is_test_env:
        raise ValueError("Refusing to run load_transactions tests outside of test env")

    _check_neo4j_test_env_canary()
    return check_output(['./load_transactions.py', *args]).decode()


def _check_neo4j_test_env_canary():
    """Check if the neo4j server is really running the test env."""
    _execute_shell_cmd_on_neo4j_container(TEST_ENV_CANARY)
