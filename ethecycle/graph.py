from typing import List, Optional, Union

from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __, GraphTraversal, bothE, inE, out, outE, unfold
from gremlin_python.process.traversal import P, T
from gremlin_python.statics import load_statics

from ethecycle.util.logging import console
from ethecycle.util.string_constants import TXN, WALLET

TINKERPOP_URI = 'ws://tinkerpop:8182/gremlin'

# Load the common predicates into global variable space
# See: https://tinkerpop.apache.org/docs/current/reference/#gremlin-python-imports
load_statics(globals())
g = traversal().withRemote(DriverRemoteConnection(TINKERPOP_URI, 'g'))


def print_obj_counts() -> None:
    console.print(f"Graph contains {count_wallets()} wallets.")
    console.print(f"Graph contains {count_txns()} transactions.")


def count_wallets() -> int:
    """Count all wallet nodes"""
    return g.V().hasLabel(WALLET).count().next()


def count_txns() -> int:
    """Count all transaction edges."""
    return g.E().hasLabel(TXN).count().next()


def wallets_without_txns() -> int:
    """https://stackoverflow.com/questions/52857677/gremlin-query-to-get-the-list-of-vertex-not-connected-with-any-other-vertex"""
    return g.V().where(__.not_(bothE())).count().next()


def get_wallets(limit: int = 100) -> List[dict]:
    # Extract just the address strings: wallet_addresses = [w[T.id] for w in get_wallets(2)]
    return g.V().limit(limit).elementMap().toList()


def get_transactions(limit: int = 100) -> List[dict]:
    return g.E().limit(limit).elementMap().toList()


def find_wallet(wallet_address: str) -> Optional[dict]:
    return g.V(wallet_address).elementMap().next()


def delete_graph() -> None:
    """Reset graph to pristine state."""
    g.V().drop().iterate()


def write_graph(output_file: str) -> None:
    """Write graph?"""
    g.io(output_file).write().iterate()


def wallets_with_min_outbound_txns(num_transactions: int) -> List[dict]:
    """Wallets with minimum number of outbound txions"""
    return g.V().where(out().count().is_(P.gte(num_transactions))).elementMap().toList()


def wallets_with_min_outbound_txn_value(total_value: Union[float, int]) -> List[dict]:
    """Wallets with minimum number of outbound txions"""
    return g.V().where(outE().values('value').sum().is_(P.gte(total_value))).elementMap().toList()


def txns_from_wallet(address: str) -> List[dict]:
    return g.V(address).outE().elementMap().toList()


def txns_values_to_wallet(address: str) -> List[dict]:
    return g.V(address).inE().values('value').toList()


def find_cycles_from_wallets(addresses: Union[str, List[str]], max_cycle_length: int) -> GraphTraversal:
    """
    Return query to find de-deuped cycles. Note that this does not respect the arrow of time (yet).
    Note you must call iterate() on the returned query (or explain(), or whatever).
    Cycle Detection recipe: https://tinkerpop.apache.org/docs/current/recipes/#cycle-detection
    """
    addresses = addresses if isinstance(addresses, list) else [addresses]

    return g.V(*addresses).as_(WALLET).repeat(out().simplePath()).side_effect(lambda x: print(x)). \
        times(max_cycle_length). \
        where(out().as_(WALLET)).path(). \
        dedup().by(unfold().order().by(id).dedup().fold())


# https://stackoverflow.com/questions/40165426/gremlin-graph-traversal-that-uses-previous-edge-property-value-to-filter-later-e
def arrow_of_time(start_address: str):
    # (this comment should be next to the where() clause): compare with the first edge
    g.V(start_address).outE(). \
        as_('firstEdge'). \
        inV().outE(). \
        where(P.gt('firstEdge')).  \
        by('block_number') # // use only the 'weight' property for the equality check



# StackExchange:
# g.V('1','2','3','56').
#   sideEffect(
#     outE('route').
#     inV().
#     hasLabel('airport').
#     where(without('labels')).
#     limit(2).
#     aggregate('labels')).
#   sideEffect(
#     inE('contains').
#     outV().
#     hasLabel('country').
#     where(without('labels')).
#     limit(2).
#     aggregate('labels')).
#   cap('labels').
#   unfold().
#   values('desc')
