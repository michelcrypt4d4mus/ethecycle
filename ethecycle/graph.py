from typing import List, Optional

from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import GraphTraversal, out, unfold

TINKERPOP_URI = 'ws://tinkerpop:8182/gremlin'


class Graph:
    graph = traversal().withRemote(DriverRemoteConnection(TINKERPOP_URI, 'g'))

    @classmethod
    def count_vertices(cls) -> int:
        return cls.graph.V().hasLabel('vertex').count().next()

    @classmethod
    def count_vertices(cls) -> int:
        return cls.graph.V().hasLabel('vertex').count().next()

    @classmethod
    def count_edges(cls) -> int:
        return cls.graph.E().hasLabel('edge').count().next()

    @classmethod
    def delete_graph(cls) -> None:
        cls.graph.V().drop().iterate()

    @classmethod
    def vertices(cls, limit: int = 500) -> List[dict]:
        return cls.graph.V().limit(limit).elementMap().toList()

    @classmethod
    def edges(cls, limit: int = 500) -> List[dict]:
        return cls.graph.E().limit(limit).elementMap().toList()

    @classmethod
    def find_wallet(cls, wallet_address: str) -> Optional[dict]:
        return cls.graph.V(wallet_address).elementMap().next()

    @classmethod
    def write_graph(cls, output_file: str) -> None:
        """Write graph?"""
        cls.graph.io(output_file).write().iterate()

    @classmethod
    def find_cycles_query(cls, max_cycle_length: int) -> GraphTraversal:
        """
        Return query to find de-deuped cycles. Note that this does not respect the arrow of time (yet).
        Note you must call iterate() on the returned query (or explain(), or whatever).
        """
        return cls.graph.V().as_('a').repeat(out().simplePath()).times(max_cycle_length). \
            where(out().as_('a')).path(). \
            dedup().by(unfold().order().by(id).dedup().fold())
