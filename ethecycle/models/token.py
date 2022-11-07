"""
Data class for tokens. Note that tokens are also wallets insofar as all tokens have an
on-chain address.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Union

from rich.text import Text


@dataclass
class Token:
    blockchain: Optional[str]  # Some CMC data has no blockchain info...
    address: Optional[str]  # Some CMC data has no addresses...
    symbol: str
    name: str
    decimals: int
    token_type: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    is_scam: Optional[bool] = None
    url_explorer: Optional[str] = None
    launched_at: Optional[Union[datetime, str]] = None
    listed_on_coin_market_cap_at: Optional[Union[datetime, str]] = None
    extra_fields: Optional[Dict[str, Any]] = None
    data_source: Optional[str] = None
    extracted_at: Optional[Union[datetime, str]] = None

    def __post_init__(self):
        """Look up label and category if they were not provided."""
        self.address = self.address.lower() if self.address else None
        self.blockchain = self.blockchain.lower() if self.blockchain else None
        self.token_type = self.token_type.lower() if self.token_type is not None else None

        if isinstance(self.extracted_at, datetime):
            self.extracted_at = self.extracted_at.replace(microsecond=0).isoformat()

    @classmethod
    def from_properties(cls, properties: Dict[str, Any]) -> 'Token':
        constructor_fields = {k: properties.get(k) for k in cls.__dataclass_fields__.keys()}
        constructor_fields['extra_fields'] = {k: v for k, v in properties.items() if k not in constructor_fields}

        # if Config.debug:
        #     console.print(Panel(f"Symbol: {properties[SYMBOL]} ({properties.get(ADDRESS)})", expand=False))
        #     pprint(constructor_fields)

        return cls(**constructor_fields)

    def __rich__(self):
        txt = Text('').append(self.symbol, 'bright_green').append(f" (").append(self.address, style='grey')
        txt.append(f") ").append(self.name, 'cyan').append(f" {self.blockchain}", 'bytes')
        return txt
