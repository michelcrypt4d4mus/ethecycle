"""
Class to manage sqlite DB holding wallet tag info.
Context managers: https://rednafi.github.io/digressions/python/2020/03/26/python-contextmanager.html#nesting-contexts
"""
from contextlib import contextmanager
from sqlite3.dbapi2 import IntegrityError
from typing import Any, Dict, List

import sqllex as sx
from rich.pretty import pprint

from ethecycle.blockchains.token import Token
from ethecycle.data.wallet_labels import db
from ethecycle.util.logging import console, log
from ethecycle.util.string_constants import EXTRACTED_AT
from ethecycle.util.time_helper import current_timestamp_iso8601_str
from ethecycle.wallet import Wallet


@contextmanager
def table_connection(table_name):
    """Connect to db and yield table obj. Disconnects automatically when done to commit data."""
    db = get_db_connection()

    try:
        yield db[table_name]
    except Exception as e:
        console.print_exception()
        console.print(f"Closing connection to SQLite table '{table_name}")
    finally:
        log.info(f"Closing DB connection to {table_name}")
        db.disconnect()


@contextmanager
def wallets_table():
    """Returns connection to wallets data table."""
    with table_connection(db.WALLET_TABLE_NAME) as wallets_table:
        yield wallets_table


@contextmanager
def tokens_table():
    """Returns connection to tokens data table."""
    with table_connection(db.TOKENS_TABLE_NAME) as tokens_table:
        yield tokens_table


def insert_rows(table_name: str, rows: List[Dict[str, Any]]) -> None:
    extracted_at = current_timestamp_iso8601_str()
    rows_written = 0
    failed_writes = 0

    with table_connection(table_name) as table:
        for row in rows:
            row[EXTRACTED_AT] = row.get(EXTRACTED_AT) or extracted_at

            try:
                table.insert(**row)  # TODO: should prolly use db.insertmany()
                rows_written += 1
            except IntegrityError as e:
                failed_writes += 1
                console.print_exception()
                msg = f"Integrity violation inserting row {row}... logging and continuing"
                console.print(msg)
                log.warning(msg)

    console.print(f"Finished writing {rows_written} '{table_name}' rows ({failed_writes} failures).")


def insert_wallets(wallets: List[Wallet]) -> None:
    insert_rows(db.WALLET_TABLE_NAME, [wallet.to_address_db_row() for wallet in wallets])


def insert_tokens(tokens: List[Token]) -> None:
    insert_rows(db.TOKENS_TABLE_NAME, [token.to_address_db_row() for token in tokens])


def delete_rows_for_data_source(table_name: str, _data_source: str) -> None:
    """Delete all rows where _data_source arg is the data_source col. (Allows updates by reloading entire source)"""
    with table_connection(table_name) as db_table:
        data_source_row_count = db_table.select(
            SELECT='COUNT(*)',
            WHERE=(db_table['data_source'] == _data_source)
        )

        console.print(f"About to delete {data_source_row_count[0][0]} rows from {table_name}")
        db_table.delete({'data_source': _data_source})
        console.print("Deleted!", style='bright_red')


def get_db_connection() -> sx.SQLite3x:
    """Make sure db._db is built / connected and that the tables h`ave been created."""
    if db._db is None:
        db._db = sx.SQLite3x(path=db.WALLET_DB_PATH)

    if not _is_connected_to_db_file():
        db._db.connect()

    db._create_tokens_table(db._db)
    db._create_wallets_table(db._db)
    return db._db


# https://stackoverflow.com/questions/71655300/python-sqlite3-how-to-check-if-connection-is-an-in-memory-database
# TODO: doesn't need to take connection arg
def _is_connected_to_db_file() -> bool:
    """Abuse 'pragma database list' to check if connection status real or just in memory."""
    if not db._db.connection:
        return False

    console.print("Checking DB connection: ", 'yellow')
    local_cursor = db._db.connection.cursor()
    local_cursor.execute('pragma database_list')
    connected_to_file = local_cursor.fetchall()[0][2]
    return connected_to_file is not None and len(connected_to_file) > 0
