import csv
from itertools import groupby
from typing import Dict, List, Optional

from gremlin_python.structure.graph import GraphTraversalSource

from ethecycle.export.graphml import export_graphml, pretty_print_xml
from ethecycle.graph import Graph
from ethecycle.transaction import Txn
from ethecycle.util.string_constants import TOKENS

time_sorter = lambda txn: txn.block_number
wallet_sorter = lambda txn: txn.from_address


def load_txns_to_graph(txn_csv_file_path: str, token: str) -> GraphTraversalSource:
    """Load txns from a CSV file, filter them for token_address only, and load to graph via GraphML."""
    wallets_txns = get_wallets_txions(txn_csv_file_path, token)
    filename = export_graphml(wallets_txns, 'ethereum')
    pretty_print_xml()
    Graph.graph.io(filename).read().iterate()
    return Graph.graph


def get_wallets_txions(file_path: str, token: str) -> Dict[str, List[Txn]]:
    """Get all txns for a given token"""
    txns = sorted(load_txion_csv(file_path, token), key=wallet_sorter)

    return {
        from_address: sorted(list(txns), key=time_sorter)
        for from_address, txns in groupby(txns, wallet_sorter)
    }


def load_txion_csv(file_path: str, token: Optional[str] = None) -> List[Txn]:
    """Load txions from a CSV, optionally filtered for 'token' records only."""
    if not (token is None or token in TOKENS):
        raise ValueError(f"Address for '{token}' token not found.")

    with open(file_path, newline='') as csvfile:
        return [
            Txn(*row) for row in csv.reader(csvfile, delimiter=',')
            if row[0] != 'token_address' and (token is None or row[0] == TOKENS[token])
        ]
