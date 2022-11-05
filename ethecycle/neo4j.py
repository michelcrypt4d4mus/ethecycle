"""
Connect to neo4j; run queries.
Docs: https://neo4j.com/docs/api/python-driver/current/
"""
import re
from typing import Any, List, Optional

from neo4j import GraphDatabase, Record
from neo4j.graph import Graph
from pandas import DataFrame
from rich.text import Text

from ethecycle.util.filesystem_helper import PROJECT_ROOT_DIR
from ethecycle.util.logging import console
from ethecycle.util.neo4j_helper import neo4j_user_and_pass

INDEX_CQL_FILE = PROJECT_ROOT_DIR.joinpath('queries').joinpath('indexes.cql')


class Neo4j:
    def __init__(self):
        self.driver = GraphDatabase.driver("neo4j://neo4j:7687", auth=neo4j_user_and_pass())

    def close(self):
        self.driver.close()

    def query_results_df(self, cql: str) -> DataFrame:
        """Return pandas data frame."""
        return self.driver.session().run(cql).to_df()

    def query_results(self, cql: str) -> List[Record]:
        """Return list of query result rows."""
        with self.driver.session().begin_transaction() as tx:
            return list(tx.run(cql))

    def query_single_result(self, cql: str) -> Optional[Any]:
        """Return a single numeric/string/date/etc. value."""
        with self.driver.session().begin_transaction() as tx:
            result = tx.run(cql).single()

            if result is not None:
                return result.value()

    def query_result_graph(self, cql: str) -> Optional[Graph]:
        """Return in memory graph of all query results."""
        with self.driver.session().begin_transaction() as tx:
            return tx.run(cql).graph()

    def create_indexes(self):
        """Create indexes on txns and wallets."""
        with open(INDEX_CQL_FILE) as file:
            idx_queries = [q for q in file.read().split(';') if not re.match('\\s+', q, re.DOTALL)]
            print(idx_queries)

        with self.driver.session().begin_transaction() as tx:
            for idx_query in idx_queries:
                txt = Text("Creating index with query:", style='dim').append(idx_query, style='cyan')
                console.print(txt)
                tx.run(idx_query)
