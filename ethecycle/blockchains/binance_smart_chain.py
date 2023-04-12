import re
from ethecycle.blockchains.chain_info import ChainInfo


class BinanceSmartChain(ChainInfo):
    SHORT_NAME = 'bsc'
    NAME_REGEX = re.compile('\\s*binance\\s*smart\\s*chain$', re.IGNORECASE)
    ADDRESS_PREFIXES = ['bnb', '0x']
    ADDRESS_LENGTH = 42

    @classmethod
    def chain_string(cls) -> str:
        return 'bsc'
