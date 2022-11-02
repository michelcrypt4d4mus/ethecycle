"""
Contains hardcoded chain address data.
"""
from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.blockchains.token import Token
from ethecycle.data.chain_addresses.address_db import delete_rows_for_data_source, insert_tokens
from ethecycle.util.logging import console
from ethecycle.util.string_constants import ETHEREUM
from ethecycle.data.chain_addresses.db import TOKENS_TABLE_NAME

HARDCODED = 'hardcoded'

# eth is not actually a token so this is a synthetic 'token'
HARDCODED_TOKENS = [
    Token(
        blockchain=ETHEREUM,
        token_type=None,
        address=Ethereum.ETH_ADDRESS,
        symbol=Ethereum.ETH,
        name=ETHEREUM,
        decimals=0,  # TODO: is this right?
        data_source='hardcoded'
    )
]


def import_hardcoded_addresses():
    console.print("Importing hardcoded addresses...")
    delete_rows_for_data_source(TOKENS_TABLE_NAME, HARDCODED)
    insert_tokens(HARDCODED_TOKENS)
