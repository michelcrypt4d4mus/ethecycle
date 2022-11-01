from typing import List, Optional

import sqllex as sx

from ethecycle.util.filesystem_helper import DB_DIR
from ethecycle.util.logging import console
from ethecycle.util.string_constants import *

CHAIN_ADDRESSES_DB_FILE_NAME = 'chain_addresses.db'
CHAIN_ADDRESSES_DB_PATH = str(DB_DIR.joinpath(CHAIN_ADDRESSES_DB_FILE_NAME))

WALLETS_TABLE_NAME = 'wallets'
TOKENS_TABLE_NAME = 'tokens'

UNIQUE_INDEXES = {
    WALLETS_TABLE_NAME: [
        [DATA_SOURCE, BLOCKCHAIN, ADDRESS]
    ],
    TOKENS_TABLE_NAME: [
        [DATA_SOURCE, BLOCKCHAIN, ADDRESS]
    ]
}

# Not for direct use. Access the DB through methods in wallet_db.py
_db: Optional[sx.SQLite3x] = None


def _create_tokens_table() -> None:
    console.print(f"Creating table '{TOKENS_TABLE_NAME}' in {CHAIN_ADDRESSES_DB_PATH}")

    _db.create_table(
        TOKENS_TABLE_NAME,
        {
            'symbol': [sx.TEXT, sx.NOT_NULL],
            'name': sx.TEXT,
            'category': sx.TEXT,
            'blockchain': sx.TEXT,
            'token_type': sx.TEXT,
            'address': sx.TEXT,
            'is_active': sx.BOOL,
            'is_hidden': sx.BOOL,
            'is_audited': sx.BOOL,
            'had_an_ico': sx.BOOL,
            'launched_at': sx.TEXT,
            'url_discord': sx.TEXT,
            'url_telegram': sx.TEXT,
            'url_chat': sx.TEXT,
            'url_announcement': sx.TEXT,
            'url_explorer': sx.TEXT,
            'url_message_board': sx.TEXT,
            'url_reddit': sx.TEXT,
            'url_source_code': sx.TEXT,
            'url_technical_doc': sx.TEXT,
            'url_twitter': sx.TEXT,
            'url_website': sx.TEXT,
            'extra_fields': sx.BLOB,  # JSON string
            'listed_on_coin_market_cap_at': sx.DATE,
            'coin_market_cap_id': sx.NUMERIC,
            'coin_market_cap_watchers': sx.TEXT,
            'data_source': [sx.TEXT, sx.NOT_NULL],
            'extracted_at': sx.TEXT
        },
        IF_NOT_EXIST=True
    )

    for index_cols in UNIQUE_INDEXES[TOKENS_TABLE_NAME]:
        _create_index(TOKENS_TABLE_NAME, index_cols, is_unique=True)


def _create_wallets_table() -> None:
    console.print(f"Creating table '{WALLETS_TABLE_NAME}' {CHAIN_ADDRESSES_DB_PATH}")

    _db.create_table(
        WALLETS_TABLE_NAME,
        {
            'address': sx.TEXT,
            'blockchain': sx.TEXT,
            'label': sx.TEXT,
            'category': sx.TEXT,
            'data_source': sx.TEXT,
            'extracted_at': sx.TEXT
        },
        IF_NOT_EXIST=True
    )

    for index_cols in UNIQUE_INDEXES[WALLETS_TABLE_NAME]:
        _create_index(WALLETS_TABLE_NAME, index_cols, is_unique=True)


def _create_index(table_name: str, columns: List[str], is_unique: bool = False) -> None:
    """Add (optionally unique) index on columns to table_name."""
    idx_name = '_'.join(['idx', table_name] + columns)
    sql = f"CREATE {'UNIQUE' if is_unique else ''} INDEX {idx_name} ON {table_name}({','.join(columns)})"
    console.print(f"  Index SQL: {sql}", style='dim')
    _db.execute(script=sql)
