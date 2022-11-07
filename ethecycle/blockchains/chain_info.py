"""
Abstract class to hold blockchain specific info (address lengths, token specifications, etc.).
Handles lookups of address properties for tokens and wallets on the chain.
"""
from typing import Any, Dict, List, Optional

from inflection import underscore

from ethecycle.models.token import Token
from ethecycle.config import Config
from ethecycle.chain_addresses.address_db import load_tokens, load_wallets
from ethecycle.util.logging import log
from ethecycle.util.string_constants import *
from ethecycle.models.wallet import Wallet


class ChainInfo:
    # Addresses on this chain should start with one of these strings and have this length
    ADDRESS_PREFIXES: List[str] = []
    ADDRESS_LENGTH: int
    # No chain should have an address standard shorter than this
    MINIMUM_ADDRESS_LENGTH = 6

    # Default decimals for tokens on this chain
    DEFAULT_DECIMALS = 0

    # Should be populated with the categories that have been pulled for this blockchain
    LABEL_CATEGORIES_SCRAPED_FROM_DUNE: List[str] = []

    # Lazy load; should only be access through cls.token_addresses(), cls.wallet_label(), etc.
    _tokens_by_address: Dict[str, Token] = {}
    _tokens_by_symbol: Dict[str, Token] = {}
    _wallet_labels: Dict[str, Wallet] = {}

    # Use flags to prevent repeatedly reloading data on chains where we have no info in the DB
    _loaded_tokens = False
    _loaded_wallets = False

    @classmethod
    def token_address(cls, token_symbol: str) -> str:
        """Lookup a contract's chain address by the symbol."""
        if token_symbol not in cls.token_symbols():
            raise ValueError(f"No '{cls.chain_string()}' address found for {token_symbol}!")

        return cls.token_symbols()[token_symbol].address

    @classmethod
    def token_symbol(cls, token_address: str) -> Optional[str]:
        """Reverse lookup - takes an address, returns a symbol"""
        token = cls._get_token_by_address(token_address)
        return token.symbol if token else None

    @classmethod
    def token_decimals(cls, token_address: str) -> int:
        """Reverse lookup - takes an address, returns a symbol"""
        token = cls._get_token_by_address(token_address)
        return cls.DEFAULT_DECIMALS if token is None else (token.decimals or cls.DEFAULT_DECIMALS)

    @classmethod
    def token_addresses(cls) -> Dict[str, Token]:
        """Returns dict mapping token address to Token obj for this chain."""
        if len(cls._tokens_by_address) == 0 and not Config.skip_load_from_db and not cls._loaded_tokens:
            tokens = load_tokens(cls)
            cls._tokens_by_symbol = {token.symbol: token for token in tokens}
            cls._tokens_by_address = {token.address: token for token in tokens}
            cls._loaded_tokens = True

        return cls._tokens_by_address

    @classmethod
    def token_symbols(cls) -> Dict[str, Token]:
        """Returns dict mapping token symbol to Token obj for this chain."""
        cls.token_addresses()  # Ensures data is loaded from DB
        return cls._tokens_by_symbol

    @classmethod
    def wallet_label(cls, wallet_address: str) -> Optional[str]:
        """Lazy loaded wallet address labels."""
        wallet = cls._get_wallet_by_address(wallet_address)
        return None if wallet is None else wallet.label

    @classmethod
    def wallet_category(cls, wallet_address: str) -> Optional[str]:
        """Get category for a wallet address if there is one in DB."""
        wallet = cls._get_wallet_by_address(wallet_address)
        return None if wallet is None else wallet.category

    @classmethod
    def known_wallets(cls) -> Dict[str, Wallet]:
        """Lazy loaded wallet label, categories, etc."""
        if len(cls._wallet_labels) == 0 and not Config.skip_load_from_db and not cls._loaded_wallets:
            cls._wallet_labels = {wallet.address: wallet for wallet in load_wallets(cls)}
            cls._loaded_wallets = True

        return cls._wallet_labels

    @classmethod
    def scanner_url(cls, address: str) -> str:
        """Generate a URL for a chain browser, e.g. etherscan.io."""
        pass

    @classmethod
    def is_valid_address(cls, address: str) -> bool:
        """True if address starts with a prefix in ADDRESS_PREFIXES (or if ADDRESS_PREFIXES is empty)."""
        if isinstance(address, float) or len(address) <= cls.MINIMUM_ADDRESS_LENGTH:
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
    def _get_token_by_address(cls, token_address: str):
        return cls.token_addresses().get(token_address)

    @classmethod
    def _get_wallet_by_address(cls, wallet_address: str):
        return cls.known_wallets().get(wallet_address)

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
