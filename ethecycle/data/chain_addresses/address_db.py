"""
Class to manage sqlite DB holding wallet tag info.
Context managers: https://rednafi.github.io/digressions/python/2020/03/26/python-contextmanager.html#nesting-contexts
"""
from contextlib import contextmanager
from sqlite3.dbapi2 import IntegrityError
from typing import Any, Dict, List

import sqllex as sx
from rich.pretty import pprint

# from ethecycle.blockchains.token import Token  # Circular import!
from ethecycle.data.chain_addresses import db
from ethecycle.util.logging import console, log, print_dim
from ethecycle.util.string_constants import ADDRESS, EXTRACTED_AT
from ethecycle.util.time_helper import current_timestamp_iso8601_str
from ethecycle.wallet import Wallet

DbRows = List[Dict[str, Any]]


@contextmanager
def table_connection(table_name):
    """Connect to db and yield table obj. Disconnects automatically when done to commit data."""
    db = get_db_connection()

    try:
        yield db[table_name]
    except Exception as e:
        console.print_exception()
        console.print(f"Exception while connected to '{table_name}'...")
    finally:
        log.info(f"Closing DB connection to {table_name}...")
        db.disconnect()


@contextmanager
def wallets_table():
    """Returns connection to wallets data table."""
    with table_connection(db.WALLETS_TABLE_NAME) as wallets_table:
        yield wallets_table


@contextmanager
def tokens_table():
    """Returns connection to tokens data table."""
    with table_connection(db.TOKENS_TABLE_NAME) as tokens_table:
        yield tokens_table


def insert_rows(table_name: str, rows: DbRows) -> None:
    """Insert 'rows' into table named 'table_name'."""
    print_dim(f"Writing {len(rows)} rows to table '{table_name}'...")
    extracted_at = current_timestamp_iso8601_str()

    for row in rows:
        row[EXTRACTED_AT] = row.get(EXTRACTED_AT) or extracted_at

    db_conn = get_db_connection()
    columns = db_conn.get_columns_names(table_name)
    row_tuples = [[row.get(c) for c in columns] for row in rows]

    try:
        db_conn.insertmany(table_name, row_tuples)
    except IntegrityError as e:
        _insert_one_at_a_time(table_name, rows)
    finally:
        db_conn.disconnect()

    print_dim(f"Finished writing {len(rows)} rows to '{table_name}'.")


def insert_wallets(wallets: List[Wallet]) -> None:
    insert_rows(db.WALLETS_TABLE_NAME, [wallet.to_address_db_row() for wallet in wallets])


def insert_tokens(tokens: List['Token']) -> None:
    insert_rows(db.TOKENS_TABLE_NAME, [token.__dict__ for token in tokens])


def delete_rows_from_source(table_name: str, _data_source: str) -> None:
    """Delete all rows where _data_source arg is the data_source col. (Allows updates by reloading entire source)"""
    with table_connection(table_name) as db_table:
        data_source_row_count = db_table.select(
            SELECT='COUNT(*)',
            WHERE=(db_table['data_source'] == _data_source)
        )[0][0]

        if data_source_row_count == 0:
            return

        console.print(f"Deleting {data_source_row_count} rows in '{table_name}' sourced from {_data_source}...")
        db_table.delete({'data_source': _data_source})
        console.print("Deleted!", style='bright_red')


def is_table_in_database(table_name: str) -> bool:
    """Returns true if a table named 'table_name' exists in the DB."""
    try:
        db._db.get_table(table_name)
        return True
    except KeyError:
        return False


def drop_and_recreate_tables() -> None:
    """Drop and recreate all tables and them (only recreates schema; does not re-import rows)"""
    _db = get_db_connection()

    for table_name in db.UNIQUE_INDEXES.keys():
        console.print(f"Dropping '{table_name}'...", style='bright_red')
        _db.drop(TABLE=table_name, IF_EXIST=True)

    db._create_tokens_table()
    db._create_wallets_table()


def get_db_connection() -> sx.SQLite3x:
    """Make sure db._db is built / connected and that the tables h`ave been created."""
    if db._db is None:
        db._db = sx.SQLite3x(path=db.CHAIN_ADDRESSES_DB_PATH)

    if not _is_connected_to_db_file():
        db._db.connect()

    # Create tables if they don't exist
    if not is_table_in_database(db.TOKENS_TABLE_NAME):
        db._create_tokens_table()
    if not is_table_in_database(db.WALLETS_TABLE_NAME):
        db._create_wallets_table()

    return db._db


def _insert_one_at_a_time(table_name: str, rows: DbRows) -> None:
    """Insert 'rows' into table named 'table_name' one at a time for use as a fallback."""
    console.print(f"Fallback write {len(rows)} rows to '{table_name}' one at a time...", style='bright_yellow')
    rows_written = 0
    failed_writes = 0

    with table_connection(table_name) as table:
        for row in rows:
            log.debug(f"Inserting {row}")

            try:
                table.insert(**row)  # TODO: should prolly use db.insertmany()
                rows_written += 1
            except IntegrityError as e:
                log.warning(f"Skipping {row[ADDRESS]}: {type(e).__name__} error on row {row}...")
                failed_writes += 1

    print_dim(f"Wrote {rows_written} '{table_name}' rows one at a time ({failed_writes} failures).")


# https://stackoverflow.com/questions/71655300/python-sqlite3-how-to-check-if-connection-is-an-in-memory-database
# TODO: doesn't need to take connection arg
def _is_connected_to_db_file() -> bool:
    """Abuse 'pragma database list' to check if connection status real or just in memory."""
    if not db._db.connection:
        return False

    log.debug("Checking DB connection status...")
    local_cursor = db._db.connection.cursor()
    local_cursor.execute('pragma database_list')
    connected_to_file = local_cursor.fetchall()[0][2]
    return connected_to_file is not None and len(connected_to_file) > 0
