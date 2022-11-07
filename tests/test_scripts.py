from os import path
from subprocess import CalledProcessError, check_output

from ethecycle.config import Config
from ethecycle.util.neo4j_helper import execute_cypher_query, _execute_shell_cmd_on_neo4j_container


def test_show_tokens(*args) -> str:
    assert check_output(['show_tokens']).decode()


def test_show_chain_addresses(*args) -> str:
    assert check_output(['show_chain_addresses']).decode()

