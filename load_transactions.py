#!/usr/bin/env python
import sys
from argparse import ArgumentParser
from os import path

from rich.columns import Columns
from rich.panel import Panel
from rich.text import Text
from rich_argparse_plus import RichHelpFormatterPlus

from ethecycle.config import Config
from ethecycle.models.blockchain import BLOCKCHAINS
from ethecycle.models.token import Token
from ethecycle.neo4j import Neo4j
from ethecycle.transaction_loader import load_into_neo4j
from ethecycle.util.filesystem_helper import files_in_dir
from ethecycle.util.logging import ask_for_confirmation, console, set_log_level
from ethecycle.util.number_helper import MEGABYTE
from ethecycle.util.string_constants import DEBUG, ETHEREUM

INCREMENTAL_LOAD_WARNING = Text("\nYou selected incremental import which probably doesn't work.\n", style='red')
INCREMENTAL_LOAD_WARNING.append('  Did you forget the --drop option?', style='bright_red')
SPLIT_BIG_FILES_THRESHOLD = 100 * MEGABYTE
LIST_TOKEN_SYMBOLS = '--list-token-symbols'
DEFAULT_DEBUG_LINES = 5

Token.chain_addresses()  # Force load from DB

CONFIGURED_TOKENS = set([
    symbol
    for _blockchain, symbol_tokens in Token._by_blockchain_symbol.items()
    for symbol in symbol_tokens.keys()
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

parser.add_argument('-p', '--preserve-csvs', action='store_true',
                    help="remove (delete) extracted data CSVs once they have been loaded")

parser.add_argument('-D', '--debug', action='store_true',
                    help='show debug level log output')

parser.add_argument(LIST_TOKEN_SYMBOLS, action='store_true',
                    help='show all configured tokens selectable with --token and exit')


# Parse args
if LIST_TOKEN_SYMBOLS in sys.argv:
    console.print(Panel('Known Token Symbols'))
    console.line()
    console.print(Columns(sorted(list(CONFIGURED_TOKENS))))
    console.line()
    sys.exit()

args = parser.parse_args()

if args.debug:
    Config.debug = True
    set_log_level(DEBUG)

if args.drop:
    Config.drop_database = True
else:
    ask_for_confirmation(INCREMENTAL_LOAD_WARNING)

if args.extract_only:
    Config.extract_only = True

if args.token and args.token not in CONFIGURED_TOKENS:
    raise ValueError(f"'{args.token}' is not a known symbol. Try --list-token-symbols to see options.")

if args.preserve_csvs:
    Config.preserve_csvs = True

# Make sure we are passing a list of paths and not just a single path
if path.isfile(args.csv_path):
    txn_csvs = [args.csv_path]
elif path.isdir(args.csv_path):
    console.print(f"Directory detected, loading all files from '{args.csv_path}'...", style='bright_cyan')
    txn_csvs = files_in_dir(args.csv_path)
else:
    raise ValueError(f"'{args.csv_path}' is not a filesystem path")

load_into_neo4j(txn_csvs, args.blockchain, args.token)

if args.drop:
    Neo4j().create_indexes()
