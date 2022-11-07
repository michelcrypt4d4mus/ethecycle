"""
Load transactions from CSV as python lists and/or directly into the graph database.
"""
import time
from os import path, remove
from typing import List, Optional

from rich.text import Text

from ethecycle.config import Config
from ethecycle.export.neo4j_csv import HEADER, Neo4jCsvs
from ethecycle.models.blockchain import get_chain_info
from ethecycle.models.transaction import Txn
from ethecycle.util.filesystem_helper import OUTPUT_DIR
from ethecycle.util.logging import console, log, print_benchmark
from ethecycle.util.neo4j_helper import admin_load_bash_command, import_to_neo4j
from ethecycle.util.string_constants import *
from ethecycle.util.time_helper import current_timestamp_iso8601_str


def load_into_neo4j(txn_csvs: List[str], blockchain: str, token: Optional[str] = None) -> None:
    """
    ETL that loads chain txion CSVs into Neo4j, optionally filtered for 'token' arg.
    CSVs will be deleted after successful load unless the 'preserve_csvs' arg is set to True.
    """
    extracted_at = current_timestamp_iso8601_str()
    start_time = time.perf_counter()
    chain_info = get_chain_info(blockchain)
    neo4j_csvs = [Neo4jCsvs(HEADER)]

    for txn_csv in txn_csvs:
        start_file_time = time.perf_counter()
        txns = Txn.extract_from_csv(txn_csv, chain_info, extracted_at, token)
        duration = print_benchmark(f"Extracted {len(txns)} from source CSV", start_file_time)
        neo4j_csvs.append(Neo4jCsvs(txns))
        print_benchmark(f"Generated CSVs for '{path.basename(txn_csv)}'", start_file_time + duration)

    # Create neo4j-admin shell command that will bulk load all the Neo4j CSVs we just extracted/transformed.
    bulk_load_shell_command = admin_load_bash_command(neo4j_csvs)
    print_benchmark(f"\nProcessed {len(txn_csvs)} CSVs", start_time, indent_level=0, style='yellow')

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

    _clean_up(neo4j_csvs)


def _clean_up(neo4j_csvs: List[Neo4jCsvs]) -> None:
    """Remove CSVs that were successfully loaded and other maintenance"""
    console.line()

    if Config.preserve_csvs:
        console.print(f"Successfully loaded CSVs left in '{OUTPUT_DIR}' and not deleted.", style='color(93)')
    else:
        for loaded_csv in [csv_file for neo_csvs in neo4j_csvs for csv_file in neo_csvs.generated_csvs]:
            log.debug(f"Deleting successfully loaded CSV: {loaded_csv}")
            remove(loaded_csv)

    console.line(2)
