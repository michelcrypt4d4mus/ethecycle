from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Type, Union

from rich.pretty import pprint
from rich.text import Text

from ethecycle.util.string_constants import ADDRESS, MISSING_ADDRESS

FROM_ADDRESS = 'from_address'
TO_ADDRESS = 'to_address'

# Columns for Neo4j import
TXN_CSV_COLS = [
    'transaction_id',  # Combination of transaction_hash and log_index
    'blockchain',
    'token_address',
    'symbol',
    FROM_ADDRESS,
    TO_ADDRESS,
    'num_tokens:double',
    'block_number:int',
    'extracted_at:datetime',
]

NEO4J_RELATIONSHIP_COLS = {
    FROM_ADDRESS: ':START_ID',
    TO_ADDRESS: ':END_ID',
}

TXN_CSV_HEADER = [NEO4J_RELATIONSHIP_COLS.get(col, col) for col in TXN_CSV_COLS]
TXN_CSV_FIELDS = [col.split(':')[0] for col in TXN_CSV_COLS]


@dataclass
class Txn():
    token_address: str
    from_address: str
    to_address: str
    csv_value: str  # num_tokens
    transaction_hash: str
    log_index: str
    block_number: int
    chain_info: Type
    extracted_at: Optional[Union[datetime, str]] = None

    def __post_init__(self):
        # Some txns have multiple internal transfers so append log_index to achieve uniqueness
        self.blockchain = self.chain_info._chain_str()
        self.transaction_id = f"{self.transaction_hash}-{self.log_index}"
        self.symbol = self.chain_info.token_symbol(self.token_address)
        self.num_tokens = float(self.csv_value) / 10 ** self.chain_info.token_decimals(self.token_address)
        self.num_tokens_str = "{:,.18f}".format(self.num_tokens)
        self.block_number = int(self.block_number)
        self.scanner_url = self.chain_info.scanner_url(self.transaction_hash)

        if isinstance(self.extracted_at, datetime):
            self.extracted_at = self.extracted_at.replace(microsecond=0).isoformat()

    def to_neo4j_csv_row(self) -> List[Optional[str]]:
        """Generate Neo4J bulk load CSV row."""
        row = []

        for col in TXN_CSV_FIELDS:
            default_value = MISSING_ADDRESS if col.endswith(ADDRESS) else None
            row.append(getattr(self, col) or default_value)

        return row

    def __rich__(self) -> Text:
        txt = Text('<').append(self.transaction_hash[:8], style='magenta')
        txt.append(', To: ').append(self.to_address[:8], style='color(222)').append(', value: ')
        return txt.append(f"{self.num_tokens_str}", style='cyan').append('>')

    def __str__(self) -> str:
        return self.__rich__().plain

    def __eq__(self, other: 'Txn'):
        return self.transaction_id == other.transaction_id

    @classmethod
    def count_col_vals(cls, txns: List['Txn'], col: str) -> None:
        """Given a list of txns and a column name, count occurences of each value and show top 100"""
        counts = defaultdict(lambda: 0)

        for txn in txns:
            counts[getattr(txn, col)] += 1

        pprint(sorted(counts.items(), key=lambda r: r[1], reverse=True)[0:100])
