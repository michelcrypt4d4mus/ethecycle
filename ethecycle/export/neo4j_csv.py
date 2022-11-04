"""
Turn a transactions file into CSVs Neo4j admin tool can import and import it.
Unclear if there's a way to just load from a single CSV and have it create nodes on the fly.

Docs: https://neo4j.com/docs/operations-manual/current/tools/neo4j-admin/neo4j-admin-import/

Data types: int, long, float, double, boolean, byte, short, char, string, point, date,
            localtime, time, localdatetime, datetime, duration
"""
import csv
import time
from datetime import datetime
from os import path
from typing import List, Union

from ethecycle.blockchains.blockchains import get_chain_info

from ethecycle.models.transaction import Txn
from ethecycle.util.filesystem_helper import OUTPUT_DIR, timestamp_for_filename
from ethecycle.util.neo4j_helper import EDGE_LABEL, HEADER, NODE_LABEL
from ethecycle.util.logging import print_benchmark
from ethecycle.util.string_constants import ETHEREUM
from ethecycle.models.wallet import Wallet

WALLET_CSV_HEADER = [
    'address:ID',
    'blockchain',
    'label',
    'category',
    'extracted_at:datetime',
]

TXN_CSV_HEADER = [
    'transactionID',  # Combination of transaction_hash and log_index
    'blockchain',
    'token_address',
    'symbol',
    ':START_ID',  # from_address
    ':END_ID',  # to_address
    'num_tokens:double',
    'block_number:int',
    'extracted_at:datetime',
]


class Neo4jCsvs:
    def __init__(self, txns: Union[List[Txn], str], blockchain: str = ETHEREUM) -> None:
        """Generates CSV files from 'txns'. Prints headers if txns is 'header'. Output filenames are based on the timestamp."""
        csv_basename = HEADER if txns == HEADER else timestamp_for_filename()
        build_csv_path = lambda label: path.join(OUTPUT_DIR, f"{label}_{csv_basename}.csv")
        self.wallet_csv_path = build_csv_path(NODE_LABEL)
        self.txn_csv_path = build_csv_path(EDGE_LABEL)
        self.blockchain = blockchain

        if txns == HEADER:
            self._generate_header_csvs()
        else:
            # Don't make txns a property of the instance (pass them as arg) so GC can reclaim the memory later.
            self._generate_txn_and_wallet_csvs(txns)

    def generated_csvs(self) -> List[str]:
        """Paths of generated CSVs"""
        return [self.wallet_csv_path, self.txn_csv_path]

    def _generate_txn_and_wallet_csvs(self, txns: List[Txn]):
        """Break out wallets and txions into two CSV files for nodes and edges for Neo4j bulk loader."""
        extracted_at = datetime.utcnow().replace(microsecond=0).isoformat()
        chain_info = get_chain_info(self.blockchain)
        start_time = time.perf_counter()

        # Wallet nodes
        with open(self.wallet_csv_path, 'w') as csvfile:
            csv_writer = csv.writer(csvfile)

            for wallet in Wallet.extract_wallets_from_transactions(txns, chain_info):
                csv_writer.writerow(wallet.to_neo4j_csv_row() + [extracted_at])

        duration_from_start = print_benchmark('Wrote wallet CSV', start_time, indent_level=2)

        # Transaction edges
        with open(self.txn_csv_path, 'w') as csvfile:
            csv_writer = csv.writer(csvfile)

            for txn in txns:
                csv_writer.writerow(txn.to_neo4j_csv_row() + [extracted_at])

        print_benchmark('Wrote txn CSV', start_time + duration_from_start, indent_level=2)

    # NOTE: Had bizarre issues with this on macOS... removed WALLET_header.csv but could not write to
    #       Wallet_header.csv until I did a `touch /ethecycle/Wallet_header.csv`.
    #       I assume it has something to do w/macOS's lack of case sensitivity.
    def _generate_header_csvs(self) -> None:
        """Write single row CSVs with header info for nodes and edges."""
        with open(self.txn_csv_path, 'w') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(TXN_CSV_HEADER)

        with open(self.wallet_csv_path, 'w') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(WALLET_CSV_HEADER)
