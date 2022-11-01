from dataclasses import dataclass
from typing import Optional


@dataclass
class Token:
    blockchain: str
    token_type: Optional[str]
    address: str
    symbol: str
    name: str
    decimals: int

    def __post_init__(self):
        """Look up label and category if they were not provided."""
        self.address = self.address.lower()
        self.blockchain = self.blockchain.lower()
        self.token_type = self.token_type.lower() if self.token_type is not None else None
