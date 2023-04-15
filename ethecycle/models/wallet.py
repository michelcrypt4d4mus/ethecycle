"""
Simple class to hold wallet info.
TODO: maybe compute the date or block_number of first txion? Maybe better done in-graph...
"""
from dataclasses import dataclass
from functools import partial
from random import randint
from typing import Any, Dict, List, Optional, Type, Union

from rich.text import Text

#from ethecycle.blockchains.chain_info import ChainInfo # Circular import :(
from ethecycle.models.address import Address
from ethecycle.models.token import Token
#from ethecycle.models.transaction import Txn
from ethecycle.util.string_constants import *

NEO4J_WALLET_CSV_HEADER = [
    'address:ID',
    'blockchain',
    'name',
    'category',
    'extracted_at:datetime',
]

WALLET_CSV_COLUMNS = [col.split(':')[0] for col in NEO4J_WALLET_CSV_HEADER]

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


@dataclass(kw_only=True)
class Wallet(Address):
    def __post_init__(self):
        """Validate address"""
        super().__post_init__()

        if self.address is None:
            raise ValueError(f"Address is required for wallets: {self}")

    @classmethod
    def from_token(cls, token: 'Token') -> 'Wallet':
        """Alternate constructor to build a Wallet object out of a Token object."""
        return cls(
            address=token.address,
            chain_info=token.chain_info,
            name=f"{token.symbol} Token",
            category=TOKEN,
            data_source=token.data_source,
            extracted_at=token.extracted_at
        )

    @classmethod
    def extract_wallets_from_transactions(cls, txns: List['Txn']) -> List['Wallet']:
        """
        Construct Wallet objects out of the to/from addresses in a list of Txns and add labels.
        Assumes all txns are from same blockchain.
        """
        addresses = set([t.to_address for t in txns]).union(set([t.from_address for t in txns]))

        try:
            addresses.remove('')
        except KeyError:
            pass

        addresses.add(MISSING_ADDRESS)
        TokenWallet = partial(cls, blockchain=txns[0].blockchain, extracted_at=txns[0].extracted_at)
        return [TokenWallet(address=a).load_name_and_category() for a in addresses]

    @classmethod
    def _after_load_callback(cls) -> None:
        """Add the token addresses because tokens are wallets too."""
        for token in Token.all():
            cls._by_blockchain_address[token.blockchain][token.address] = cls.from_token(token)

    def load_name_and_category(self) -> 'Wallet':
        """Loads label and category fields from chain_addresses.db. Returns self."""
        if not self.blockchain or not self.address:
            return self

        self.name = self.name or type(self).name_at_address(self.blockchain, self.address)
        self.category = self.category or type(self).category_at_address(self.blockchain, self.address)
        return self

    def to_neo4j_csv_row(self) -> List[Optional[str]]:
        """Generate Neo4J bulk load CSV row."""
        return [getattr(self, col) for col in WALLET_CSV_COLUMNS]

    def _category_style(self) -> str:
        """Get a color for the wallet category."""
        if self.category not in WALLET_LABEL_COLORS:
            WALLET_LABEL_COLORS[str(self.category)] = randint(38, 229)

        return f"color({WALLET_LABEL_COLORS[str(self.category)]})"

    def __str__(self):
        return self.__rich__().plain

    def __rich__(self):
        """rich text format string."""
        txt = Text('', style='white').append(self.address, 'magenta dim').append(': ', 'grey')

        if self.name:
            txt.append(self.name, 'color(229) bold')
        else:
            txt.append_text(UNKNOWN)

        txt.append(' (', 'grey')

        if self.category:
            txt.append(self.category, style=self._category_style())
        else:
            txt.append_text(UNKNOWN)

        if self.organization:
            txt.append(' [').append(self.organization, style='color(123)').append(']')

        return txt.append(')', 'grey')
