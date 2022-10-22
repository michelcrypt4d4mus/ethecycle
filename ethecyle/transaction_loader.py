import csv
from itertools import groupby
from typing import Dict, List, Optional

from gremlin_python.structure.graph import GraphTraversalSource

from ethecycle.export.graphml import export_graphml, pretty_print_xml
from ethecycle.graph import get_graph
from ethecycle.transaction import Txn

time_sorter = lambda txn: txn.block_number
wallet_sorter = lambda txn: txn.from_address


def get_wallets_txions(file_path: str, token_address: str) -> Dict[str, List[Txn]]:
    """Get all txns for a given token"""
    txns = sorted(load_txion_csv(file_path, token_address), key=wallet_sorter)

    return {
        from_address: sorted(list(txns), key=time_sorter)
        for from_address, txns in groupby(txns, wallet_sorter)
    }


def load_txion_csv(file_path: str, token_address: Optional[str] = None) -> List[Txn]:
    """Load txions from a CSV."""
    with open(file_path, newline='') as csvfile:
        return [
            Txn(*row) for row in csv.reader(csvfile, delimiter=',')
            if row[0] != 'token_address' and (token_address is None or row[0] == token_address)
        ]


def load_txns_to_graph(txn_csv_file_path: str, token_address: str) -> GraphTraversalSource:
    """Load txns from a CSV file, filter them for token_address only, and load to graph via GraphML."""
    wallets_txns = get_wallets_txions(txn_csv_file_path, token_address)
    filename = export_graphml(wallets_txns, 'ethereum')
    pretty_print_xml()
    graph = get_graph()
    graph.io(filename).read().iterate()
    return graph


def write_graph(graph: GraphTraversalSource, output_file: str) -> None:
    """Write graph?"""
    graph.io(output_file).write().iterate()

