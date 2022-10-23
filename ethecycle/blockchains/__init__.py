from typing import Type

from ethecycle.blockchains.chain_info import ChainInfo
from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.util.string_constants import ETHEREUM

BLOCKCHAINS = {
    ETHEREUM: Ethereum
}


def get_chain_info(blockchain: str) -> Type[ChainInfo]:
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unknown blockchain '{blockchain}'.")

    return BLOCKCHAINS[blockchain]
