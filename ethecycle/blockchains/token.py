from dataclasses import dataclass


@dataclass
class Token:
    blockchain: str
    token_type: str
    token_address: str
    symbol: str
    name: str
    decimals: int
