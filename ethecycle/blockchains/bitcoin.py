from ethecycle.blockchains.chain_info import ChainInfo
from ethecycle.util.logging import log


class Bitcoin(ChainInfo):
    SHORT_NAME = 'btc'
    ADDRESS_PREFIXES = ['1', '3', 'bc1', 'lnbc']  # lnbc is lightning
