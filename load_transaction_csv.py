#!/usr/local/bin/python
import sys
from argparse import ArgumentParser
from functools import partial
from os import path

from rich_argparse_plus import RichHelpFormatterPlus
from rich.columns import Columns
from rich.panel import Panel
from rich.text import Text

from ethecycle.blockchains import BLOCKCHAINS
from ethecycle.graph import print_obj_counts, delete_graph, g
from ethecycle.transaction_loader import load_txn_csv_to_graph
from ethecycle.util.filesystem_helper import files_in_dir, split_big_file
from ethecycle.util.num_helper import MEGABYTE, size_string
from ethecycle.util.logging import console, print_headline, set_log_level
from ethecycle.util.string_constants import ETHEREUM

SPLIT_BIG_FILES_THRESHOLD = 100 * MEGABYTE
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

parser.add_argument('csv_path',
                    help='either a CSV containing txion data or a directory containing multiple such CSVs')

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


# The real action is here.
load_csv = partial(load_txn_csv_to_graph, blockchain=args.blockchain, token=args.token, debug=args.debug)

if path.isfile(args.csv_path):
    file_size = path.getsize(args.csv_path)
    console.print(f"Loading {size_string(file_size)}) file", style='yellow')
    load_csv(args.csv_path)

    # in order to load in chunks you need to avoid duplicate vertices...
    # if file_size < SPLIT_BIG_FILES_THRESHOLD:
    #     load_csv(args.csv_path)
    # else:
    #     console.print(f"Large file ({size_string(file_size)}) detected, splitting...", style='yellow')
    #     files = split_big_file(args.csv_path)

    #     for file in files:
    #         load_csv(file)

    #     console.print(f"Load complete. NOT cleaning up {len(files)} in '{path.dirname(files[0])}'.")
elif path.isdir(args.csv_path):
    files = files_in_dir(args.csv_path)
    msg = Text("Directory with ", 'yellow').append(str(len(files)), style='cyan').append(' files detected...')
    console.print(msg)

    for file in files:
        args.csv_path(file)


if args.debug:
    print_headline(f"Sample of {args.debug} Wallets in Graph")

    for node in g.V().limit(args.debug).elementMap().toList():
        console.print(node)

    print_headline(f"Sample of {args.debug} Transactions in Graph")

    for edge in g.E().limit(args.debug).elementMap().toList():
        console.print(edge)

print_obj_counts()
console.line()
