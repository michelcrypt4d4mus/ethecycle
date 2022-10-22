from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.structure.graph import GraphTraversalSource

TINKERPOP_URI = 'ws://tinkerpop:8182/gremlin'


def get_graph() -> GraphTraversalSource:
    return traversal().withRemote(DriverRemoteConnection(TINKERPOP_URI, 'g'))
