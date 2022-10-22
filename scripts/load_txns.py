from ethecycle.graph import count_vertices, delete_graph
from ethecycle.transaction_loader import load_txns_to_graph
from ethecycle.util.string_constants import USDT_ADDRESS

TRANSACTION_FILE = '/trondata/output_1000_lines.csv'

delete_graph()
load_txns_to_graph(TRANSACTION_FILE, USDT_ADDRESS)
