"""
Turn a transactions file into CSVs Neo4j admin tool can import and import it.
Unclear if there's a way to just load from a single CSV and have it create nodes on the fly.

Docs: https://neo4j.com/docs/operations-manual/current/tools/neo4j-admin/neo4j-admin-import/

Data types: int, long, float, double, boolean, byte, short, char, string, point, date,
            localtime, time, localdatetime, datetime, duration
"""
import csv
from os.path import join
from typing import Any, Dict, List
from ethecycle.transaction import Txn

from ethecycle.util.filesystem_helper import OUTPUT_DIR, timestamp_for_filename
from ethecycle.util.string_constants import ETHEREUM
from ethecycle.util.types import WalletTxns

# Path on the docker container
NEO4J_DB = 'neo4j'
ADMIN_LOADER_CMD = f"/var/lib/neo4j/bin/neo4j-admin database import full "

# TODO: could use the chain for labeling e.g. 'eth_wallet' and 'eth_txn'
NODE_LABEL = 'WALLET'
EDGE_LABEL = 'TXN'

WALLET_CSV_HEADER = [
    'address:ID',
    'blockchain'
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
]

# Keys will be prefixed with '--' in the final command
LOADER_CLI_ARGS = {
    'id-type': 'string'
}


class Neo4jCsvs:
    def __init__(self) -> None:
        """Generates filenames based on the timestamp."""
        output_file_timestamp_str = timestamp_for_filename()

        self.wallet_csv_path, self.txn_csv_path = (
            join(OUTPUT_DIR, f"{label}_{output_file_timestamp_str}.csv")
            for label in [NODE_LABEL, EDGE_LABEL]
        )

    def generate_admin_load_bash_command(self) -> str:
        """Generate a shell command to be run on the Neo4j container"""
        load_args = [f"--{k}={v}" for k, v in LOADER_CLI_ARGS.items()]
        load_args.append(f"--nodes={NODE_LABEL}={self.wallet_csv_path}")
        load_args.append(f"--relationships={EDGE_LABEL}={self.txn_csv_path}")
        return f"{ADMIN_LOADER_CMD} " + ' '.join(load_args) + ' ' + NEO4J_DB


def generate_neo4j_csvs(wallets_txns: WalletTxns, blockchain: str = ETHEREUM) -> Neo4jCsvs:
    """Break out wallets and txions into two CSV files for nodes and edges."""
    neo4j_csvs = Neo4jCsvs()

    # Wallet nodes
    with open(neo4j_csvs.wallet_csv_path, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(WALLET_CSV_HEADER)
        # TODO: We need all to and from addresses... the WalletTxns is not the most helpful structure
        all_txns = [txn for txns in wallets_txns.values() for txn in txns]
        wallets = set(wallets_txns.keys()).union(set([txn.to_address for txn in all_txns]))

        for wallet_address in wallets:
            csv_writer.writerow([wallet_address, blockchain])

    with open(neo4j_csvs.txn_csv_path, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(TXN_CSV_HEADER)

        for txns in wallets_txns.values():
            for txn in txns:
                csv_writer.writerow(_neo4j_csv_row(txn))

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
        txn.block_number
    ]
