from gremlin_python.structure.graph import GraphTraversalSource

from ethecyle.export.graphml import export_graphml, pretty_print_xml
from ethecyle.graph import get_graph
from ethecyle.transaction_loader import USDT_ADDRESS, get_wallets_txions

TRANSACTION_FILE = '/trondata/output_1000_lines.csv'


def load_txns_to_graph() -> GraphTraversalSource:
    wallets_txns = get_wallets_txions(TRANSACTION_FILE, USDT_ADDRESS)
    filename = export_graphml(wallets_txns)
    pretty_print_xml()
    graph = get_graph()
    graph.io(filename).read().iterate()
    return graph
