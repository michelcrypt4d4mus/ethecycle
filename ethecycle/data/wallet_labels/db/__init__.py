from typing import Optional

import sqllex as sx

from ethecycle.util.filesystem_helper import DB_DIR
from ethecycle.util.logging import console

WALLET_TABLE_NAME = 'wallets'
TOKENS_TABLE_NAME = 'tokens'
WALLET_DB_PATH = DB_DIR.joinpath('wallets.db')

_db: Optional[sx.SQLite3x] = None


def _create_tokens_table(db: sx.SQLite3x) -> None:
    console.print(f"Creating {TOKENS_TABLE_NAME} in {WALLET_DB_PATH}")

    db.create_table(
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


def _create_wallets_table(db: sx.SQLite3x) -> None:
    console.print(f"Creating {WALLET_TABLE_NAME} in {WALLET_DB_PATH}")

    db.create_table(
        WALLET_TABLE_NAME,
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
