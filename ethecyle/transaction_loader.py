import csv
from itertools import groupby
from typing import Dict, List, Optional

from gremlin_python.structure.graph import GraphTraversalSource

from ethecyle.transaction import Txn

UDST_ADDRESS = '0xdac17f958d2ee523a2206206994597c13d831ec7'.lower()
WETH_ADDRESS = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'.lower()
PILLAGERS_ADDRESS = '0x17f2fdd7e1dae1368d1fc80116310f54f40f30a9'.lower()

wallet_sorter = lambda txn: txn.from_address
time_sorter = lambda txn: txn.block_number


def get_wallets_txions(token_address: str) -> Dict[str, List[Txn]]:
    """Get all txns for a given token"""
    txns = sorted(load_txions(token_address), key=wallet_sorter)

    return {
        from_address: sorted(list(txns), key=time_sorter)
        for from_address, txns in groupby(txns, wallet_sorter)
    }


def load_txions(token_address: Optional[str] = None) -> List[Txn]:
    with open('/trondata/data/output_15770001_15780000.csv', newline='') as csvfile:
        return [
            Txn(*row) for row in csv.reader(csvfile, delimiter=',')
            if row[0] != 'token_address' and (token_address is None or row[0] == token_address)
        ]


def write_graph(graph: GraphTraversalSource) -> None:
    graph.io(someOutputFile).write().iterate()
