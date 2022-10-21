from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.traversal import Column

from ethecyle.logging import print_wallet_header
from ethecyle.transaction_loader import UDST_ADDRESS, get_wallets_txions


wallets_txns = get_wallets_txions(UDST_ADDRESS)
wallet_addresses = set(list(wallets_txns.keys()))
graph = traversal().withRemote(DriverRemoteConnection('ws://tinkerpop:8182/gremlin', 'g'))

graph.inject(wallet_addresses).unfold().as_('entity'). \
    addV('entity').as_('v'). \
        sideEffect(_.select('entity').unfold().as_('kv').select('v'). \
            property(_.select('kv').by(Column.keys), _.select('kv').by(Column.values))).iterate()



for wallet_address, txns in wallets_txns.items():
    print_wallet_header(wallet_address, txns)

    graph.inject(wallet_addresses).unfold().as_('entity'). \
        addV('entity').as_('v'). \
            sideEffect(__.select('entity').unfold().as_('kv').select('v'). \
                property(__.select('kv').by(Column.keys), __.select('kv').by(Column.values))).iterate()


