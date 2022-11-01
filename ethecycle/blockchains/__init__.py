import re
from collections import namedtuple
from typing import Type

from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.util.string_constants import *

ChainAbbrevation = namedtuple('ChainAbbrevation', ['chain_regex', 'abbreviation'])
ChainRegex = lambda pattern: re.compile(pattern, re.IGNORECASE)

BLOCKCHAINS = {
    ETHEREUM: Ethereum
}

CHAIN_ABBREVIATIONS = [
    ChainAbbrevation(ChainRegex(AVALANCHE), AVAX),
    ChainAbbrevation(ChainRegex('\\s*binance\\s*smart\\s*chain$'), 'bsc'),
    ChainAbbrevation(ChainRegex(ETHEREUM), Ethereum.ETH),
]


def get_chain_info(blockchain: str) -> Type['ChainInfo']:
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unknown blockchain '{blockchain}'.")

    return BLOCKCHAINS[blockchain]
