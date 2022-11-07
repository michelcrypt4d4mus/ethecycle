"""
Data class for tokens. Note that tokens are also wallets insofar as all tokens have an
on-chain address.
"""
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Union

from rich.text import Text

from ethecycle.models.address import Address
from ethecycle.util.logging import console, log
from ethecycle.util.string_constants import SYMBOL
from ethecycle.util.string_helper import strip_and_set_empty_string_to_none

DEFAULT_DECIMALS = 0


@dataclass(kw_only=True)
class Token(Address):
    symbol: str
    name: str
    decimals: int
    token_type: Optional[str] = None
    is_active: Optional[bool] = None
    is_scam: Optional[bool] = None
    url_explorer: Optional[str] = None
    launched_at: Optional[Union[datetime, str]] = None
    listed_on_coin_market_cap_at: Optional[Union[datetime, str]] = None
    extra_fields: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Minor data cleanup"""
        super().__post_init__()

        if self.token_type is not None:
            self.token_type = strip_and_set_empty_string_to_none(self.token_type)

        self.token_type = self.token_type.lower() if self.token_type else None

    @classmethod
    def from_properties(cls, properties: Dict[str, Any]) -> 'Token':
        """Alternate constructor that groups extra fields into 'extra_fields' dict."""
        constructor_fields = {k: properties.get(k) for k in cls.__dataclass_fields__.keys()}
        constructor_fields['extra_fields'] = {k: v for k, v in properties.items() if k not in constructor_fields}
        return cls(**constructor_fields)

    @classmethod
    def token_address(cls, blockchain: str, token_symbol: str) -> str:
        """Lookup a contract's chain address by the symbol."""
        cls.chain_addresses()  # Ensures data is loaded from DB
        chain_addresses = cls._by_blockchain_symbol[blockchain]

        if token_symbol not in chain_addresses:
            raise ValueError(f"No address found for '{token_symbol}' on '{blockchain}' chain!")

        return chain_addresses[token_symbol].address

    @classmethod
    def token_symbol(cls, blockchain: str, token_address: str) -> Optional[str]:
        """Reverse lookup - takes an address, returns a symbol"""
        return cls.get_address_property(blockchain, token_address, SYMBOL)

    @classmethod
    def token_decimals(cls, blockchain: str, token_address: str) -> int:
        """Returns number of decimals in token at this 'token_address'."""
        return cls.get_address_property(blockchain, token_address, 'decimals') or DEFAULT_DECIMALS

    @classmethod
    def _after_load_callback(cls) -> None:
        """Build the symbols to tokens dict (_by_blockchain_symbol) for each chain."""
        cls._by_blockchain_symbol = defaultdict(lambda: dict())

        for blockchain, token_addresses in cls._by_blockchain_address.items():
            chain_symbols = cls._by_blockchain_symbol[blockchain]

            for token in token_addresses.values():
                if token.symbol is None:
                    log.debug(f"Skipping token with no symbol ({token.address})")
                    continue

                chain_symbols[token.symbol] = token

    def __rich__(self):
        txt = Text('').append(self.symbol, 'bright_green').append(f" (").append(self.address, style='grey')
        txt.append(f") ").append(self.name, 'cyan').append(f" {self.blockchain}", 'bytes')
        return txt
