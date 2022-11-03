from typing import Optional
from urllib.parse import urljoin

from ethecycle.blockchains.chain_info import ChainInfo
from ethecycle.util.logging import log
from ethecycle.util.string_constants import *


class Ethereum(ChainInfo):
    LABEL_CATEGORIES_SCRAPED_FROM_DUNE = ['cex', 'multisig', 'bridge', 'funds', 'mev', 'hackers']
    ADDRESS_PREFIXES = ['0x']
    ADDRESS_LENGTH = 42
    TXN_HASH_LENGTH = 66
    SCANNER_BASE_URI = 'https://etherscan.io/'
    ETH_ADDRESS = '0x0'  # Synthetic address because eth itself is not a token
    SHORT_NAME = 'eth'

    # TODO: Currently the data has been adjusted for decimal places, but in the future it may not be
    log.warning("Number of decimals for eth set to 0 but for some data sets it may be 18.")

    @classmethod
    def scanner_url(cls, address: str) -> Optional[str]:
        address_length = len(address)

        if address_length == cls.ADDRESS_LENGTH:
            return cls._build_scanner_url(ADDRESS, address)
        elif address_length == cls.TXN_HASH_LENGTH:
            return cls._build_scanner_url('tx', address)
        elif address == cls.ETH_ADDRESS:
            return None
        else:
            log.warning(f"Can't generate scanner URL for address '{address}'")
            return None

    @classmethod
    def extract_address_from_scanner_url(cls, scanner_url: str) -> str:
        return scanner_url.split('/')[-1]

    @classmethod
    def _build_scanner_url(cls, restful_path: str, address: str) -> str:
        return urljoin(cls.SCANNER_BASE_URI, f"{restful_path}/{address}")
