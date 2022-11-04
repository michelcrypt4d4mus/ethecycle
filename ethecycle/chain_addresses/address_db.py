"""
Class to manage sqlite DB holding wallet tag info. Most methods here assume you are bulk
updating all data in a given table from a given data_source.
Context managers: https://rednafi.github.io/digressions/python/2020/03/26/python-contextmanager.html#nesting-contexts
"""
import json
from contextlib import contextmanager
from sqlite3.dbapi2 import IntegrityError
from typing import Any, Dict, List, Optional, Union

import sqllex as sx
from rich.panel import Panel
from rich.pretty import pprint

from ethecycle.models.token import Token
from ethecycle.chain_addresses import db
from ethecycle.chain_addresses.db.table_definitions import (DATA_SOURCE_ID,
     DATA_SOURCES_TABLE_NAME, TOKENS_TABLE_NAME, WALLETS_TABLE_NAME, TABLE_DEFINITIONS)
from ethecycle.config import Config
from ethecycle.util.logging import console, log, print_dim
from ethecycle.util.string_constants import *
from ethecycle.util.time_helper import current_timestamp_iso8601_str
from ethecycle.models.wallet import Wallet

DbRows = List[Dict[str, Any]]

# TODO: Deal with this a better way
COLUMNS_TO_NOT_LOAD = ['chain_info', 'data_source']


@contextmanager
def table_connection(table_name):
    """Connect to db and yield table obj. Disconnects automatically when done to commit data."""
    db = get_db_connection()

    try:
        yield db[table_name]
    except Exception as e:
        console.print_exception()
        console.print(f"Exception while connected to '{table_name}'...")
        raise e
    finally:
        log.debug(f"Closing DB connection to {table_name}...")

        # Hold connection open for big inserts bc writing is slow.
        if not Config.skip_load_from_db:
            db.disconnect()


@contextmanager
def wallets_table():
    """Returns connection to wallets data table."""
    with table_connection(WALLETS_TABLE_NAME) as wallets_table:
        yield wallets_table


@contextmanager
def tokens_table():
    """Returns connection to tokens data table."""
    with table_connection(TOKENS_TABLE_NAME) as tokens_table:
        yield tokens_table


def load_wallets(chain_info: 'ChainInfo') -> List[Wallet]:
    """Load wallets (and tokens - tokens have wallet addresses) from the database."""
    token_wallets = [Wallet.from_token(token, chain_info) for token in load_tokens(chain_info)]
    column_names = [c for c in Wallet.__dataclass_fields__.keys() if c not in COLUMNS_TO_NOT_LOAD]

    with wallets_table() as table:
        db_rows = table.select_all(SELECT=column_names, WHERE=table[BLOCKCHAIN] == chain_info._chain_str())

    db_rows = [dict(zip(column_names, row)) for row in db_rows]
    return token_wallets + [Wallet(chain_info=chain_info, **row) for row in _coalesce_rows(db_rows)]


def load_tokens(chain_info: 'ChainInfo') -> List[Token]:
    """Load known tokens from addresses DB for a chain."""
    column_names = [c for c in Token.__dataclass_fields__.keys() if c not in COLUMNS_TO_NOT_LOAD]

    with tokens_table() as table:
        db_rows = table.select_all(SELECT=column_names, WHERE=table[BLOCKCHAIN] == chain_info._chain_str())

    rows = [dict(zip(column_names, row)) for row in db_rows]
    return [Token(**row) for row in _coalesce_rows(rows)]


def insert_rows(table_name: str, rows: DbRows) -> None:
    """Insert 'rows' into table named 'table_name'. Assumes all rows have the same data_source."""
    print_dim(f"Writing {len(rows)} rows to table '{table_name}'...")
    db_conn = get_db_connection()
    columns = db_conn.get_columns_names(table_name)
    row_tuples = [[row.get(c) for c in columns] for row in rows]

    if True: #Config.debug:
        console.print(Panel("FIRST ROW TO INSERT", expand=False))
        pprint(rows[0])

    try:
        db_conn.insertmany(table_name, row_tuples)
    except IntegrityError as e:
        if Config.debug:
            console.print_exception()

        console.print(f"{e} while bulk loading!", style='bright_red')
        console.print("Cleaning up before switching to one at a time...", style='bright_white')
        delete_rows_from_source(table_name, rows[0]['data_source'])
        _insert_one_at_a_time(table_name, row_tuples)
    finally:
        # Hold connection open for big inserts bc writing is slow.
        if not Config.skip_load_from_db:
            db_conn.disconnect()

    print_dim(f"Finished writing {len(rows)} rows to '{table_name}'.")


def insert_wallets_from_data_source(wallets: List[Wallet]) -> None:
    """Update all rows from a given data_source (assumes all 'wallets' have same data_source)"""
    _prepare_rows(wallets)
    delete_rows_from_source(WALLETS_TABLE_NAME, wallets[0].data_source)
    insert_rows(WALLETS_TABLE_NAME, [wallet.to_address_db_row() for wallet in wallets])


def insert_tokens_from_data_source(tokens: List[Token]) -> None:
    """Update all rows from a given data_source (assumes all 'tokens' have same data_source)"""
    _prepare_rows(tokens)
    delete_rows_from_source(TOKENS_TABLE_NAME, tokens[0].data_source)
    insert_rows(TOKENS_TABLE_NAME, [token.__dict__ for token in tokens])


