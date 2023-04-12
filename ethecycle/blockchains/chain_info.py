"""
Abstract class to hold blockchain specific info (address lengths, token specifications, etc.).
Handles lookups of address properties for tokens and wallets on the chain.
"""
from typing import Dict, List

from inflection import underscore

from ethecycle.util.string_constants import *


class ChainInfo:
    # Addresses on this chain should start with one of these strings and have this length
    ADDRESS_PREFIXES: List[str] = []

    # No chain has an address standard shorter 6 chars. Subclasses can define ADDRESS_LENGTH to be more specific.
    MINIMUM_ADDRESS_LENGTH = 6
    ADDRESS_LENGTH: int

    # Default decimals for tokens on this chain
    DEFAULT_DECIMALS = 0

    # Should be populated with the categories that have been pulled for this blockchain
    LABEL_CATEGORIES_SCRAPED_FROM_DUNE: List[str] = []

    _wallet_names: Dict[str, 'Wallet'] = {}

    # Use flags to prevent repeatedly reloading data on chains where we have no info in the DB
    _loaded_tokens = False
    _loaded_wallets = False

    @classmethod
    def scanner_url(cls, address: str) -> str:
        """Generate a URL for a chain browser, e.g. etherscan.io."""
        pass

    @classmethod
    def is_valid_address(cls, address: str) -> bool:
        """True if address starts with a prefix in ADDRESS_PREFIXES (or if ADDRESS_PREFIXES is empty)."""
        if isinstance(address, float) or len(address) <= cls.MINIMUM_ADDRESS_LENGTH or ' ' in address:
            return False

        if len(cls.ADDRESS_PREFIXES) == 0:
            return True
        else:
            if not any(address.startswith(prefix) for prefix in cls.ADDRESS_PREFIXES):
                return False
            elif 'ADDRESS_LENGTH' not in dir(cls):
                return True

            return len(address) == cls.ADDRESS_LENGTH

    @classmethod
    def chain_string(cls) -> str:
        """Returns lowercased version of class name (which should be the name of the blockchain)."""
        return underscore(cls.__name__)

    @classmethod
    def _chain_shortname(cls):
        if 'SHORT_NAME' in dir(cls):
            return cls.SHORT_NAME
        else:
            return cls.chain_string()
