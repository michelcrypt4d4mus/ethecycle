from gremlin_python.driver.driver_remote_connection import \
    DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __, unfold
from gremlin_python.process.traversal import Column

from ethecyle.logging import print_wallet_header
from ethecyle.transaction_loader import UDST_ADDRESS, get_wallets_txions

wallets_txns = get_wallets_txions(UDST_ADDRESS)
wallet_addresses = set(list(wallets_txns.keys()))
graph = traversal().withRemote(DriverRemoteConnection('ws://tinkerpop:8182/gremlin', 'g'))


# Add wallets as vertices
graph.inject([{'address': address} for address in wallet_addresses]).unfold().as_('wallet'). \
    addV('wallet').as_('v'). \
        sideEffect(
            __.select('wallet').unfold().as_('kv').select('v'). \
                property(__.select('kv').by(Column.keys), __.select('kv').by(Column.values))
    ).iterate()


def count_vertices(g) -> int:
    return g.V().hasLabel('wallet').count().next()



# Adding vertices one at a time is very slow
#for wallet_address in wallet_addresses:
#    graph.addV('wallet').property('name','Julia Child').property('gender','F')


# graph.inject(wallet_addresses).unfold().as_('wallet'). \
#     addV('wallet').as_('v'). \
#         sideEffect(
#             __.select('wallet').unfold().as_('kv').select('v'). \
#                 property(__.select('kv').by(Column.keys), __.select('kv').by(Column.values))
#     ).iterate()


# graph.inject(wallet_addresses).unfold().as_('address'). \
#     addV('address').as_('v'). \
#         sideEffect(__.select('address').unfold().as_('kv').select('v'). \
#             property(__.select('kv').by(Column.keys), _.select('kv').by(Column.values))).iterate()



# for wallet_address, txns in wallets_txns.items():
#     print_wallet_header(wallet_address, txns)

#     # __ or _ ?
#     graph.inject(wallet_addresses).unfold().as_('entity'). \
#         addV('entity').as_('v'). \
#             sideEffect(__.select('entity').unfold().as_('kv').select('v'). \
#                 property(__.select('kv').by(Column.keys), __.select('kv').by(Column.values))).iterate()


