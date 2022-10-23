#!/usr/local/bin/python
from argparse import ArgumentParser

from rich_argparse_plus import RichHelpFormatterPlus

from ethecycle.blockchains import BLOCKCHAINS
from ethecycle.graph import print_obj_counts, delete_graph, g
from ethecycle.transaction_loader import load_txn_csv_to_graph
from ethecycle.util.logging import console, print_headline, set_log_level
from ethecycle.util.string_constants import ETHEREUM

DEBUG_LINES = 5

CONFIGURED_TOKENS = set([
    token
    for chain_info in BLOCKCHAINS.values()
    for token in chain_info.token_addresses().keys()
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
                    help='token to filter transactions for',
                    choices=CONFIGURED_TOKENS)

parser.add_argument('-n', '--no-drop', action='store_true',
                    help="don't drop the current graph before loading new data")

parser.add_argument('-D', '--debug', action='store_true',
                    help='debug output (shows full XML, etc)')


# Parse args, run loader
args = parser.parse_args()

if args.debug:
    console.log("Debug mode...")
    set_log_level('DEBUG')

if not args.no_drop:
    delete_graph()

load_txn_csv_to_graph(args.csv_path, args.blockchain, args.token, args.debug)

if args.debug:
    print_headline(f"Sample of {DEBUG_LINES} Wallets in Graph")

    for node in g.V().limit(DEBUG_LINES).elementMap().toList():
        console.print(node)

    print_headline(f"Sample of {DEBUG_LINES} Transactions in Graph")

    for edge in g.E().limit(DEBUG_LINES).elementMap().toList():
        console.print(edge)

print_obj_counts()
console.line()
