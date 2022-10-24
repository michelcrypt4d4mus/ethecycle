from typing import Dict
from urllib.parse import urljoin

from ethecycle.blockchains.chain_info import ChainInfo
from ethecycle.util.string_constants import *


class Ethereum(ChainInfo):
    ADDRESS_LENGTH = 42
    TXN_HASH_LENGTH = 66
    SCANNER_BASE_URI = 'https://etherscan.io/'
    TOKEN_INFO_DIR = 'eth'

    TOKENS = {
        USDT: '0xdac17f958d2ee523a2206206994597c13d831ec7'.lower(),
        WETH: '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'.lower(),
        'PILLAGERS': '0x17f2fdd7e1dae1368d1fc80116310f54f40f30a9'.lower(),
    }

    @classmethod
    def token_addresses(cls) -> Dict[str, str]:
        return cls.TOKENS

    @classmethod
    def scanner_url(cls, address: str) -> str:
        address_length = len(address)

        if address_length == cls.ADDRESS_LENGTH:
            return cls._build_scanner_url(ADDRESS, address)
        elif address_length == cls.TXN_HASH_LENGTH:
            return cls._build_scanner_url('tx', address)
        else:
            raise ValueError(f"{cls}: {address} has length {address_length}, cannot create etherscan URL")

    @classmethod
    def token_info_dir(cls) -> str:
        return cls.TOKEN_INFO_DIR

    @classmethod
    def _build_scanner_url(cls, restful_path: str, address: str) -> str:
        return urljoin(cls.SCANNER_BASE_URI, f"{restful_path}/{address}")
