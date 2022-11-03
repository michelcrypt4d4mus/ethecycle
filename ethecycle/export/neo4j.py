"""
Turn a transactions file into CSVs Neo4j admin tool can import and import it.
Unclear if there's a way to just load from a single CSV and have it create nodes on the fly.

Docs: https://neo4j.com/docs/operations-manual/current/tools/neo4j-admin/neo4j-admin-import/

Data types: int, long, float, double, boolean, byte, short, char, string, point, date,
            localtime, time, localdatetime, datetime, duration
"""
import csv
import time
from contextlib import contextmanager
from datetime import datetime
from os import environ, path
from subprocess import check_output
from typing import List, Optional

from rich.text import Text
from ethecycle.blockchains.blockchains import get_chain_info

from ethecycle.config import Config
from ethecycle.transaction import Txn
from ethecycle.util.filesystem_helper import OUTPUT_DIR, timestamp_for_filename
from ethecycle.util.logging import PEACH, console, print_benchmark
from ethecycle.util.string_constants import ETHEREUM
from ethecycle.wallet import Wallet

# Path on the docker container
NEO4J_DB = 'neo4j'
NEO4J_BIN_DIR = '/var/lib/neo4j/bin'
NEO4J_AUTH = environ.get('NEO4J_AUTH')
NEO4J_SSH = f"ssh root@neo4j -o StrictHostKeyChecking=accept-new "
NEO4J_ADMIN_EXECUTABLE = path.join(NEO4J_BIN_DIR, 'neo4j-admin')
CSV_IMPORT_CMD = f"{NEO4J_ADMIN_EXECUTABLE} database import"
CYPHER_EXECUTABLE = path.join(NEO4J_BIN_DIR, 'cypher-shell')

START_DB_QUERY = f"STOP DATABASE {NEO4J_DB}"
STOP_DB_QUERY = f"STOP DATABASE {NEO4J_DB}"
START_SERVER_CMD = f"{NEO4J_ADMIN_EXECUTABLE} server start "
STOP_SERVER_CMD = f"{NEO4J_ADMIN_EXECUTABLE} server stop "

# TODO: could use the chain for labeling e.g. 'eth_wallet' and 'eth_txn'
NODE_LABEL = 'Wallet'
EDGE_LABEL = 'TXN'
INDENT = '      '

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
    'report-file': OUTPUT_DIR.joinpath(f"import_{timestamp_for_filename()}.log"),
    'skip-duplicate-nodes': 'true',
    'trim-strings': 'true',
}

INCREMENTAL_INSTRUCTIONS = Text() + Text(f"Incremental import to current DB '{NEO4J_DB}'...\n\n", style='magenta bold') + \
    Text(f"You must stop the server to run incremental import:\n") + \
    Text(f"      {STOP_SERVER_CMD}\n", style='bright_cyan') + \
    Text(f"Afterwards restart with:\n") + \
    Text(f"      {START_SERVER_CMD}\n\n", style='bright_cyan') + \
    Text(
        f"Incremental load via neo4j-admin doesn't seem to work; use --drop options or LOAD CSV instead\n",
        style='bright_red bold blink reverse',
        justify='center'
    ) + \
    Text(f"(If you messed up and forgot the --drop option, replace command with:\n   {CSV_IMPORT_CMD} full --id-type=string --skip-duplicate-nodes=true --overwrite-destination=true", style='dim')


