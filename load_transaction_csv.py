#!/usr/local/bin/python
from argparse import ArgumentParser

from rich_argparse_plus import RichHelpFormatterPlus

from ethecycle.graph import count_edges, count_vertices, delete_graph, g
from ethecycle.transaction_loader import load_txn_csv_to_graph
from ethecycle.util.logging import console, print_headline
from ethecycle.util.string_constants import TOKENS

DEBUG_LINES = 5

# Argument parser
RichHelpFormatterPlus.choose_theme('prince')

parser = ArgumentParser(
    formatter_class=RichHelpFormatterPlus,
    description="Load transactions from a CSV into Gremlin graph via XML export/import."
)

parser.add_argument('csv_path', metavar='CSV_FILE', help='CSV containing transaction data')

parser.add_argument('-t', '--token',
                    help='token to filter transactions for',
                    choices=TOKENS.keys())

parser.add_argument('-D', '--debug', action='store_true',
                    help='debug output (shows full XML, etc)')

# Parse args, run loader
args = parser.parse_args()
delete_graph()
load_txn_csv_to_graph(args.csv_path, args.token, args.debug)

if args.debug:
    print_headline(f"Sample of {DEBUG_LINES} Wallets in Graph")

    for node in g.V().limit(DEBUG_LINES).elementMap().toList():
        console.print(node)

    print_headline(f"Sample of {DEBUG_LINES} Transactions in Graph")

    for edge in g.E().limit(DEBUG_LINES).elementMap().toList():
        console.print(edge)

console.print(f"Loaded {count_vertices()} wallets.")
console.print(f"Loaded {count_edges()} transactions.")
