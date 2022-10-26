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
from typing import Any, Dict, List, Optional

from rich.text import Text

from ethecycle.config import Config
from ethecycle.transaction import Txn
from ethecycle.util.filesystem_helper import OUTPUT_DIR, timestamp_for_filename
from ethecycle.util.logging import console
from ethecycle.util.string_constants import ETHEREUM

# Path on the docker container
NEO4J_DB = 'neo4j'
NEO4J_ADMIN_EXECUTABLE = '/var/lib/neo4j/bin/neo4j-admin'
CSV_IMPORT_CMD = f"{NEO4J_ADMIN_EXECUTABLE} database import "
STOP_SERVER_CMD = f"{NEO4J_ADMIN_EXECUTABLE} server stop "
START_SERVER_CMD = f"{NEO4J_ADMIN_EXECUTABLE} server start "

# TODO: could use the chain for labeling e.g. 'eth_wallet' and 'eth_txn'
NODE_LABEL = 'WALLET'
EDGE_LABEL = 'TXN'
MISSING_ADDRESS = 'no_address'
INDENT = '      '

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
    'skip-duplicate-nodes': 'true'
}

LOAD_INSTRUCTIONS = Text(f"\nTo load the CSV into Neo4j get a shell on the neo4j container ") + \
        Text("then copy paste the command below.\n") + \
        Text(f"To get such a shell on the Neo4j container run this script from the OS bash shell:\n\n") + \
        Text(f"{INDENT}scripts/docker/neo4j_shell.sh\n\n", style='bright_cyan') + \
        Text(f"neo4j-admin command to copy/paste:")

INCREMENTAL_INSTRUCTIONS = Text() + Text(f"Incremental import to current DB '{NEO4J_DB}'...\n\n", style='magenta bold') + \
    Text(f"You must stop the server to run incremental import:\n") + \
    Text(f"      {STOP_SERVER_CMD}\n", style='bright_cyan') + \
    Text(f"Afterwards restart with:\n") + \
    Text(f"      {START_SERVER_CMD}\n\n", style='bright_cyan') + \
    Text(
        f"Incremental load via neo4j-admin doesn't seem to work; use --drop options or LOAD CSV instead",
        style='bright_yellow bold blink reverse',
        justify='center'
    )


class Neo4jCsvs:
    def __init__(self, csv_basename: Optional[str] = None) -> None:
        """Generates filenames based on the timestamp."""
        csv_basename = csv_basename or timestamp_for_filename()
        build_csv_path = lambda label: path.join(OUTPUT_DIR, f"{label}_{csv_basename}.csv")
        self.wallet_csv_path = build_csv_path(NODE_LABEL)
        self.txn_csv_path = build_csv_path(EDGE_LABEL)

    @staticmethod
    def admin_load_bash_command(neo4j_csvs: List['Neo4jCsvs']) -> str:
        neo4j_csvs = [write_header_csvs()] + neo4j_csvs
        wallet_csvs = [n.wallet_csv_path for n in neo4j_csvs]
        txn_csvs = [n.txn_csv_path for n in neo4j_csvs]
        console.print(LOAD_INSTRUCTIONS)

        if Config.drop_database:
            msg = f"WARNING: This command will overwrite current DB '{NEO4J_DB}'!\n"
            console.print(msg, style='red blink bold', justify='center')
            LOADER_CLI_ARGS['overwrite-destination'] = 'true'
            subcommand = 'full'
        else:
            console.print(INCREMENTAL_INSTRUCTIONS)
            LOADER_CLI_ARGS['force'] = 'true'  # Apparently required for incremental load
            #LOADER_CLI_ARGS['stage'] = 'build'
            subcommand = 'incremental'

        load_args = [f"--{k}={v}" for k, v in LOADER_CLI_ARGS.items()]
        load_args.append(f"--nodes={NODE_LABEL}={','.join(wallet_csvs)}")
        load_args.append(f"--relationships={EDGE_LABEL}={','.join(txn_csvs)}")
        return f"{CSV_IMPORT_CMD} {subcommand} {' '.join(load_args)} {NEO4J_DB}"


def generate_neo4j_csvs(txns: List[Txn], blockchain: str = ETHEREUM) -> Neo4jCsvs:
    """Break out wallets and txions into two CSV files for nodes and edges."""
    extracted_at = datetime.utcnow().replace(microsecond=0).isoformat()
    neo4j_csvs = Neo4jCsvs()

    # Wallet nodes
    with open(neo4j_csvs.wallet_csv_path, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)
        wallets = set([txn.to_address for txn in txns]).union(set([txn.from_address for txn in txns]))
        wallets.add(MISSING_ADDRESS)

        for wallet_address in wallets:
            csv_writer.writerow([wallet_address, blockchain, extracted_at])

    # Transaction edges
    with open(neo4j_csvs.txn_csv_path, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)

        for txn in txns:
            csv_writer.writerow(_neo4j_csv_row(txn) + [extracted_at])

    return neo4j_csvs


def write_header_csvs() -> Neo4jCsvs:
    """One row CSV with header info"""
    header_csvs = Neo4jCsvs('header')

    with open(header_csvs.txn_csv_path, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(TXN_CSV_HEADER)

    with open(header_csvs.wallet_csv_path, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(WALLET_CSV_HEADER)

    return header_csvs


def _neo4j_csv_row(txn: Txn) -> List[Any]:
    """Generate row from Txn class."""
    return [
        txn.transaction_id,
        txn.blockchain,
        txn.token_address,
        txn.token,
        txn.from_address or MISSING_ADDRESS,
        txn.to_address or MISSING_ADDRESS,
        txn.num_tokens,
        txn.block_number
    ]