def _prepare_rows(objs: Union[List[Token], List[Wallet]]) -> None:
    """Validate all rows have same data_source. Set 'extracted_at' and 'data_source_id' fields."""
    if len(objs) == 0:
        return

    data_source = objs[0].data_source

    if data_source is None or not isinstance(data_source, str):
        raise ValueError(f"Invalid data_source field for {objs[0]}!")

    extracted_at = current_timestamp_iso8601_str()
    data_source_id = _get_or_create_data_source_id(data_source)

    for obj in objs:
        if obj.data_source != data_source:
            raise ValueError(f"Insertion have mismatched data_sources: '{obj.data_source}' != '{data_source}'")

        obj.extracted_at = obj.extracted_at or extracted_at
        obj.data_source_id = data_source_id
        #import pdb;pdb.set_trace()
        if 'extra_fields' in dir(obj) and obj.extra_fields is not None:
            obj.extra_fields = json.dumps(obj.extra_fields)


def delete_rows_from_source(table_name: str, _data_source: str) -> None:
    """Delete all rows where _data_source arg is the data_source col. (Allows updates by reloading entire source)"""
    data_source_id = _get_or_create_data_source_id(_data_source)

    with table_connection(table_name) as db_table:
        data_source_row_count = db_table.select(
            SELECT='COUNT(*)',
            WHERE=(db_table[DATA_SOURCE_ID] == data_source_id)
        )[0][0]

        if data_source_row_count == 0:
            return

        console.print(f"Deleting {data_source_row_count} rows in '{table_name}' sourced from '{_data_source}'...", style='bytes')
        db_table.delete({DATA_SOURCE_ID: data_source_id})
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
    db_conn = get_db_connection()

    for table_definition in TABLE_DEFINITIONS:
        table_definition.drop_table(db_conn)

    for table_definition in TABLE_DEFINITIONS:
        table_definition.create_table(db_conn)


def get_db_connection() -> sx.SQLite3x:
    """Make sure db._db is built / connected and that the tables h`ave been created."""
    if db._db is None:
        db._db = sx.SQLite3x(path=db.CHAIN_ADDRESSES_DB_PATH)

    if not _is_connected_to_db_file():
        db._db.connect()

    for table_definition in TABLE_DEFINITIONS:
        if not is_table_in_database(table_definition.table_name):
            table_definition.create_table(db._db)

    return db._db


def _insert_one_at_a_time(table_name: str, rows: List[List[Any]]) -> None:
    """Insert 'rows' into table named 'table_name' one at a time for use as a fallback."""
    console.print(f"Fallback write {len(rows)} rows to '{table_name}' one at a time...", style='bright_yellow')
    rows_written = 0
    failed_writes = 0

    with table_connection(table_name) as table:
        for row in rows:
            log.debug(f"Inserting {row}")

            try:
                table.insert(row)
                rows_written += 1
            except IntegrityError as e:
                if Config.debug:
                    console.print_exception()

                log.warning(f"Skipping because {type(e).__name__} error on row {row}...")
                failed_writes += 1

    print_dim(f"Wrote {rows_written} '{table_name}' rows one at a time ({failed_writes} failures).")


# https://stackoverflow.com/questions/71655300/python-sqlite3-how-to-check-if-connection-is-an-in-memory-database
def _is_connected_to_db_file() -> bool:
    """Abuse 'pragma database list' to check if connection status real or just in memory."""
    if not db._db.connection:
        return False

    log.debug("Checking DB connection status...")
    local_cursor = db._db.connection.cursor()
    local_cursor.execute('pragma database_list')
    connected_to_file = local_cursor.fetchall()[0][2]
    return connected_to_file is not None and len(connected_to_file) > 0


def _get_or_create_data_source_id(data_source: str) -> int:
    """Get the data_sources.id, creating a row if necessary."""
    data_sources = _load_table(DATA_SOURCES_TABLE_NAME)
    row = next((r for r in data_sources if r[DATA_SOURCE] == data_source), None)

    if row is not None:
        return row['id']

    with table_connection(DATA_SOURCES_TABLE_NAME) as table:
        table.insert(data_source=data_source, created_at=current_timestamp_iso8601_str())
        return table.select_all(WHERE=table[DATA_SOURCE] == data_source)[0][0]


def _load_table(table_name: str) -> List[Dict[str, Any]]:
    """Load whole table into list of dicts."""
    with table_connection(table_name) as table:
        column_names = table.get_columns_names()
        rows = table.select_all()

    log.debug(f"Table '{table_name}' has columns:\n  {column_names}\nrows: {rows}")
    return [dict(zip(column_names, row)) for row in rows]


def _coalesce_rows(rows: DbRows) -> DbRows:
    """Assemble the best data for each address by combining the data_sources in the DB."""
    if len(rows) == 0:
        return rows

    cols = list(rows[0].keys())
    coalesced_rows: Dict[str, Dict[str, Any]] = {}

    for row in rows:
        address = row[ADDRESS]

        # If the address is not in the coalesced_rows yet just add it and go to next row
        if address not in coalesced_rows:
            #log.debug(f"Initializing {address} with data from {row['data_source_id']}")
            coalesced_rows[address] = row
            continue

        # Otherwise fill in any missing fields in the coalesced row with data from 'row'
        coalesced_row = coalesced_rows[address]

        for col in cols:
            #log.debug(f"Updating {address}: {col} with '{row[col]}' from {row['data_source_id']}...")
            coalesced_row[col] = coalesced_row.get(col) or row.get(col)

    return list(coalesced_rows.values())
