from gremlin_python.process.traversal import T

from ethecycle.graph import g, get_wallets, wallets_without_txns

wallet_addresses = [w[T.id] for w in get_wallets(2)]
#find_cycles_from_wallets(wallet_addresses, 3)


