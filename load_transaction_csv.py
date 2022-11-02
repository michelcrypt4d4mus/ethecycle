#!/usr/bin/env python
import sys
from argparse import ArgumentParser
from os import path

from rich.columns import Columns
from rich.panel import Panel
from rich_argparse_plus import RichHelpFormatterPlus

from ethecycle.blockchains import BLOCKCHAINS
from ethecycle.config import Config
from ethecycle.transaction_loader import create_neo4j_bulk_load_csvs
from ethecycle.util.logging import console, set_log_level
from ethecycle.util.num_helper import MEGABYTE
from ethecycle.util.string_constants import DEBUG, ETHEREUM

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

parser.add_argument('-d', '--drop', action='store_true',
                    help="drop and recreate the database")

parser.add_argument('-e', '--extract-only', action='store_true',
                    help="extract and transform but do not load (will display a command that can load)")

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
    set_log_level(DEBUG)

if args.drop:
    Config.drop_database = True

if args.extract_only:
    Config.extract_only = True

if args.token and args.token not in CONFIGURED_TOKENS:
    raise ValueError(f"'{args.token}' is not a known symbol. Try --list-token-symbols to see options.")

# Actual loading happens here
create_neo4j_bulk_load_csvs(args.csv_path, args.blockchain, args.token)