class Neo4jCsvs:
    def __init__(self, csv_basename: Optional[str] = None) -> None:
        """Generates filenames based on the timestamp."""
        csv_basename = csv_basename or timestamp_for_filename()
        build_csv_path = lambda label: path.join(OUTPUT_DIR, f"{label}_{csv_basename}.csv")
        self.wallet_csv_path = build_csv_path(NODE_LABEL)
        self.txn_csv_path = build_csv_path(EDGE_LABEL)

    @staticmethod
    def admin_load_bash_command(neo4j_csvs: List['Neo4jCsvs']) -> str:
        """Generate shell command to bulk load a set of CSVs."""
        neo4j_csvs = [write_header_csvs()] + neo4j_csvs
        wallet_csvs = [n.wallet_csv_path for n in neo4j_csvs]
        txn_csvs = [n.txn_csv_path for n in neo4j_csvs]

        if Config.drop_database:
            msg = f"WARNING: This command will overwrite current DB '{NEO4J_DB}'!"
            console.print(msg, style='red blink bold', justify='center')
            LOADER_CLI_ARGS['overwrite-destination'] = 'true'
            subcommand = 'full'
        else:
            console.print(INCREMENTAL_INSTRUCTIONS)
            # '--force' is required for all incremental loads, which must be run when the DB is stopped
            LOADER_CLI_ARGS['force'] = 'true'
            LOADER_CLI_ARGS['stage'] = 'all'
            subcommand = 'incremental'

        load_args = [f"--{k}={v}" for k, v in LOADER_CLI_ARGS.items()]
        load_args.append(f"--nodes={NODE_LABEL}={','.join(wallet_csvs)}")
        load_args.append(f"--relationships={EDGE_LABEL}={','.join(txn_csvs)}")
        return f"{CSV_IMPORT_CMD} {subcommand} {' '.join(load_args)} {NEO4J_DB}"


def generate_neo4j_csvs(txns: List[Txn], blockchain: str = ETHEREUM) -> Neo4jCsvs:
    """Break out wallets and txions into two CSV files for nodes and edges."""
    extracted_at = datetime.utcnow().replace(microsecond=0).isoformat()
    chain_info = get_chain_info(blockchain)
    neo4j_csvs = Neo4jCsvs()
    start_time = time.perf_counter()

    # Wallet nodes
    with open(neo4j_csvs.wallet_csv_path, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)

        for wallet in Wallet.extract_wallets_from_transactions(txns, chain_info):
            csv_writer.writerow(wallet.to_neo4j_csv_row() + [extracted_at])

    duration_from_start = print_benchmark('Wrote wallet CSV', start_time, indent_level=2)

    # Transaction edges
    with open(neo4j_csvs.txn_csv_path, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)

        for txn in txns:
            csv_writer.writerow(txn.to_neo4j_csv_row() + [extracted_at])

    print_benchmark('Wrote txn CSV', start_time + duration_from_start, indent_level=2)
    return neo4j_csvs


# NOTE: Had bizarre issues with this on macOS... removed WALLET_header.csv but could not write to
#       Wallet_header.csv until I did a `touch /ethecycle/Wallet_header.csv`.
#       I assume it has something to do w/macOS's lack of case sensitivity.
def write_header_csvs() -> Neo4jCsvs:
    """Write single row CSVs with header info for nodes and edges."""
    header_csvs = Neo4jCsvs('header')

    with open(header_csvs.txn_csv_path, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(TXN_CSV_HEADER)

    with open(header_csvs.wallet_csv_path, 'w') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(WALLET_CSV_HEADER)

    return header_csvs


@contextmanager
def stop_database():
    """Start and stop the database in a context."""
    execute_cypher_query(STOP_DB_QUERY)

    try:
        yield
    except Exception as e:
        console.print_exception()
        raise e
    finally:
        execute_cypher_query(START_DB_QUERY)


def execute_cypher_query(cql: str) -> None:
    """Execute CQL query on the Neo4J container"""
    console.print(Text("Executing CQL query: ").append(cql, style=PEACH))
    user, password = _neo4j_user_and_pass()
    cmd = f"echo '{cql}' | {CYPHER_EXECUTABLE} -u {user} -p {password}"
    execute_shell_cmd_on_neo4j_container(cmd)


def execute_shell_cmd_on_neo4j_container(cmd: str) -> None:
    remote_cmd = f"{NEO4J_SSH} {cmd}"
    print(f"Executing remote command:\n\n{remote_cmd}")
    query_result = check_output(remote_cmd.split(' ')).decode()
    console.print(f"\nRESULT:\n{query_result}\n")


def _neo4j_user_and_pass() -> List[str]:
    """Returns a 2-tuple, [username, password]."""
    if '/' not in (NEO4J_AUTH or ''):
        raise ValueError("NEO4J_AUTH env var is not set correctly")

    return NEO4J_AUTH.split('/')
