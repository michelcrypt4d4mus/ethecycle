from ethecyle.export.gremlin_graphml import export_xml
from ethecyle.transaction_loader import USDT_ADDRESS, get_wallets_txions

wallets_txns = get_wallets_txions('/trondata/output_1000_lines.csv', USDT_ADDRESS)
export_xml(wallets_txns)
