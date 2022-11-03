import re
from ethecycle.blockchains.chain_info import ChainInfo


class BinanceSmartChain(ChainInfo):
    SHORT_NAME = 'bsc'
    NAME_REGEX = re.compile('\\s*binance\\s*smart\\s*chain$', re.IGNORECASE)
    ADDRESS_PREFIXES = ['bnb']
