#!/usr/local/bin/python
from argparse import ArgumentParser
from secrets import choice

from rich_argparse_plus import RichHelpFormatterPlus

from ethecycle.graph import Graph
from ethecycle.transaction_loader import load_txns_to_graph
from ethecycle.util.string_constants import TOKENS, USDT

TRANSACTION_FILE = '/trondata/output_1000_lines.csv'

RichHelpFormatterPlus.choose_theme('prince')


parser = ArgumentParser(
    formatter_class=RichHelpFormatterPlus,
    description="Load transactions from a CSV into Gremlin graph via XML export/import."
)

parser.add_argument('csv_path', metavar='CSV_FILE', help='CSV containing transaction data')

parser.add_argument('-t', '--token',
                    help='token to filter transactions for',
                    choices=TOKENS.keys())

args = parser.parse_args()
Graph.delete_graph()
load_txns_to_graph(args.csv_path, args.token)
