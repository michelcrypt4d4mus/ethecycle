#import code
import csv
import logging
from collections import defaultdict, namedtuple
from dataclasses import dataclass, replace
from itertools import groupby
from typing import Dict, List

from anytree import NodeMixin, RenderTree
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.pretty import pprint
from rich.text import Text
from rich.tree import Tree

# This transaction sends tokens other than WETH in the interntal txns
# https://etherscan.io/tx/0x674b78361f197aa20495be7e2a335eddbb9e324330213477883fe4af1676afa4
3
# ['0x96939020e626b31d9888d7f9c26a767802e6047a',
#  '0xca94644e7f8e594f50a6764f6f3738bf574366ea',
#  '0x96939020e626b31d9888d7f9c26a767802e6047a',
#  '1522997066457498936934',
#  '0x674b78361f197aa20495be7e2a335eddbb9e324330213477883fe4af1676afa4',
#  '107',
#  '15770279']

LOG_LEVEL = 'WARN'

COL_NAMES = ['token_address', 'from_address', 'to_address', 'value', 'transaction_hash', 'log_index', 'block_number']
WETH = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'.lower()
START_CYCLE_COLOR = 52
MILLION = 1000000
BILLION = MILLION * 1000
MAX_DEPTH = 4
MIN_VALUE = 100.0

console = Console()
wallet_sorter = lambda txn: txn.from_address
time_sorter = lambda txn: txn.block_number
log = logging.getLogger('cycle_finder')
log.addHandler(RichHandler(rich_tracebacks=True))
log.setLevel(LOG_LEVEL)
log.handlers[0].setLevel(LOG_LEVEL)


@dataclass
class Txn(NodeMixin):
    token_address: str
    from_address: str
    to_address: str
    csv_value: float
    transaction_hash: str
    log_index: str
    block_number: int

    def __post_init__(self):
        self.value = float(self.csv_value) / 10 ** 18
        self.value_str = "{:,.1f}".format(self.value)
        #self.value = int(self.value)
        self.block_number = int(self.block_number)
        self.style = 'white'

    def print_tree(self):
        #console.print(Panel(f"Tree From {self.transaction_hash}"))

        for pre, _fill, txn in RenderTree(self):
            console.print(Text(pre) + txn.__rich__())

    def __rich__(self) -> Text:
        txt = Text('<', style=self.style).append(self.transaction_hash[:8], style='magenta')
        txt.append(', To: ').append(self.to_address[:8], style='color(222)').append(', value: ')
        return txt.append(f"{self.value_str}", style='cyan').append('>')

    def __str__(self) -> str:
        return self.__rich__().plain

    def __eq__(self, other: 'Txn'):
        return self.transaction_hash == other.transaction_hash


Txn.current_cycle_color = START_CYCLE_COLOR


def build_txn_tree(wallets_txns: Dict[str, List[Txn]], starting_txn: Txn, txn: Txn, depth: int = 0):
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


def get_token_txions(token_address) -> Dict[str, List[Txn]]:
    """Get all txns for a given token"""
    with open('data/output_15770001_15780000.csv', newline='') as csvfile:
        txns = [Txn(*row) for row in csv.reader(csvfile, delimiter=',') if row[0] == token_address]

    txns = sorted(txns, key=wallet_sorter)

    return {
        from_address: sorted(list(txns), key=time_sorter)
        for from_address, txns in groupby(txns, wallet_sorter)
    }


def _count_col_vals(tuples, col: str):
    counts = defaultdict(lambda: 0)

    for txn in tuples:
        counts[getattr(txn, col)] += 1

    pprint(sorted(counts.items(), key=lambda r: r[1], reverse=True)[0:100])

