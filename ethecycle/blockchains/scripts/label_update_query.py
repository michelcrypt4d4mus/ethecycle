"""
Helper for generating dune queries to find new labels
TODO: Get this into the /scripts dir
"""
from rich.pretty import pprint

from ethecycle.blockchains.ethereum import Ethereum
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


def generate_ethereum_labels_query():
    Ethereum._load_wallet_label_file_contents()

    query = NEW_LABELS_QUERY.format(
        addresses=quoted_join(Ethereum._wallet_labels.keys(), separator=',\n    '),
        categories=quoted_join(Ethereum.WALLET_LABEL_CATEGORIES)
    )

    print(query)


def show_address_labels():
    for address, wallet_info in Ethereum.wallet_labels().items():
        pprint(address)
        pprint(wallet_info)
