"""
Load transactions from CSV as python lists and/or directly into the graph database.
"""
import time
from os import path, remove
from typing import List, Optional, Type

from rich.text import Text

from ethecycle.blockchains.blockchains import get_chain_info
from ethecycle.config import Config
from ethecycle.export.neo4j_csv import HEADER, Neo4jCsvs
from ethecycle.models.transaction import Txn
from ethecycle.util.filesystem_helper import OUTPUT_DIR, files_in_dir
from ethecycle.util.logging import ask_for_confirmation, console, log, print_benchmark
from ethecycle.util.neo4j_helper import admin_load_bash_command, import_to_neo4j
from ethecycle.util.time_helper import current_timestamp_iso8601_str
from ethecycle.util.string_constants import *

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

INCREMENTAL_LOAD_WARNING = Text("\nYou selected incremental import which probably doesn't work.\n", style='red')
INCREMENTAL_LOAD_WARNING.append('  Did you forget the --drop option?', style='bright_red')

time_sorter = lambda txn: txn.block_number
wallet_sorter = lambda txn: txn.from_address


def load_into_neo4j(
        txn_csv_path: str,
        blockchain: str,
        token: Optional[str] = None,
        preserve_csvs: Optional[bool] = False
    ) -> None:
    """
    ETL that loads chain txion CSVs into Neo4j, optionally filtered for 'token' arg.
    CSVs will be deleted after successful load unless the 'preserve_csvs' arg is set to True.
    """
    if not Config.drop_database:
        ask_for_confirmation(INCREMENTAL_LOAD_WARNING)

    if path.isfile(txn_csv_path):
        txn_csvs = [txn_csv_path]
    elif path.isdir(txn_csv_path):
        console.print(f"Directory detected, loading all files from '{txn_csv_path}'...", style='bright_cyan')
        txn_csvs = files_in_dir(txn_csv_path)
    else:
        raise ValueError(f"'{txn_csv_path}' is not a filesystem path")

    start_time = time.perf_counter()
    extracted_at = current_timestamp_iso8601_str()
    chain_info = get_chain_info(blockchain)

    neo4j_csvs = [Neo4jCsvs(HEADER)] + [
        _extract_and_transform(txn_csv, chain_info, extracted_at, token)
        for txn_csv in txn_csvs
    ]

    print_benchmark(f"\nProcessed {len(txn_csvs)} CSVs", start_time, indent_level=0, style='yellow')
    bulk_load_shell_command = admin_load_bash_command(neo4j_csvs)

    if Config.extract_only:
        print("\n" + bulk_load_shell_command)  # Use regular print() because console.print() does weird line wraps
        console.print("\n     --extract-only mode; not executing load. Above command can be run manually.", style='red bold')
    elif Config.drop_database:
        import_to_neo4j(bulk_load_shell_command)
    else:
        print("\n" + bulk_load_shell_command)
        raise ValueError("Incremental load doesn't work yet)")
        with stop_database() as context:
            _import_to_neo4j(bulk_load_shell_command)

    console.line()

    if preserve_csvs:
        console.print(f"Successfully loaded CSVs left in '{OUTPUT_DIR}' and not deleted.", style='color(93)')
    else:
        for loaded_csv in [csv_file for neo_csvs in neo4j_csvs for csv_file in neo_csvs.generated_csvs]:
            log.debug(f"Deleting successfully loaded CSV: {loaded_csv}")
            remove(loaded_csv)

    console.line(2)


def _extract_and_transform(csv_path: str, chain_info: Type['ChainInfo'], extracted_at: str, token: Optional[str] = None) -> Neo4jCsvs:
    """Extract transactions and transform to Neo4j bulk load CSVs"""
    start_file_time = time.perf_counter()
    txns = Txn.extract_from_csv(csv_path, chain_info, extracted_at)

    if token:
        token_address = chain_info.token_address(token)
        txns = [txn for txn in txns if txn.token_address == token_address]

    duration = print_benchmark('Extracted data from source CSV', start_file_time)
    neo4j_csvs = Neo4jCsvs(txns, chain_info)
    print_benchmark(f"Generated CSVs for {path.dirname(csv_path)}", start_file_time + duration)
    return neo4j_csvs
