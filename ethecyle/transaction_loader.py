import csv
from itertools import groupby
from typing import Dict, List, Optional

from gremlin_python.structure.graph import GraphTraversalSource

from ethecyle.transaction import Txn

USDT_ADDRESS = '0xdac17f958d2ee523a2206206994597c13d831ec7'.lower()
WETH_ADDRESS = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'.lower()
PILLAGERS_ADDRESS = '0x17f2fdd7e1dae1368d1fc80116310f54f40f30a9'.lower()

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


def write_graph(graph: GraphTraversalSource, output_file: str) -> None:
    """Write graph?"""
    graph.io(output_file).write().iterate()
