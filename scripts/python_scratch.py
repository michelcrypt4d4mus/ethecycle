from gremlin_python.process.traversal import T

from ethecycle.graph import *

wallet_addresses = [w[T.id] for w in get_wallets(2)]
medium_wallets = wallets_with_outbound_txns_in_range(5, 10)

g.V(medium_wallets[0]).repeat(out()).emit().path().limit(10).toList()

# Show path walked - start and end point with edge txion IDs
for p in g.V(medium_wallets[0]).repeat(outE().inV()).emit().path().limit(10).toList():
    console.print("\nPATH", style='u')
    for i, path_element in enumerate(p):
        console.print(f"  Step {i}: {path_element}")


# Page 43...
for p in g.V(medium_wallets[0]).repeat(outE().inV()).emit().path().limit(10).toList():
    console.print("\nPATH", style='u')
    for i, path_element in enumerate(p):
        console.print(f"  Step {i}: {path_element}")
