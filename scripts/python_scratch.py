from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import (__, GraphTraversal, bothE, inE, out,
    outE, range_, unfold, values)
from gremlin_python.process.traversal import P, T
from gremlin_python.structure.graph import Path

from ethecycle.graph import g, print_paths, two_hops_from_wallet, wallets_with_outbound_txns_in_range
from ethecycle.util.logging import console
from ethecycle.util.num_helper import is_even
from ethecycle.util.string_constants import *

# Find some wallets
medium_wallets = wallets_with_outbound_txns_in_range(5, 10)
medium_wallet = medium_wallets[0]


# Show path walked - start and end point with edge txion IDs
for p in g.V(medium_wallets[0]).repeat(outE().inV()).emit().path().limit(10).toList():
    console.print("\nPATH", style='u')
    for i, path_element in enumerate(p):
        console.print(f"  Step {i}: {path_element}")


# Emit just the etherscan URLs and amounts or transactions
for p in g.V(medium_wallets[0]).repeat(outE().inV()).emit().path().by(SCANNER_URL).by(NUM_TOKENS).limit(100).toList():
    console.print("\nPATH", style='u')
    for i, path_element in enumerate(p):
        console.print(f"  Step {i}: {path_element}")


# Emit just wallet addresses and number tokens in transactions
for p in g.V(medium_wallets[0]).repeat(outE().inV()).emit().path().by(T.id).by(NUM_TOKENS).limit(100).toList():
    console.print("\nPATH", style='u')

    for i, path_element in enumerate(p):
        if is_even(i):
            console.print(f"  Step {i}: Wallet {path_element}")
        else:
            console.print(f"    Step {i}: Sent {path_element} tokens to:")


# Use by() with anonymous values().fold() to pull block number and amount
g.V(medium_wallet).outE().limit(5).path().by(values(BLOCK_NUMBER, NUM_TOKENS).fold()).toList()

# Show all properties of nodes and edges on two hops from medium_wallet
g.V(medium_wallet).outE().inV().outE().valueMap().toList()

# Chain of txions where each one came in a higher block_number than the last
g.V(medium_wallet).outE().as_('txn1').inV().outE().where(P.gt('txn1')).by(BLOCK_NUMBER).as_('txn2'). \
    inV().outE().where(P.gt('txn2')).by(BLOCK_NUMBER).inV().path().by(T.id).by(NUM_TOKENS).toList()


two_hops = g.V(medium_wallet).outE().as_('txn1').inV().outE().where(P.gt('txn1')).by(BLOCK_NUMBER).as_('txn2'). \
    inV().outE().where(P.gt('txn2')).by(BLOCK_NUMBER).inV().path().by(T.id).by(NUM_TOKENS).toList()


g.V(medium_wallet).repeat(outE().as_('txn1').inV().outE().where(P.gt('txn1')).by(BLOCK_NUMBER)).times(3). \
    inV().path().by(T.id).by(NUM_TOKENS).toList()
