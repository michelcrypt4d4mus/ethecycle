"""
Load transactions from CSV as python lists and/or directly into the graph database.
"""
import csv
import time
from os import path, remove
from subprocess import check_output
from typing import List, Optional

from rich.text import Text

from ethecycle.blockchains.blockchains import get_chain_info
from ethecycle.config import Config
from ethecycle.export.neo4j_csv import HEADER, Neo4jCsvs
from ethecycle.models.transaction import Txn
from ethecycle.util.filesystem_helper import OUTPUT_DIR, file_size_string, files_in_dir
from ethecycle.util.neo4j_helper import admin_load_bash_command, import_to_neo4j
from ethecycle.util.logging import ask_for_confirmation, console, log, print_benchmark

time_sorter = lambda txn: txn.block_number
wallet_sorter = lambda txn: txn.from_address

INCREMENTAL_LOAD_WARNING = Text("\nYou selected incremental import which probably doesn't work.\n", style='red')
INCREMENTAL_LOAD_WARNING.append('  Did you forget the --drop option?', style='bright_red')


def load_into_neo4j(
        txn_csv_path: str,
        blockchain: str,
        token: Optional[str] = None,
        preserve_csvs: Optional[bool] = False
    ) -> None:
    """ETL that loads chain txion CSVs into Neo4j."""
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
    neo4j_csvs = [Neo4jCsvs(HEADER)] + [_extract_and_transform(txn_csv, blockchain, token) for txn_csv in txn_csvs]
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
        for loaded_csv in [csv_file for neo_csvs in neo4j_csvs for csv_file in neo_csvs.generated_csvs()]:
            log.debug(f"Deleting successfully loaded CSV: {loaded_csv}")
            remove(loaded_csv)

    console.line(2)


def extract_transactions(csv_path: str, blockchain: str, token: Optional[str] = None) -> List[Txn]:
    """Load txions from a CSV to list of Txn objects optionally filtered for 'token' records only."""
    chain_info = get_chain_info(blockchain)
    token_address = None

    if not (token is None or token in chain_info.tokens()):
        raise ValueError(f"Address for '{token}' token not found.")

    msg = Text('Loading ').append(blockchain, style='color(112)').append(' chain ')

    if token:
        msg.append(token + ' ', style='color(207)')
        token_address = chain_info.token_address(token)

    console.print(msg.append(f"transactions from '").append(csv_path, 'green').append("'..."))
    console.print(f"   {file_size_string(csv_path)}", style='dim')

    with open(csv_path, newline='') as csvfile:
        return [
            Txn(*([blockchain] + row + [chain_info])) for row in csv.reader(csvfile, delimiter=',')
            if row[0] != 'token_address' and (token is None or row[0] == token_address)
        ]


def _extract_and_transform(csv_path: str, blockchain: str, token: Optional[str] = None) -> Neo4jCsvs:
    """Extract transactions and transform to Neo4j bulk load CSVs"""
    start_file_time = time.perf_counter()
    txns = extract_transactions(csv_path, blockchain, token)
    duration = print_benchmark('Extracted data from source CSV', start_file_time)
    neo4j_csvs = Neo4jCsvs(txns, blockchain)
    print_benchmark(f"Generated CSVs for {path.dirname(csv_path)}", start_file_time + duration)
    return neo4j_csvs
