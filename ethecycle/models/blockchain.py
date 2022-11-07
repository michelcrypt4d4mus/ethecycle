from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional, Type, Union

from inflection import pluralize, titleize, underscore

from ethecycle.blockchains.binance_smart_chain import BinanceSmartChain
from ethecycle.blockchains.bitcoin import Bitcoin
from ethecycle.blockchains.bitcoin_cash import BitcoinCash
from ethecycle.blockchains.cardano import Cardano
from ethecycle.blockchains.chain_info import ChainInfo
from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.blockchains.litecoin import Litecoin
from ethecycle.blockchains.ripple import Ripple
from ethecycle.blockchains.tron import Tron
from ethecycle.util.logging import log
from ethecycle.util.string_constants import *


# Keys are lowercase underscore strings ('bitcoin_cash') values are ChainInfo subclasses
BLOCKCHAINS = {
    underscore(chain_info.__name__): chain_info
    for chain_info in ChainInfo.__subclasses__()
}


@dataclass
class Blockchain:
    """Class to hold a ChainInfo object along with a mapping from address strings to Address objs."""
    chain_info: Type[ChainInfo]
    addresses: Dict[str, 'Address'] = field(default_factory=dict)


def get_chain_info(blockchain: str) -> Type['ChainInfo']:
    """Return the ChainInfo subclass for 'blockchain' or create default ChainInfo on the fly."""
    if blockchain not in BLOCKCHAINS:
        log.debug(f"Using default ChainInfo for unknown blockchain: '{blockchain}'.")
        BLOCKCHAINS[blockchain] = type(titleize(blockchain), (ChainInfo,), {})

    return BLOCKCHAINS[blockchain]


def guess_chain_info_from_address(address: str) -> Optional[Type['ChainInfo']]:
    """Guess which chain the address is on from the address format. Not guaranteed accurate!"""
    for chain_info in BLOCKCHAINS.values():
        if chain_info.is_valid_address(address):
            return chain_info
