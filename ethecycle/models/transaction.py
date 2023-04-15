import csv
import gzip
import io
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Type, Union

from rich.pretty import pprint
from rich.text import Text

from ethecycle.blockchains.chain_info import ChainInfo
from ethecycle.config import Config
from ethecycle.models.token import Token
from ethecycle.util.string_constants import *
from ethecycle.util.filesystem_helper import GZIP_EXTENSION

# Expected column order for source CSVs.
RAW_TXN_DATA_CSV_COLS = [
    TOKEN_ADDRESS,
    FROM_ADDRESS,
    TO_ADDRESS,
    'value',  # num_tokens
    TRANSACTION_HASH,
    LOG_INDEX,
    BLOCK_NUMBER
]

# Columns for Neo4j import
NEO4J_TXN_CSV_COLS = [
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

NEO4J_TXN_CSV_HEADER = [NEO4J_RELATIONSHIP_COLS.get(col, col) for col in NEO4J_TXN_CSV_COLS]
NEO4J_TXN_CSV_COLUMN_NAMES = [col.split(':')[0] for col in NEO4J_TXN_CSV_COLS]


@dataclass
class Txn():
    token_address: str
    from_address: str
    to_address: str
    csv_value: str  # num_tokens
    transaction_hash: str
    block_number: int
    log_index: str
    chain_info: Type
    extracted_at: Optional[Union[datetime, str]] = None

    def __post_init__(self):
        """Some txns have multiple internal transfers so append log_index to achieve a unique ID."""
        self.blockchain = self.chain_info.chain_string()
        self.transaction_id = f"{self.transaction_hash}-{self.log_index}"
        self.symbol = Token.token_symbol(self.blockchain, self.token_address)
        self.num_tokens = float(self.csv_value)

        if not Config.skip_decimal_division:
            self.num_tokens /= 10 ** Token.token_decimals(self.blockchain, self.token_address)

        self.num_tokens_str = "{:,.18f}".format(self.num_tokens)
        self.block_number = int(self.block_number)
        self.scanner_url = self.chain_info.scanner_url(self.transaction_hash)

        if isinstance(self.extracted_at, datetime):
            self.extracted_at = self.extracted_at.replace(microsecond=0).isoformat()

    def to_neo4j_csv_row(self) -> List[Optional[str]]:
        """Generate Neo4J bulk load CSV row."""
        row = []

        for col in NEO4J_TXN_CSV_COLUMN_NAMES:
            default_value = MISSING_ADDRESS if col.endswith(ADDRESS) else None
            row.append(getattr(self, col) or default_value)

        return row

    @classmethod
    def extract_from_csv(
            cls,
            csv_path: str,
            chain_info: Type['ChainInfo'],
            extracted_at: str,
            token: Optional['str']
        ) -> List['Txn']:
        """Load txions from a headerless CSV to list of Txn objects."""
        if csv_path.endswith(GZIP_EXTENSION):
            with gzip.open(csv_path, 'rt') as zipfile:
                txns = [Txn(*(row + [chain_info])) for row in csv.reader(zipfile, delimiter='|')]
        else:
            with open(csv_path, newline='') as csvfile:
                txns = [Txn(*(row + [chain_info])) for row in csv.reader(csvfile, delimiter='|')]

        # Fill in extracted_at so all records in same job have same timestamp
        for txn in txns:
            txn.extracted_at = extracted_at

        # Optionally filter for a single token symbol
        if token:
            token_address = Token.token_address(chain_info.chain_string(), token)
            txns = [txn for txn in txns if txn.token_address == token_address]

        return txns

    @classmethod
    def count_col_vals(cls, txns: List['Txn'], col: str) -> None:
        """Given a list of txns and a column name, count occurences of each value and show top 100"""
        counts = defaultdict(lambda: 0)

        for txn in txns:
            counts[getattr(txn, col)] += 1

        pprint(sorted(counts.items(), key=lambda r: r[1], reverse=True)[0:100])

    def __rich__(self) -> Text:
        txt = Text('<').append(self.transaction_hash[:8], style='magenta')
        txt.append(', To: ').append(self.to_address[:8], style='color(222)').append(', value: ')
        return txt.append(f"{self.num_tokens_str}", style='cyan').append('>')

    def __str__(self) -> str:
        return self.__rich__().plain

    def __eq__(self, other: 'Txn'):
        return self.transaction_id == other.transaction_id
