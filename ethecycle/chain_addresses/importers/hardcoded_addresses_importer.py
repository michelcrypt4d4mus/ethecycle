"""
Contains hardcoded chain address data.
"""
from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.chain_addresses.address_db import insert_addresses
from ethecycle.models.token import Token
from ethecycle.util.logging import print_address_import
from ethecycle.util.string_constants import ETHEREUM

HARDCODED = 'hardcoded'

# eth is not actually a token so this is a synthetic 'token'
HARDCODED_TOKENS = [
    Token(
        chain_info=Ethereum,
        token_type=None,
        address=Ethereum.ETH_ADDRESS,
        symbol=Ethereum.SHORT_NAME,
        name=ETHEREUM,
        decimals=0,  # TODO: is this right?
        data_source=HARDCODED
    )
]


def import_hardcoded_addresses():
    print_address_import(HARDCODED)
    insert_addresses(HARDCODED_TOKENS)
