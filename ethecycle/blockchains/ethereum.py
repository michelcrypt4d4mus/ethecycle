from typing import Dict
from urllib.parse import urljoin

from ethecycle.blockchains.chain_info import ChainInfo
from ethecycle.util.logging import log
from ethecycle.util.string_constants import *


class Ethereum(ChainInfo):
    ADDRESS_LENGTH = 42
    TXN_HASH_LENGTH = 66
    SCANNER_BASE_URI = 'https://etherscan.io/'
    TOKEN_INFO_DIR = 'eth'
    ETH_ADDRESS = '0x0'

    @classmethod
    def scanner_url(cls, address: str) -> str:
        address_length = len(address)

        if address_length == cls.ADDRESS_LENGTH:
            return cls._build_scanner_url(ADDRESS, address)
        elif address_length == cls.TXN_HASH_LENGTH:
            return cls._build_scanner_url('tx', address)
        elif address == cls.ETH_ADDRESS:
            return 'n/a'
        else:
            log.warning(f"Can't generate scanner URL for address '{address}'")
            return 'n/a'

    @classmethod
    def token_info_dir(cls) -> str:
        return cls.TOKEN_INFO_DIR

    @classmethod
    def _build_scanner_url(cls, restful_path: str, address: str) -> str:
        return urljoin(cls.SCANNER_BASE_URI, f"{restful_path}/{address}")
