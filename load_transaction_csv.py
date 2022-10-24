#!/usr/local/bin/python
import sys
from argparse import ArgumentParser

from rich.columns import Columns
from rich.panel import Panel
from rich_argparse_plus import RichHelpFormatterPlus

from ethecycle.blockchains import BLOCKCHAINS
from ethecycle.graph import print_obj_counts, delete_graph, g
from ethecycle.transaction_loader import load_txn_csv_to_graph
from ethecycle.util.logging import console, print_headline, set_log_level
from ethecycle.util.string_constants import ETHEREUM

LIST_TOKEN_SYMBOLS = '--list-token-symbols'
DEFAULT_DEBUG_LINES = 5

CONFIGURED_TOKENS = set([
    token
    for chain_info in BLOCKCHAINS.values()
    for token in chain_info.tokens().keys()
])


# Argument parser
RichHelpFormatterPlus.choose_theme('prince')

parser = ArgumentParser(
    formatter_class=RichHelpFormatterPlus,
    description="Load transactions from a CSV into Gremlin graph via XML export/import."
)

parser.add_argument('csv_path', metavar='CSV_FILE', help='CSV containing transaction data')

parser.add_argument('-b', '--blockchain',
                    help='blockchain this CSV contains data for',
                    choices=BLOCKCHAINS.keys(),
                    default=ETHEREUM)

parser.add_argument('-t', '--token',
                    help='token symbol to filter transactions for (e.g. USDT, WETH)')

parser.add_argument('-n', '--no-drop', action='store_true',
                    help="don't drop the current graph before loading new data")

parser.add_argument('-D', '--debug',
                    help='debug output: shows full XML and optionally indicated number of elements in final graph',
                    nargs='?',
                    type=int,
                    metavar='LINES',
                    const=DEFAULT_DEBUG_LINES)

parser.add_argument(LIST_TOKEN_SYMBOLS, action='store_true',
                    help='show all configured tokens selectable with --token and exit')


# Parse args, run loader
if LIST_TOKEN_SYMBOLS in sys.argv:
    console.print(Panel('Known Token Symbols'))
    console.line()
    console.print(Columns(sorted(list(CONFIGURED_TOKENS))))
    console.line()
    sys.exit()

args = parser.parse_args()

if args.debug:
    console.log("Debug mode...")
    set_log_level('DEBUG')

if not args.no_drop:
    delete_graph()

if args.token and args.token not in CONFIGURED_TOKENS:
    raise ValueError(f"'{args.token}' is not a known symbol. Try --list-token-symbols to see options.")

load_txn_csv_to_graph(args.csv_path, args.blockchain, args.token, args.debug)

if args.debug:
    print_headline(f"Sample of {args.debug} Wallets in Graph")

    for node in g.V().limit(args.debug).elementMap().toList():
        console.print(node)

    print_headline(f"Sample of {args.debug} Transactions in Graph")

    for edge in g.E().limit(args.debug).elementMap().toList():
        console.print(edge)

print_obj_counts()
console.line()
