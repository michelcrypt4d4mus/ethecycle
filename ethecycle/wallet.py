# Simple class to hold wallet info
# TODO: maybe compute the date or block_number of first txion? Maybe better done in-graph...
from dataclasses import dataclass
from typing import List, Optional

from rich.text import Text

from ethecycle.transaction import Txn
from ethecycle.util.string_constants import MISSING_ADDRESS


@dataclass
class Wallet:
    address: str
    blockchain: str
    chain_info: 'ChainInfo'
    label: Optional[str] = None
    category: Optional[str] = None

    def __post_init__(self):
        # Some txns have multiple internal transfers so append log_index to achieve uniqueness
        if self.label and self.category:
            return

        self.label = self.chain_info.wallet_label(self.address)
        self.category = self.chain_info.wallet_category(self.address)

    def to_neo4j_csv_row(self):
        """Generate Neo4J bulk load CSV row."""
        return [
            self.address,
            self.blockchain,
            self.label,
            self.category
        ]

    def __rich__(self):
        """rich text format string."""
        txt = Text('').append(self.address, 'bytes').append(': ', 'grey').append(self.label or 'UNKNOWN', 'color(229) bold')
        txt.append(' (', 'grey').append(self.category or 'UNKNOWN', 'blue').append(')', 'grey')
        return txt

    def __str__(self):
        return self.__rich__().plain

    @classmethod
    def extract_wallets_from_transactions(cls, txns: List[Txn], chain_info: 'ChainInfo') -> List['Wallet']:
        """Extract wallet address from from/to addresses and add labels. Assumes all txns have same chain."""
        wallet_addresses = set([txn.to_address for txn in txns]).union(set([txn.from_address for txn in txns]))
        wallet_addresses.remove('')
        wallet_addresses.add(MISSING_ADDRESS)
        return [Wallet(address, chain_info._chain_str(), chain_info) for address in wallet_addresses]
