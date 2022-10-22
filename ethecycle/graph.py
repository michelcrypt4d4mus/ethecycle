from typing import Optional

from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.structure.graph import GraphTraversalSource

TINKERPOP_URI = 'ws://tinkerpop:8182/gremlin'


def get_graph() -> GraphTraversalSource:
    return traversal().withRemote(DriverRemoteConnection(TINKERPOP_URI, 'g'))


def count_vertices(graph: Optional[GraphTraversalSource] = None) -> int:
    graph = graph or get_graph()
    return graph.V().hasLabel('wallet').count().next()


def delete_graph(graph: Optional[GraphTraversalSource] = None) -> None:
    graph = graph or get_graph()
    graph.V().drop().iterate()
