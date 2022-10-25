"""
Turn a transactions file into CSVs Neo4j admin tool can import and import it.
Unclear if there's a way to just load from a single CSV and have it create nodes on the fly.

Docs: https://neo4j.com/docs/operations-manual/current/tools/neo4j-admin/neo4j-admin-import/

Data types: int, long, float, double, boolean, byte, short, char, string, point, date,
            localtime, time, localdatetime, datetime, duration
"""
import csv
from datetime import datetime
from os import environ, path
from typing import Any, Dict, List
from ethecycle.config import Config
from ethecycle.transaction import Txn

from ethecycle.util.filesystem_helper import OUTPUT_DIR, timestamp_for_filename
from ethecycle.util.logging import console
from ethecycle.util.string_constants import ETHEREUM
from ethecycle.util.types import WalletTxns

# Path on the docker container
NEO4J_DB = 'neo4j'
ADMIN_LOADER_EXECUTABLE = '/var/lib/neo4j/bin/neo4j-admin'
CSV_IMPORT_CMD = f"{ADMIN_LOADER_EXECUTABLE} database import "
STOP_SERVER_CMD = f"{ADMIN_LOADER_EXECUTABLE} server stop "
START_SERVER_CMD = f"{ADMIN_LOADER_EXECUTABLE} server start "

# TODO: could use the chain for labeling e.g. 'eth_wallet' and 'eth_txn'
NODE_LABEL = 'WALLET'
EDGE_LABEL = 'TXN'

WALLET_CSV_HEADER = [
    'address:ID',
    'blockchain',
    'extracted_at:datetime',
]

TXN_CSV_HEADER = [
    'transactionID',  # Combination of transaction_hash and log_index
    'blockchain',
    'token_address',
    'token',
    ':START_ID',  # from_address
    ':END_ID',  # to_address
    'num_tokens:double',
    'block_number:int',
    'extracted_at:datetime',
]

# Keys will be prefixed with '--' in the final command
LOADER_CLI_ARGS = {
    'id-type': 'string',
}


class Neo4jCsvs:
    def __init__(self) -> None:
        """Generates filenames based on the timestamp."""
        output_file_timestamp_str = timestamp_for_filename()

        self.wallet_csv_path, self.txn_csv_path = (
            path.join(OUTPUT_DIR, f"{label}_{output_file_timestamp_str}.csv")
            for label in [NODE_LABEL, EDGE_LABEL]
        )

    def generate_admin_load_bash_command(self) -> str:
        """Generate a shell command to be run on the Neo4j container"""
        if Config.drop_database:
            console.print(f"WARNING: This command will overwrite current DB '{NEO4J_DB}'!", style='red blink')
            LOADER_CLI_ARGS['overwrite-destination'] = 'true'
            subcommand = 'full'
        else:
            console.print(f"Incremental import to current DB '{NEO4J_DB}'...", style='bright_yellow')
            console.print(f"You must stop the server to run incremental import:")
            console.print(f"      {STOP_SERVER_CMD}", style='bright_cyan')
            console.print(f"Afterwards restart with:")
            console.print(f"      {START_SERVER_CMD}\n", style='bright_cyan')
            console.print(f"INCREMENTAL LOAD DOESN'T SEEM TO WORK YET", style='bright_red blink reverse')
            LOADER_CLI_ARGS['skip-duplicate-nodes'] = 'true'
            LOADER_CLI_ARGS['force'] = 'true'
            #LOADER_CLI_ARGS['stage'] = 'build'

            subcommand = 'incremental'

        console.line()
        load_args = [f"--{k}={v}" for k, v in LOADER_CLI_ARGS.items()]
        load_args.append(f"--nodes={NODE_LABEL}={self.wallet_csv_path}")
        load_args.append(f"--relationships={EDGE_LABEL}={self.txn_csv_path}")
        return f"{CSV_IMPORT_CMD} {subcommand} {' '.join(load_args)} {NEO4J_DB}"


def generate_neo4j_csvs(wallets_txns: WalletTxns, blockchain: str = ETHEREUM) -> Neo4jCsvs:
    """Break out wallets and txions into two CSV files for nodes and edges."""
    extracted_at = datetime.utcnow().replace(microsecond=0).isoformat()
    neo4j_csvs = Neo4jCsvs()

    # Wallet nodes
    with open(neo4j_csvs.wallet_csv_path, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(WALLET_CSV_HEADER)
        # TODO: We need all to and from addresses... the WalletTxns is not the most helpful structure
        all_txns = [txn for txns in wallets_txns.values() for txn in txns]
        wallets = set(wallets_txns.keys()).union(set([txn.to_address for txn in all_txns]))

        for wallet_address in wallets:
            csv_writer.writerow([wallet_address, blockchain, extracted_at])

    # Transaction edges
    with open(neo4j_csvs.txn_csv_path, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(TXN_CSV_HEADER)

        for txns in wallets_txns.values():
            for txn in txns:
                csv_writer.writerow(_neo4j_csv_row(txn) + [extracted_at])

    return neo4j_csvs

def _neo4j_csv_row(txn: Txn) -> List[Any]:
    """Generate row from Txn class."""
    return [
        txn.transaction_id,
        txn.blockchain,
        txn.token_address,
        txn.token,
        txn.from_address,
        txn.to_address,
        txn.num_tokens,
        txn.block_number
    ]
