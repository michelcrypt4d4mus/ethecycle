from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.structure.graph import GraphTraversalSource

TINKERPOP_URI = 'ws://tinkerpop:8182/gremlin'


def get_graph() -> GraphTraversalSource:
    return traversal().withRemote(DriverRemoteConnection(TINKERPOP_URI, 'g'))


def count_vertices() -> int:
    return get_graph().V().hasLabel('wallet').count().next()
    #return get_graph().V().count().next()


def delete_graph() -> None:
    graph = get_graph()
    graph.V().drop().iterate()
    #graph.E().drop().iterate()
