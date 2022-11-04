"""
Abstract class to hold blockchain specific info (address lengths, token specifications, etc.).
Can be implemented for each chain with the appropriate overrides but a default
"""
from typing import Any, Dict, Optional

from inflection import underscore

from ethecycle.blockchains.token import Token
from ethecycle.config import Config
from ethecycle.chain_addresses.address_db import load_tokens, load_wallets
from ethecycle.util.logging import log
from ethecycle.util.string_constants import *
from ethecycle.wallet import Wallet


class ChainInfo:
    # Should be populated with the categories that have been pulled for this blockchain
    LABEL_CATEGORIES_SCRAPED_FROM_DUNE = []

    # Addresses on this chain should start with one of these strings
    ADDRESS_PREFIXES = []

    # Lazy load; should only be access through cls.tokens(), cls.wallet_label(), etc.
    _tokens_by_address: Dict[str, Token] = {}
    _tokens_by_symbol: Dict[str, Token] = {}
    _wallet_labels: Dict[str, Wallet] = {}

    @classmethod
    def scanner_url(cls, address: str) -> str:
        """Generate a URL for a chain browser, e.g. etherscan.io."""
        pass

    @classmethod
    def is_valid_address(cls, address: str) -> bool:
        """True if address starts with a prefix in ADDRESS_PREFIXES (or if ADDRESS_PREFIXES is empty)."""
        if len(cls.ADDRESS_PREFIXES) == 0:
            return True
        else:
            return any(address.startswith(prefix) for prefix in cls.ADDRESS_PREFIXES)

    @classmethod
    def token_address(cls, token_symbol: str) -> str:
        """Lookup a contract address by the symbol"""
        return cls.tokens()[token_symbol].address

    @classmethod
    def token_symbol(cls, token_address: str) -> Optional[str]:
        """Reverse lookup - takes an address, returns a symbol"""
        cls.tokens()  # Force load the tokens

        try:
            return cls._tokens_by_address[token_address].symbol
        except KeyError:
            return None

    @classmethod
    def token_decimals(cls, token_address: str) -> int:
        """Reverse lookup - takes an address, returns a symbol"""
        if token_address in cls.tokens():
            return cls.tokens()[token_address].decimals or 0
        else:
            return 0

    @classmethod
    def tokens(cls) -> Dict[str, Token]:
        """Lazy load token data."""
        if len(cls._tokens_by_symbol) == 0 and not Config.skip_load_from_db:
            tokens = load_tokens(cls)
            cls._tokens_by_symbol = {token.symbol: token for token in tokens}
            cls._tokens_by_address = {token.address: token for token in tokens}

        return cls._tokens_by_symbol

    @classmethod
    def wallet_label(cls, wallet_address: str) -> Optional[str]:
        """Lazy loaded wallet address labels."""
        if wallet_address in cls.known_wallets():
            return cls.known_wallets()[wallet_address].label
        else:
            return None

    @classmethod
    def wallet_category(cls, wallet_address: str) -> Optional[str]:
        """Lazy loaded wallet label categories."""
        if wallet_address in cls.known_wallets():
            return cls.known_wallets()[wallet_address].category
        else:
            return None

    @classmethod
    def known_wallets(cls) -> Dict[str, Wallet]:
        """Lazy loaded wallet label, categories, etc."""
        if len(cls._wallet_labels) == 0 and not Config.skip_load_from_db:
            cls._wallet_labels = {wallet.address: wallet for wallet in load_wallets(cls)}

        return cls._wallet_labels

    @classmethod
    def _chain_str(cls) -> str:
        """Returns lowercased version of class name (which should be the name of the blockchain)."""
        return underscore(cls.__name__)

    @classmethod
    def _chain_shortname(cls):
        if 'SHORT_NAME' in dir(cls):
            return cls.SHORT_NAME
        else:
            return cls._chain_str()
