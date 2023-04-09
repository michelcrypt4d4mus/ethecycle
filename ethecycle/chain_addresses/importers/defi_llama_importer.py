"""
Import data from ethereum-lists repo.
"""
import json
from os import path
from pathlib import Path
from subprocess import check_output
from typing import List

import pyjson5

from ethecycle.blockchains.blockchains import CHAIN_IDS
from ethecycle.chain_addresses.address_db import insert_addresses
from ethecycle.chain_addresses.github_data_source import GithubDataSource
from ethecycle.models.token import Token
from ethecycle.models.wallet import Wallet
from ethecycle.util.filesystem_helper import files_in_dir, load_file_contents, subdirs_of_dir
from ethecycle.util.logging import console, log, print_address_import
from ethecycle.util.string_constants import *

DEFI_LLAMA_REPO = GithubDataSource('DefiLlama/DefiLlama-Adapters')
CONFIG_REGEX = re.compile('.*const config = ({.*})', re.MULTILINE | re.DOTALL)

CEX_MAPPING = {
    'crypto-com': 'Crypto.com',
    'gate-io': 'Gate.io',
    'nexo-cex': 'Nexo'
}


def import_defi_llama_addresses():
    with DEFI_LLAMA_REPO.local_repo_path() as repo_dir:
        grep_results = check_output(f"grep -r 'const {{ cexExports }}' '{repo_dir}'", shell=True).decode()
        cex_json_paths = [result.split(':')[0] for result in grep_results.split("\n")]
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
                addresses_by_chain = pyjson5.loads(address_json5)
            except pyjson5.Json5IllegalCharacter:
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

        insert_addresses(wallets)
