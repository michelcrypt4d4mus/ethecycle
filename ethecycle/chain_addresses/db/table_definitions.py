"""
Contains address_db table definitions.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Union

import sqllex as sx
from inflection import pluralize

from ethecycle.chain_addresses.db import CHAIN_ADDRESSES_DB_PATH
from ethecycle.util.logging import console
from ethecycle.util.string_constants import *

DATA_SOURCES_TABLE_NAME = pluralize(DATA_SOURCE)
WALLETS_TABLE_NAME = pluralize(WALLET)
TOKENS_TABLE_NAME = pluralize(TOKEN)

DATA_SOURCE_ID = f"{DATA_SOURCE}_id"
ADDRESS_UNIQUE_INDEX = [DATA_SOURCE_ID, BLOCKCHAIN, ADDRESS]


@dataclass
class TableDefinition:
    table_name: str
    columns: Dict[str, Union[str, List[str]]]
    indexes: List[List[str]] = field(default_factory=list)
    unique_indexes: List[List[str]] = field(default_factory=list)

    def create_table(self, db_conn: sx.SQLite3x) -> None:
        console.print(f"Creating table '{self.table_name}' in '{CHAIN_ADDRESSES_DB_PATH}'...", style='cyan')
        db_conn.create_table(self.table_name, self.columns, IF_NOT_EXIST=True)

        for index in self.indexes:
            self._create_index(db_conn, index)

        for index in self.unique_indexes:
            self._create_index(db_conn, index, True)

    def drop_table(self, db_conn: sx.SQLite3x) -> None:
        console.print(f"Dropping '{self.table_name}'...", style='bright_red')
        db_conn.drop(TABLE=self.table_name, IF_EXIST=True)

    def _create_index(self, db_conn: sx.SQLite3x, columns: List[str], is_unique: bool = False) -> None:
        """Add (optionally unique) index on columns to table_name."""
        idx_name = '_'.join(['idx', self.table_name] + columns)
        sql = f"CREATE {'UNIQUE' if is_unique else ''} INDEX {idx_name} ON {self.table_name}({','.join(columns)})"
        console.print(f"  Index SQL: {sql}", style='dim')
        db_conn.execute(script=sql)


TABLE_DEFINITIONS = [
    TableDefinition(
        DATA_SOURCES_TABLE_NAME,
        {
            'id': [sx.INTEGER, sx.PRIMARY_KEY],
            DATA_SOURCE: [sx.TEXT, sx.NOT_NULL, sx.UNIQUE],
            'created_at': [sx.DATE, sx.NOT_NULL]
        }
    ),
    TableDefinition(
        WALLETS_TABLE_NAME,
        {
            ADDRESS: [sx.TEXT, sx.NOT_NULL],
            BLOCKCHAIN: sx.TEXT,
            'name': sx.TEXT,
            'category': sx.TEXT,
            DATA_SOURCE_ID: [sx.INTEGER, sx.NOT_NULL],
            EXTRACTED_AT: [sx.DATE, sx.NOT_NULL]
        },
        unique_indexes=[ADDRESS_UNIQUE_INDEX]
    ),
    TableDefinition(
        TOKENS_TABLE_NAME,
        {
            ADDRESS: sx.TEXT,
            BLOCKCHAIN: sx.TEXT,
            'name': sx.TEXT,
            'category': sx.TEXT,
            SYMBOL: [sx.TEXT, sx.NOT_NULL],
            'token_type': sx.TEXT,
            'decimals': sx.INTEGER,
            'is_active': sx.BOOL,
            'is_scam': sx.BOOL,
            'launched_at': sx.DATE,
            'url_explorer': sx.TEXT,
            'listed_on_coin_market_cap_at': sx.DATE,
            'extra_fields': sx.BLOB,  # JSON blob with any other params worth saving
            DATA_SOURCE_ID: [sx.INTEGER, sx.NOT_NULL],
            'extracted_at': [sx.DATE, sx.NOT_NULL]
        },
        unique_indexes=[ADDRESS_UNIQUE_INDEX]
    )
]
