from gremlin_python.driver.driver_remote_connection import \
    DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.structure import io

from ethecyle.export.gremlin_graphml import GRAPHML_OUTPUT_FILE

graph = traversal().withRemote(DriverRemoteConnection('ws://tinkerpop:8182/gremlin', 'g'))
#graph.io(GRAPHML_OUTPUT_FILE).with_(io.reader, io.graphml).read().iterate()
graph.io(GRAPHML_OUTPUT_FILE).read().iterate()
