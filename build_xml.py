from ethecyle.export.graphml import export_graphml
from ethecyle.transaction_loader import USDT_ADDRESS, get_wallets_txions

wallets_txns = get_wallets_txions('/trondata/output_1000_lines.csv', USDT_ADDRESS)
export_graphml(wallets_txns, 'ethereum')
