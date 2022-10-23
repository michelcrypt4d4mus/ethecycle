from gremlin_python.process.traversal import T

from ethecycle.graph import find_cycles_from_wallets, g, wallets

wallet_addresses = [w[T.id] for w in wallets(2)]

#find_cycles_from_wallets(wallet_addresses, 3)


g.V(*wallet_addresses).outE().count()
