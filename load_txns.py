#!/usr/local/bin/python
from ethecycle.graph import Graph
from ethecycle.transaction_loader import load_txns_to_graph
from ethecycle.util.string_constants import TOKENS, USDT

TRANSACTION_FILE = '/trondata/output_1000_lines.csv'

Graph.delete_graph()
load_txns_to_graph(TRANSACTION_FILE, USDT)
