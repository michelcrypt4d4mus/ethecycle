"""
Helper for generating dune queries to find new labels
TODO: Get this into the /scripts dir
"""
from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.chain_addresses.importers.wallets_from_dune_importer import DATA_SOURCE
from ethecycle.util.logging import console
from ethecycle.util.number_helper import comma_format
from ethecycle.util.string_helper import quoted_join

NEW_LABELS_QUERY = """
SELECT
  address,
  name
FROM labels.all
WHERE array_contains(blockchain, 'ethereum')
  AND category IN ({categories})
  AND address NOT IN (
    {addresses}
  )
ORDER BY 2
"""


def generate_ethereum_dune_labels_query():
    query = NEW_LABELS_QUERY.format(
        addresses=quoted_join(Ethereum.known_wallets().keys(), separator=',\n    '),
        categories=quoted_join(Ethereum.LABEL_CATEGORIES_SCRAPED_FROM_DUNE)
    )

    print(query)


def show_chain_addresses():
    """Print out a list of all chain addresses in the chain_addresses DB."""
    for _address, wallet in Ethereum.known_wallets().items():
        console.print(wallet)

    formatted = comma_format(len(Ethereum.known_wallets().keys()))
    console.print(f"\n\n    {formatted} wallet labels found for {Ethereum.chain_string()}.")
    console.line(2)


def show_tokens():
    for token in Ethereum.token_addresses().values():
        console.print(token)

    formatted = comma_format(len(Ethereum.token_addresses().keys()))
    console.print(f"\n\n    {formatted} tokens found for {Ethereum.chain_string()}.")
    console.line(2)
