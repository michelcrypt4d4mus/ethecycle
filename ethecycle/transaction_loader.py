"""
Load transactions from CSV as python lists and/or directly into the graph database.
"""
import csv
from itertools import groupby
from os.path import basename
from typing import Dict, List, Optional

from gremlin_python.structure.graph import GraphTraversalSource
from rich.text import Text

from ethecycle.blockchains import get_chain_info
from ethecycle.export.graphml import GRAPHML_EXTENSION, export_graphml, pretty_print_xml_file
from ethecycle.graph import g
from ethecycle.transaction import Txn
from ethecycle.util.filesystem_helper import GRAPHML_OUTPUT_DIR
from ethecycle.util.logging import console
from ethecycle.util.string_constants import ETHEREUM
from ethecycle.util.types import WalletTxns

time_sorter = lambda txn: txn.block_number
wallet_sorter = lambda txn: txn.from_address


def load_txn_csv_to_graph(
        txn_csv_path: str,
        blockchain: str,
        token: str,
        debug: bool = False
    ) -> GraphTraversalSource:
    """Load txns from a CSV file, filter them for token_address only, and load to graph via GraphML."""
    wallets_txns = get_wallets_txions(txn_csv_path, blockchain, token)
    output_file_path = str(GRAPHML_OUTPUT_DIR.joinpath(basename(txn_csv_path) + GRAPHML_EXTENSION))
    export_graphml(wallets_txns, ETHEREUM, output_file_path)

    if debug:
        pretty_print_xml_file(output_file_path)

    console.print(f"Loading graphML from '{output_file_path}'...")
    g.io(output_file_path).read().iterate()
    return g


def get_wallets_txions(file_path: str, blockchain: str, token: Optional[str] = None) -> WalletTxns:
    """Get all txns for a given token"""
    txns = sorted(load_txion_csv(file_path, blockchain, token), key=wallet_sorter)

    return {
        from_address: sorted(list(txns), key=time_sorter)
        for from_address, txns in groupby(txns, wallet_sorter)
    }


def load_txion_csv(file_path: str, blockchain: str, token: Optional[str] = None) -> List[Txn]:
    """Load txions from a CSV, optionally filtered for 'token' records only."""
    chain_info = get_chain_info(blockchain)
    token_address = None

    if not (token is None or token in chain_info.tokens()):
        raise ValueError(f"Address for '{token}' token not found.")

    msg = Text('Loading ').append(blockchain, style='color(112)').append(' ')

    if token:
        msg.append(token + ' ', style='color(207)')
        token_address = chain_info.token_address(token)

    console.print(msg.append(f"transactions from '").append(file_path, 'green').append("'..."))

    with open(file_path, newline='') as csvfile:
        # for row in csv.reader(csvfile, delimiter=','):
        #     console.print(f"ROW: {row}")
        txns = [
            Txn(*([blockchain] + row)) for row in csv.reader(csvfile, delimiter=',')
            if row[0] != 'token_address' and (token is None or row[0] == token_address)
        ]

        return txns
