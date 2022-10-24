from dataclasses import dataclass
from typing import Optional


@dataclass
class Token:
    blockchain: str
    token_type: Optional[str]
    token_address: str
    symbol: str
    name: str
    decimals: int
