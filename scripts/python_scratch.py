from gremlin_python.process.traversal import T

from ethecycle.graph import *

wallet_addresses = [w[T.id] for w in get_wallets(2)]
#find_cycles_from_wallets(wallet_addresses, 3)


g.V().has('code','SAF').repeat(out()).emit().path().by('code').limit(10)
