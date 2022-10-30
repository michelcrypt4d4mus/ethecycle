"""
Load transactions from CSV as python lists and/or directly into the graph database.
"""
import csv
import time
from os import path
from typing import List, Optional

from rich.text import Text

from ethecycle.blockchains import get_chain_info
from ethecycle.config import Config
from ethecycle.transaction import Txn
from ethecycle.export.neo4j import INDENT, Neo4jCsvs, generate_neo4j_csvs
from ethecycle.util.filesystem_helper import (file_size_string, files_in_dir)
from ethecycle.util.logging import console, print_benchmark

time_sorter = lambda txn: txn.block_number
wallet_sorter = lambda txn: txn.from_address


def create_neo4j_bulk_load_csvs(txn_csv_path: str, blockchain: str, token: Optional[str] = None) -> None:
    """Loads CSVs into Neo4j. TODO: rename to load_neo4j_csvs"""
    if not Config.drop_database:
        console.print("\nYou selected incremental import which probably doesn't work. Did you forget the --drop option?", style='bright_red')
        input("    Ctrl-C to stop this train, any other key to continue: ")

    # Actual loading happens here
    if path.isfile(txn_csv_path):
        csv_files = [txn_csv_path]
    elif path.isdir(txn_csv_path):
        console.print('Directory detected...', style='grey')
        csv_files = files_in_dir(txn_csv_path)
    else:
        raise ValueError(f"'{txn_csv_path}' is not a filesystem path")

    neo4j_csvs: List[Neo4jCsvs] = []
    start_time = time.perf_counter()

    for csv_file in csv_files:
        start_file_time = time.perf_counter()
        txns = load_txion_csv(csv_file, blockchain, token)
        duration = print_benchmark('Extracted data from source CSV', start_file_time)
        neo4j_csvs.append(generate_neo4j_csvs(txns, blockchain))
        print_benchmark(f"Generated CSVs for {path.dirname(csv_file)}", start_file_time + duration)

    print_benchmark('\nGenerated import CSVs', start_time, indent_level=0, style='yellow')

    if Config.extract_only:
        print("\n" + Neo4jCsvs.admin_load_bash_command(neo4j_csvs))
        console.print("\n     --extract-only is on so not executing load. Above command can be run manually.", style='red bold')
    else:
        Neo4jCsvs.load_to_db(neo4j_csvs)

    console.line(2)


def load_txion_csv(file_path: str, blockchain: str, token: Optional[str] = None) -> List[Txn]:
    """Load txions from a CSV to list of Txn objects optionally filtered for 'token' records only."""
    chain_info = get_chain_info(blockchain)
    token_address = None

    if not (token is None or token in chain_info.tokens()):
        raise ValueError(f"Address for '{token}' token not found.")

    msg = Text('Loading ').append(blockchain, style='color(112)').append(' chain ')

    if token:
        msg.append(token + ' ', style='color(207)')
        token_address = chain_info.token_address(token)

    console.print(msg.append(f"transactions from '").append(file_path, 'green').append("'..."))
    console.print(f"   {file_size_string(file_path)}", style='dim')

    with open(file_path, newline='') as csvfile:
        txns = [
            Txn(*([blockchain] + row + [chain_info])) for row in csv.reader(csvfile, delimiter=',')
            if row[0] != 'token_address' and (token is None or row[0] == token_address)
        ]

        return txns
