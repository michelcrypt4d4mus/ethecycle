"""
Simple class to hold wallet info.
TODO: maybe compute the date or block_number of first txion? Maybe better done in-graph...
"""
from dataclasses import dataclass
from datetime import datetime
from random import randint
from typing import Any, Dict, List, Optional, Type, Union

from rich.text import Text

from ethecycle.models.token import Token
from ethecycle.models.transaction import Txn
from ethecycle.util.string_constants import *

WALLET_CSV_HEADER = [
    'address:ID',
    'blockchain',
    'label',
    'category',
    'extracted_at:datetime',
]

WALLET_CSV_COLUMNS = [col.split(':')[0] for col in WALLET_CSV_HEADER]

# For pretty printing
WALLET_LABEL_COLORS = {
    'balancer': 49,
    'bridge': 55,
    'cex': 78,
    CONTRACT: 45,
    'contract-deployer': 47,
    DEFI: 167,
    DEX: 169,
    'funds': 33,
    'game': 13,
    'hackers': 124,
    'individual': 157,
    'market maker': 76,
    'mev': 59,
    'multisig': 34,
    'mining': 94,
    STABLECOIN: 7,
    'sybil-delegate': 29,
    TOKEN: 96,
    'token-sale': 95,
}

UNKNOWN = Text('UNKNOWN', style='color(234)')


@dataclass
class Wallet:
    address: str
    chain_info: Type
    label: Optional[str] = None
    category: Optional[str] = None
    data_source: Optional[str] = None
    extracted_at: Optional[Union[datetime, str]] = None

    def __post_init__(self):
        """Look up label and category if they were not provided."""
        self.address = self.address.lower()
        self.blockchain = self.chain_info._chain_str()
        self.category = self.category.lower() if self.category else None

        if isinstance(self.extracted_at, datetime):
            self.extracted_at = self.extracted_at.replace(microsecond=0).isoformat()

    @classmethod
    def from_token(cls, token: Token, chain_info: Type) -> 'Wallet':
        """Alternate constructor to build a Wallet() object representation of a token."""
        return cls(
            address=token.address,
            chain_info=chain_info,
            label=f"{token.symbol} Token",
            category=TOKEN,
            data_source=token.data_source,
            extracted_at=token.extracted_at
        )

    def load_labels(self) -> 'Wallet':
        """Loads label and category fields from chain_addresses.db. Returns self."""
        self.label = self.label or self.chain_info.wallet_label(self.address)
        self.category = self.category or self.chain_info.wallet_category(self.address)
        return self

    def to_neo4j_csv_row(self) -> List[Optional[str]]:
        """Generate Neo4J bulk load CSV row."""
        return [getattr(self, col) for col in WALLET_CSV_COLUMNS]

    def to_address_db_row(self) -> Dict[str, Any]:
        """Generate a dict we can insert as a row into the chain addresses DB."""
        return {k: v for k, v in self.__dict__.items() if k != 'chain_info'}

    def __rich__(self):
        """rich text format string."""
        txt = Text('').append(self.address, 'bytes').append(': ', 'grey')

        if self.label:
            txt.append(self.label, 'color(229) bold')
        else:
            txt.append_text(UNKNOWN)

        txt.append(' (', 'grey')

        if self.category:
            txt.append(self.category, style=self._category_style())
        else:
            txt.append_text(UNKNOWN)

        return txt.append(')', 'grey')

    def _category_style(self) -> str:
        """Get a color for the wallet category."""
        if self.category not in WALLET_LABEL_COLORS:
            WALLET_LABEL_COLORS[str(self.category)] = randint(38, 229)

        return f"color({WALLET_LABEL_COLORS[str(self.category)]})"

    def __str__(self):
        return self.__rich__().plain

    @classmethod
    def extract_wallets_from_transactions(cls, txns: List[Txn], chain_info: Type) -> List['Wallet']:
        """Extract wallet addresses from from and to addresses and add labels."""
        wallet_addresses = set([t.to_address for t in txns]).union(set([t.from_address for t in txns]))
        wallet_addresses.remove('')
        wallet_addresses.add(MISSING_ADDRESS)

        return [
            Wallet(address, chain_info, extracted_at=txns[0].extracted_at).load_labels()
            for address in wallet_addresses
        ]
