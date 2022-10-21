from collections import defaultdict, namedtuple
from dataclasses import dataclass, replace
from itertools import groupby
from typing import Dict, List, Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.pretty import pprint
from rich.text import Text
from rich.tree import Tree

MAX_DEPTH = 4
MIN_VALUE = 100.0


def build_txn_tree(wallets_txns: Dict[str, List[Txn]], starting_txn: Txn, txn: Txn, depth: int = 0) -> None:
    """
    Start from the from_txn.to_address wallet, build a tree.

        wallet_txns: keys are wallet address, values is a list of txns from that wallet address
        starting_txn: root of tree whose to_address is checked for cycles (we could check for other cycles but for now we don't)
        txn: the current transaction being recursed upon
        depth: how far down the tree are we
    """
    if depth > MAX_DEPTH:
        #console.print("Hit max depth", style='red')
        return

    # Find all txns out of txn.to_address that happen in the future above the MIN_VALUE
    # Use block_number as an imperfect proxy for time
    txns_from_wallet_in_future = [
        t for t in wallets_txns[txn.from_address]
        if t.block_number >= txn.block_number and t != txn and t.value > MIN_VALUE
    ]

    log.debug(('#' * depth) + f": {txn.transaction_hash[0:12]} has {len(txns_from_wallet_in_future)} txns > {MIN_VALUE}")

    # If a cycle is encountered, color it
    if txn.to_address == starting_txn.from_address and depth > 0:
        console.print(f"Found cycle starting {starting_txn} to {txn}")

        for ancestor in txn.ancestors:
            if ancestor.style != 'white':
                ancestor.style = f"color({Txn.current_cycle_color}"

        Txn.current_cycle_color += 2

    # Add children nodes
    for future_txn in txns_from_wallet_in_future:
        # Make a copy because the same txn can appear multiple times in the tree
        # In a directed graph you wouldn't do this, but anytree is not a graph library, it's a tree library :(
        child_txn = replace(future_txn)
        child_txn.parent = txn
        build_txn_tree(wallets_txns, starting_txn, child_txn, depth + 1)
