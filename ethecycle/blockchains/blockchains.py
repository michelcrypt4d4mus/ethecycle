"""
Metadata and constants having to do with the various different blockchains.
"""
import re
from collections import namedtuple
from typing import Dict, Optional, Type

from inflection import titleize, underscore

from ethecycle.blockchains.binance_smart_chain import BinanceSmartChain
from ethecycle.blockchains.bitcoin import Bitcoin
from ethecycle.blockchains.bitcoin_cash import BitcoinCash
from ethecycle.blockchains.cardano import Cardano
from ethecycle.blockchains.chain_info import ChainInfo
from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.blockchains.litecoin import Litecoin
from ethecycle.blockchains.ripple import Ripple
from ethecycle.blockchains.tron import Tron
from ethecycle.util.dict_helper import get_dict_key_by_value
from ethecycle.util.logging import log
from ethecycle.util.string_constants import *

# Keys are lowercase underscore strings ('bitcoin_cash') values are ChainInfo subclasses
BLOCKCHAINS = {
    underscore(chain_info.__name__): chain_info
    for chain_info in ChainInfo.__subclasses__()
}

# Chain IDs are from chainlist.org: https://github.com/DefiLlama/chainlist/blob/main/constants/chainIds.js
CHAIN_IDS = {
    0: "kardia",
    4: "rinkeby",  # Ethereum testnet for dApps
    1: ETHEREUM,
    8: "ubiq",
    10: "optimism",
    19: "songbird",
    20: "elastos",
    25: "cronos",
    30: "rsk",
    40: "telos",
    50: "xdc",
    52: "csc",
    55: "zyx",
    56: "binance smart chain",
    57: "syscoin",
    60: "gochain",
    61: "ethereumclassic",
    66: "okexchain",
    70: "hoo",
    82: "meter",
    87: "nova network",
    88: "tomochain",
    100: "xdai",
    106: "velas",
    108: "thundercore",
    122: "fuse",
    128: "heco",
    137: "polygon",
    200: "xdaiarb",
    246: "energyweb",
    250: "fantom",
    269: "hpb",
    288: "boba",
    321: "kucoin",
    336: "shiden",
    361: "theta",
    416: "sx",
    534: "candle",
    592: "astar",
    820: "callisto",
    888: "wanchain",
    1088: "metis",
    1231: "ultron",
    1284: "moonbeam",
    1285: "moonriver",
    2000: "dogechain",
    2020: "ronin",
    2222: "kava",
    4689: "iotex",
    5050: "xlc",
    5551: "nahmii",
    6969: "tombchain",
    7700: "canto",
    8217: "klaytn",
    9001: "evmos",
    10000: "smartbch",
    32659: "fusion",
    42161: "arbitrum",
    42170: "arb-nova",
    42220: "celo",
    42262: "oasis",
    43114: "avalanche",
    47805: "rei",
    55555: "reichain",
    71402: "godwoken",
    333999: "polis",
    888888: "vision",
    1313161554: "aurora",
    1666600000: "harmony",
    11297108109: "palm",
    836542336838601: "curio"
}


def get_chain_info(blockchain: str):
    """Return the ChainInfo subclass for 'blockchain' or create default ChainInfo on the fly."""
    if blockchain not in BLOCKCHAINS:
        log.warning(f"Using default ChainInfo for unknown blockchain '{blockchain}'.")
        BLOCKCHAINS[blockchain] = type(titleize(blockchain), (ChainInfo,), {})

    return BLOCKCHAINS[blockchain]


def get_chain_id(blockchain: str) -> Optional[int]:
    """Lookup ID from CHAIN_IDS above."""
    return get_dict_key_by_value(CHAIN_IDS, blockchain)


def guess_chain_info_from_address(address: str) -> Optional[Type[ChainInfo]]:
    """Guess which chain the address is on from the address format. Not guaranteed accurate!"""
    for chain_info in BLOCKCHAINS.values():
        if chain_info.is_valid_address(address):
            return chain_info
