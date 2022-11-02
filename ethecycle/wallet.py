"""
Simple class to hold wallet info.
TODO: maybe compute the date or block_number of first txion? Maybe better done in-graph...
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type

from rich.text import Text

from ethecycle.transaction import Txn
from ethecycle.util.string_constants import MISSING_ADDRESS

WALLET_LABEL_COLORS = {
    'bridge': 55,
    'cex': 78,
    'funds': 33,
    'hackers': 124,
    'mev': 59,
    'multisig': 34,
}

UNKNOWN = Text('UNKNOWN', style='grey dim')


@dataclass
class Wallet:
    address: str
    chain_info: Type
    label: Optional[str] = None
    category: Optional[str] = None
    data_source: Optional[str] = None

    def __post_init__(self):
        """Look up label and category if they were not provided."""
        self.address = self.address.lower()
        self.blockchain = self.chain_info._chain_str()

    def load_labels(self) -> 'Wallet':
        """Loads label and category fields from chain_addresses.db. Returns self."""
        self.label = self.label or self.chain_info.wallet_label(self.address)
        self.category = self.category or self.chain_info.wallet_category(self.address)
        return self

    def to_neo4j_csv_row(self) -> List[Optional[str]]:
        """Generate Neo4J bulk load CSV row."""
        return [
            self.address,
            self.blockchain,
            self.label,
            self.category
        ]

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
            txt.append(self.category, style=f"color({WALLET_LABEL_COLORS.get(self.category, 226)})")
        else:
            txt.append_text(UNKNOWN)

        return txt.append(')', 'grey')

    def __str__(self):
        return self.__rich__().plain

    @classmethod
    def extract_wallets_from_transactions(cls, txns: List[Txn], chain_info: Type) -> List['Wallet']:
        """Extract wallet addresses from from and to addresses and add labels."""
        wallet_addresses = set([t.to_address for t in txns]).union(set([t.from_address for t in txns]))
        wallet_addresses.remove('')
        wallet_addresses.add(MISSING_ADDRESS)
        return [Wallet(address, chain_info).load_labels() for address in wallet_addresses]
