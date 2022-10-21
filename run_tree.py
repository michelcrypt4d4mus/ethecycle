from dataclasses import replace

from rich.panel import Panel
from rich.text import Text

from find_cycles import *


def print_wallet_header(wallet_address, wallet_txns):
    console.line(2)
    txt = Text('Wallet ').append(wallet_address, style='green').append(' has ')
    txt.append(str(len(wallet_txns)), style='cyan').append(' txns')
    console.print(Panel(txt, expand=False))

wallets_txns = get_token_txions(WETH)
first_txn = list(wallets_txns.values())[0][0]

for wallet_address, txns in wallets_txns.items():
    print_wallet_header(wallet_address, txns)
    first_wallet_txn = replace(txns[0])
    build_txn_tree(wallets_txns, first_wallet_txn, first_wallet_txn)
    first_wallet_txn.print_tree()
