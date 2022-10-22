from ethecycle.transaction_loader import load_txns_to_graph
from ethecycle.util.string_constants import USDT_ADDRESS

TRANSACTION_FILE = '/trondata/output_1000_lines.csv'

load_txns_to_graph(TRANSACTION_FILE, USDT_ADDRESS)
