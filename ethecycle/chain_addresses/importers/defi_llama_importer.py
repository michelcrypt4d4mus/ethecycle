"""
Import data from DeFi Llama repo by doing a best-effort parse through various JSON and
javascript files. TODO: we could always extract more by trying harder.
"""
import json
from glob import glob
from os import path
from pathlib import Path
from subprocess import check_output
from typing import List

import json5
from rich.panel import Panel

from ethecycle.blockchains.blockchains import CHAIN_IDS
from ethecycle.chain_addresses.address_db import insert_addresses
from ethecycle.chain_addresses.github_data_source import GithubDataSource
from ethecycle.models.blockchain import guess_chain_info_from_address
from ethecycle.models.token import Token
from ethecycle.models.wallet import Wallet
from ethecycle.util.dict_helper import walk_json
from ethecycle.util.filesystem_helper import files_in_dir, load_file_contents, subdirs_of_dir
from ethecycle.util.logging import console, log, print_address_import
from ethecycle.util.string_constants import *

DEFI_LLAMA_REPO = GithubDataSource('DefiLlama/DefiLlama-Adapters')
CONFIG_REGEX = re.compile('.*const config = ({.*})', re.MULTILINE | re.DOTALL)
JSON_FILES_TO_SKIP = ['abi', 'Abi', 'package', 'package-lock', 'tsconfig']

CEX_MAPPING = {
    'crypto-com': 'Crypto.com',
    'gate-io': 'Gate.io',
    'nexo-cex': 'Nexo'
}


def import_defi_llama_addresses():
    with DEFI_LLAMA_REPO.local_repo_path() as repo_dir:
        cex_grep_results = check_output(f"grep -r 'const {{ cexExports }}' '{repo_dir}'", shell=True).decode()
        cex_json_paths = [result.split(':')[0] for result in cex_grep_results.split("\n")]
        wallets: List[Wallet] = []

        for cex_json_path in cex_json_paths:
            if len(cex_json_path) == 0:
                continue

            cex = Path(cex_json_path).parent.name
            cex = CEX_MAPPING.get(cex, cex)
            log.info(f"CEX: '{cex}', path: '{cex_json_path}'")
            javascript = load_file_contents(cex_json_path)
            match = CONFIG_REGEX.match(javascript)
            address_json5 = match.group(1)
            log.debug(address_json5)

            try:
                addresses_by_chain = json5.loads(address_json5)
            except Exception:
                log.error(f"Failed to parse {cex_json_path}")
                continue

            for chain, owners_dict in addresses_by_chain.items():
                chain = 'avax-c' if chain == 'avax' else chain

                for address in owners_dict['owners']:
                    wallet = Wallet(
                        address=address,
                        blockchain=chain,
                        category='cex',
                        name=cex,
                        data_source=DEFI_LLAMA_REPO.repo_url,
                        organization=cex
                    )
                    console.print(wallet)
                    wallets.append(wallet)

        # BitMex has a special file for bitcoin addresses
        with open(path.join(repo_dir, 'projects', 'bitmex', 'bitcoin.json')) as bitmex_bitcoin_file:
            for bitmex_bitcoin_address in json.load(bitmex_bitcoin_file):
                #print(bitmex_bitcoin_addresses)
                wallet = Wallet(
                    address=bitmex_bitcoin_address,
                    blockchain='bitcoin',
                    category='cex',
                    name='bitmex',
                    data_source=DEFI_LLAMA_REPO.repo_url,
                    organization='bitmex'
                )

        json_files = glob(path.join(repo_dir, 'projects', '**', '*.json'), recursive=True)
        json_files = [jf for jf in json_files if not any([jf.endswith(f"{sf}.json") for sf in JSON_FILES_TO_SKIP])]

        for json_file in json_files:
            if json_file.endswith('bitmex/bitcoin.json'):
                continue

            console.print(Panel(json_file, style='reverse'))
            json_data = json.loads(load_file_contents(json_file))
            console.print("\n\n\nScanning for possibilities...")
            console.print_json(json.dumps(json_data))
            have_printed_contents = False

            for k, v in walk_json(json_data):
                # /pendle/ subdir does key/value backwards
                if '/pendle/' in json_file and 'funded' in k:
                    tmp = k
                    k = '.'.join(k.split('.')[0:-1] + [v])
                    v = tmp.split('.')[-1]

                log.debug(f"Scanning '{k}'...")
                blockchain_guess = guess_chain_info_from_address(v)

                # TODO: 'algorand' is just the first dummy ChainInfo obj. it gets returned when other cannot be found.
                if blockchain_guess is not None and blockchain_guess.chain_string() != 'algorand':
                    blockchain_guess_str = blockchain_guess.chain_string()

                    if not have_printed_contents:
                        console.print_json(json.dumps(json_data))
                        have_printed_contents = True

                    for chain in CHAIN_IDS.values():
                        log.debug(f"    Re-checking {chain} in {k}")

                        if chain in (k or ''):
                            blockchain_guess_str = chain
                            break

                    json_local_path = json_file.removeprefix(repo_dir + '/projects/')
                    comment_str = "DeFiLlama file: " + json_local_path
                    json_project = json_local_path.split('/')[0]
                    label = f"{k} ({json_project})"
                    log.debug(f"file='{comment_str}', label='{label}', address='{v}', guess='{blockchain_guess_str}'")

                    wallet = Wallet(
                        blockchain=blockchain_guess_str,
                        address=v,
                        name=label,
                        data_source=DEFI_LLAMA_REPO.repo_url,
                        category='defi'
                    )

                    wallets.append(wallet)

        insert_addresses(wallets)
