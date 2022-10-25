"""
Load transactions from CSV as python lists and/or directly into the graph database.
"""
import csv
import time
from itertools import groupby
from os import path
from typing import List, Optional

from rich.text import Text

from ethecycle.blockchains import get_chain_info
from ethecycle.config import Config
from ethecycle.transaction import Txn
from ethecycle.export.neo4j import INDENT, Neo4jCsvs, generate_neo4j_csvs
from ethecycle.util.filesystem_helper import (file_size_string, files_in_dir)
from ethecycle.util.logging import console
from ethecycle.util.types import WalletTxns

time_sorter = lambda txn: txn.block_number
wallet_sorter = lambda txn: txn.from_address


def create_neo4j_bulk_load_csvs(txn_csv_path: str, blockchain: str, token: Optional[str] = None) -> None:
    # Actual loading happens here
    if path.isfile(txn_csv_path):
        csv_files = [txn_csv_path]
    elif path.isdir(txn_csv_path):
        console.print('Directory detected...', style='grey')
        csv_files = [f for f in files_in_dir(txn_csv_path)] # if f.lower().endswith('.csv')]
    else:
        raise ValueError(f"'{txn_csv_path}' is not a filesystem path")

    neo4j_csvs: List[Neo4jCsvs] = []
    start_time = time.perf_counter()

    for csv_file in csv_files:
        start_file_time = time.perf_counter()
        txns = load_txion_csv(csv_file, blockchain, token)
        extract_duration = time.perf_counter() - start_file_time
        console.print(f"   Extracted data from source CSV in {extract_duration:02.2f} seconds...", style='benchmark')

        neo4j_csvs.append(generate_neo4j_csvs(txns, blockchain))
        generation_duration = time.perf_counter() - extract_duration -  start_time
        console.print(f"   Generated CSV for {path.dirname(csv_file)} in {generation_duration:02.2f} seconds...", style='benchmark')

    generation_duration = time.perf_counter() - start_time
    console.print(f"Generated import CSVs in {generation_duration:02.2f} seconds...", style='benchmark')
    shell_command = Neo4jCsvs.admin_load_bash_command_multi_file(neo4j_csvs)
    print(shell_command)
    #console.print(INDENT + shell_command, style='bright_red')
    console.line(2)


def get_wallets_txions(file_path: str, blockchain: str, token: Optional[str] = None) -> WalletTxns:
    """Get all txns for a given token"""
    txns = sorted(load_txion_csv(file_path, blockchain, token), key=wallet_sorter)

    return {
        from_address: sorted(list(txns), key=time_sorter)
        for from_address, txns in groupby(txns, wallet_sorter)
    }


def load_txion_csv(file_path: str, blockchain: str, token: Optional[str] = None) -> List[Txn]:
    """Load txions from a CSV, optionally filtered for 'token' records only."""
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
            Txn(*([blockchain] + row)) for row in csv.reader(csvfile, delimiter=',')
            if row[0] != 'token_address' and (token is None or row[0] == token_address)
        ]

        return txns



# def load_txn_csv_to_gremlin_db(
#         txn_csv_path: str,
#         blockchain: str,
#         token: str,
#         debug: bool = False
#     ):
#     """Load txns from a CSV file, filter them for token_address only, and load to graph via GraphML."""
#     start_time = time.perf_counter()
#     wallets_txns = get_wallets_txions(txn_csv_path, blockchain, token)
#     extract_duration = time.perf_counter() - start_time
#     console.print(f"   Extracted CSV in {extract_duration:02.2f} seconds...", style='benchmark')
#     output_file_path = str(OUTPUT_DIR.joinpath(basename(txn_csv_path) + GRAPHML_EXTENSION))
#     export_graphml(wallets_txns, ETHEREUM, output_file_path)

#     if debug:
#         pretty_print_xml_file(output_file_path)

#     console.print(f"Loading graphML from '{output_file_path}'...")
#     console.print(f"   {file_size_string(output_file_path)}", style='dim')
#     load_start_time = time.perf_counter()

#     if not is_running_in_container():
#         output_file_path = system_path_to_container_path(output_file_path)

#     g.io(output_file_path).read().iterate()
#     load_duration = time.perf_counter() - load_start_time
#     console.print(f"   Loaded to graph in {load_duration:02.2f} seconds...", style='benchmark')
#     overall_duration = time.perf_counter() - start_time
#     console.print(f"Start to finish runtime: {overall_duration:02.2f} seconds...", style=BYTES_HIGHLIGHT)

