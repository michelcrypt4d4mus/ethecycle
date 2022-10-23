"""
Simple class to hold blockchain specific info
"""
from abc import ABC, abstractmethod
from typing import Dict

from ethecycle.util.dict_helper import get_dict_key_by_value


class ChainInfo(ABC):
    @classmethod
    @abstractmethod
    def token_addresses(cls) -> Dict[str, str]:
        """Mapping of tokens (e.g. 'USDT') to addresses (e.g. '0x2323523fdsf')."""
        pass

    @classmethod
    @abstractmethod
    def scanner_url(cls, address: str) -> str:
        pass

    @classmethod
    def token_address(cls, token: str) -> str:
        return cls.token_addresses()[token]

    @classmethod
    def get_token_by_address(cls, token_address: str) -> str:
        try:
            return get_dict_key_by_value(cls.token_addresses(), token_address)
        except ValueError:
            return 'unknown'
