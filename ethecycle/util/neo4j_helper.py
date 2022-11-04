"""
Methods that interact with the Neo4j docker container.
"""
from contextlib import contextmanager
from os import environ, path
from subprocess import check_output
from typing import List

from rich.text import Text

from ethecycle.config import Config
from ethecycle.util.filesystem_helper import OUTPUT_DIR, timestamp_for_filename
from ethecycle.util.logging import PEACH, console

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

# Graph stuff TODO: could use the chain for labeling e.g. 'eth_wallet' and 'eth_txn'
NODE_LABEL = 'Wallet'
EDGE_LABEL = 'TXN'
HEADER = 'header'
INDENT = '      '

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


def admin_load_bash_command(neo4j_csvs: List['Neo4jCsvs']) -> str:
    """Generate shell command to bulk load a set of CSVs."""
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


def import_to_neo4j(bulk_load_shell_command: str) -> None:
    """Load into the Neo4J database via bulk load."""
    ssh_cmd = f"{NEO4J_SSH} {bulk_load_shell_command}"
    console.print("About to actually execute:\n", style='bright_red')
    print(ssh_cmd + "\n")
    ssh_result = check_output(ssh_cmd.split(' ')).decode()
    console.print(f"\nRESULT:\n{ssh_result}\n")


@contextmanager
def stop_database():
    """Start and stop the database in a context."""
    raise ValueError("This only works on neo4j enterprise.")
    execute_cypher_query(STOP_DB_QUERY)

    try:
        yield
    except Exception as e:
        console.print_exception()
        raise e
    finally:
        execute_cypher_query(START_DB_QUERY)


def execute_cypher_query(cql: str) -> str:
    """Execute CQL query on the Neo4J container"""
    console.print(Text("Executing CQL query: ").append(cql, style=PEACH))
    user, password = _neo4j_user_and_pass()
    cmd = f"echo '{cql}' | {CYPHER_EXECUTABLE} -u {user} -p {password}"
    return _execute_shell_cmd_on_neo4j_container(cmd)


def _execute_shell_cmd_on_neo4j_container(cmd: str) -> str:
    remote_cmd = f"{NEO4J_SSH} {cmd}"
    print(f"Executing remote command:\n\n{remote_cmd}")
    cmd_result = check_output(remote_cmd.split(' ')).decode().rstrip()
    console.print(f"\nRESULT:\n{cmd_result}\n")
    return cmd_result


def _neo4j_user_and_pass() -> List[str]:
    """Returns a 2-tuple, [username, password]."""
    if '/' not in (NEO4J_AUTH or ''):
        raise ValueError("NEO4J_AUTH env var is not set correctly")

    return NEO4J_AUTH.split('/')
