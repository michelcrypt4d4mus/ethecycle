"""
Build the graph. Helpful: https://tinkerpop.apache.org/docs/current/recipes/#long-traversals
https://dkuppitz.github.io/gremlin-cheat-sheet/101.html
"""
from itertools import chain
from typing import List

from gremlin_python.process.graph_traversal import __, id_, select, unfold
from gremlin_python.process.traversal import Column
from gremlin_python.structure.graph import GraphTraversalSource

from ethecycle.graph import g
from ethecycle.transaction import Txn
from ethecycle.transaction_loader import get_wallets_txions
from ethecycle.util.string_constants import *

wallets_txns = get_wallets_txions('/trondata/output_1000_lines.csv', USDT)
wallet_addresses = list(wallets_txns.keys())
all_txns = list(chain(*wallets_txns.values()))


def add_wallets_as_vertices(wallet_addresses: List[str]) -> None:
    """Add wallets as vertices."""
    g.inject([{ADDRESS: address} for address in wallet_addresses]).unfold().as_(WALLET). \
        addV(WALLET).as_('v').sideEffect(
            __.select(WALLET).unfold().as_('kv').select('v'). \
                property(__.select('kv').by(Column.keys), __.select('kv').by(Column.values))
        ).iterate()



# Doesn't work yet... https://stackoverflow.com/questions/71406191/bulk-upsert-in-gremlin-python-fails-with-typeerror-graphtraversal-object-is
def build_graph(graph: GraphTraversalSource, txns: List[Txn], wallet_addresses: List[str]) -> None:
    """Add both vertices (wallets) and edges (txions) in one traversal."""
    wallets = [{'address': address} for address in wallet_addresses]
    graph.withSideEffect('txns', [t.__dict__ for t in txns]). \
        inject(wallets).sideEffect(
            unfold(). \
                addV(WALLET). \
                    property(id_, select('address')). \
                    group('m'). \
                    by(id_). \
                    by(unfold()) \
        ).select('txns').unfold().as_('t'). \
            addE(TXN). \
                from_(select('m').select(select('t').select('from_address'))). \
                to(select('m').select(select('t').select('to_address'))). \
                property(id_, select('transaction_id')). \
                property(NUM_TOKENS, select(NUM_TOKENS)) \
            .iterate()


build_graph(graph, all_txns, wallet_addresses)


# drop all vertices:
graph.V().drop().iterate()

# Adding vertices one at a time is very slow
#for wallet_address in wallet_addresses:
#    graph.addV(WALLET).property('name','Julia Child').property('gender','F')


# graph.inject(wallet_addresses).unfold().as_(WALLET). \
#     addV(WALLET).as_('v'). \
#         sideEffect(
#             __.select(WALLET).unfold().as_('kv').select('v'). \
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



# def add_txions_as_edges(txions: List[Txn]) -> None:
#     """Add transactions as edges between from_address and to_address."""
#     graph.inject([tx.__dict__ for tx in txions]).unfold().as_(TXN). \
#         addE(TXN).as_('e').sideEffect(
#             __.select(TXN).unfold().as_('kv').select('e'). \
#                 property(__.select('kv').by(Column.keys), __.select('kv').by(Column.values))
#         ).iterate()
