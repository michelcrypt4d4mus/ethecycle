"""
Class to manage sqlite DB holding wallet tag info.
"""
from contextlib import contextmanager
from typing import Generator

import sqllex as sx

from ethecycle.blockchains import wallet_database
from ethecycle.util.logging import console, log


@contextmanager
def wallets_table() -> Generator[sx.AbstractTable, None, None]:
    """Create if it doesn't exist and disconnect automatically when done to commit data."""
    ensure_db_connection()

    try:
        yield wallet_database._db[wallet_database.WALLET_TABLE_NAME]
    except Exception as e:
        console.print_exception()
        console.print(f"Closing connection to SQLite '{wallet_database.WALLET_TABLE_NAME}")
    finally:
        log.info("Closing DB connection")
        wallet_database._db.disconnect()


@contextmanager
def tokens_table() -> Generator[sx.AbstractTable, None, None]:
    """Create if it doesn't exist and disconnect automatically when done to commit data."""
    ensure_db_connection()

    try:
        yield wallet_database._db[wallet_database.TOKENS_TABLE_NAME]
    except Exception as e:
        console.print_exception()
        console.print(f"Closing connection to SQLite '{wallet_database.WALLET_TABLE_NAME}")
    finally:
        if wallet_database._db is None:
            console.print(f"SQLite DB already closed.")
        else:
            log.info("Closing DB connection")
            wallet_database._db.disconnect()


def ensure_db_connection() -> None:
    wallet_database._db = sx.SQLite3x(path=wallet_database.WALLET_DB_PATH)
    wallet_database._db.connect()
    wallet_database._create_tokens_table(wallet_database._db)
    #wallet_database._create_wallets_table(_db)
