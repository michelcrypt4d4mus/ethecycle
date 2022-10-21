from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection


g = traversal().withRemote(DriverRemoteConnection('ws://tinkerpop:8182/gremlin', 'g'))
