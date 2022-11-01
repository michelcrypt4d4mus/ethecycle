"""
Class to manage sqlite DB holding wallet tag info.
Context managers: https://rednafi.github.io/digressions/python/2020/03/26/python-contextmanager.html#nesting-contexts
"""
import sqlite3
from contextlib import contextmanager
from typing import Generator

import sqllex as sx

from ethecycle.blockchains import wallet_database
from ethecycle.util.logging import console, log


@contextmanager
def wallets_table():
    """Returns connection to wallets data table."""
    with table_connection('tokens') as tokens_table:
        yield table_connection(wallet_database.WALLET_TABLE_NAME)


@contextmanager
def tokens_table():
    """Returns connection to tokens data table."""
    with table_connection('tokens') as tokens_table:
        yield table_connection(wallet_database.TOKENS_TABLE_NAME)


@contextmanager
def table_connection(table_name):
    """Create if it doesn't exist and disconnect automatically when done to commit data."""
    db = get_db_connection()

    try:
        yield db[table_name]
    except Exception as e:
        console.print_exception()
        console.print(f"Closing connection to SQLite table '{table_name}")
    finally:
        log.info("Closing DB connection")
        db.disconnect()


def delete_rows_for_data_source(table_name: str, _data_source: str) -> None:
    """Delete all rows where _data_source arg is the data_source col. (Allows updates by reloading entire source)"""
    with table_connection(table_name) as db_table:
        data_source_row_count = db_table.select(
            SELECT='COUNT(*)',
            WHERE=(db_table['data_source'] == _data_source)
        )
        # import pdb;pdb.set_trace()
        console.print(f"About to delete {data_source_row_count} rows from {table_name}")
        db_table.delete({'data_source': _data_source})
        console.print("Deleted!", style='bright_red')


def get_db_connection() -> sx.SQLite3x:
    """Make sure wallet_database._db is built / connected and that the tables h`ave been created."""
    if wallet_database._db is None:
        wallet_database._db = sx.SQLite3x(path=wallet_database.WALLET_DB_PATH)

    if not _is_connected_to_db_file():
        wallet_database._db.connect()

    wallet_database._create_tokens_table(wallet_database._db)
    wallet_database._create_wallets_table(wallet_database._db)
    return wallet_database._db


# https://stackoverflow.com/questions/71655300/python-sqlite3-how-to-check-if-connection-is-an-in-memory-database
# TODO: doesn't need to take connection arg
def _is_connected_to_db_file() -> bool:
    """Abuse 'pragma database list' to check if connection status real or just in memory."""
    conn = wallet_database._db.connection

    if conn is None:
        return False

    console.print("Checking DB connection: ", 'yellow')
    local_cursor = conn.cursor()
    local_cursor.execute('pragma database_list')
    connected_to_file = local_cursor.fetchall()[0][2]
    return connected_to_file is not None and len(connected_to_file) > 0
