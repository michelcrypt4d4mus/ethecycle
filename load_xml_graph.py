from gremlin_python.structure.graph import GraphTraversalSource

from ethecyle.export.graphml import GRAPHML_OUTPUT_FILE, export_graphml, pretty_print_xml
from ethecyle.transaction_loader import USDT_ADDRESS, get_wallets_txions
from ethecyle.graph import get_graph

TRANSACTION_FILE = '/trondata/output_1000_lines.csv'


def load_txns_to_graph() -> GraphTraversalSource:
    wallets_txns = get_wallets_txions('/trondata/output_1000_lines.csv', USDT_ADDRESS)
    filename = export_graphml(wallets_txns)
    graph = get_graph()
    graph.io(filename).read().iterate()
    return graph
