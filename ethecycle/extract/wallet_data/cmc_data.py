"""
Extract tag data from https://github.com/tttienthinh/CoinMarketCap.git
"""
import csv
import json
from datetime import datetime
from os import path
from types import NoneType
from typing import Any, Dict, List, Union

from rich.pretty import pprint
from rich.table import Table
from rich.text import Text

from ethecycle.blockchains.chain_info import ADDRESS_PREFIX
from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.util.filesystem_helper import (TOKEN_DATA_REPO_PARENT_DIR,
     WALLET_LABELS_DIR, files_in_dir)
from ethecycle.util.logging import console, log
from ethecycle.util.string_constants import *

CMC_DATA_DIR = path.join(TOKEN_DATA_REPO_PARENT_DIR, 'CoinMarketCap', 'Download', 'detail')
CMC_CSV_PATH = WALLET_LABELS_DIR.joinpath('coin_market_cap_data.csv')
NON_DISPLAY_KEYS = 'description holders notice relatedCoins relatedExchanges slug statistics tags urls wallets'.split()

CHAT = 'chat'
CONTRACT_ADDRESS = 'contractAddress'
IS_ACTIVE = 'is_active'
PLATFORMS = 'platforms'
STATUS = 'status'
UNTRACKED = 'untracked'
URL_EXPLORER = 'url_explorer'
URLS = 'urls'

TABLE_COLS = """
    symbol
    name
    category
    blockchain
    address
    is_active
""".split()

CSV_OUTPUT_COLUMNS = TABLE_COLS + """
    id
    is_hidden
    is_audited
    had_an_ico
    listed_on_coinmarketcap_at
    launched_at
    cmc_watchers
    url_discord
    url_telegram
""".split()


def extract_data(token_data: Dict[str, Any]) -> List[Dict[str, Union[str, int, float, NoneType]]]:
    """Turn a CMC data .json file into 1 or more result rows."""
    info = {
        k: v
        for k, v in token_data.items()
        if k in ['id', 'category', 'name', SYMBOL]
    }

    status = token_data.get(STATUS)
    info['is_hidden'] = status == 'hidden'
    info['is_audited'] = token_data.get('isAudited')
    info['listed_on_coinmarketcap_at'] = token_data.get('dateAdded')
    info['launched_at'] = token_data.get('dateLaunched')
    info['cmc_watchers'] = token_data.get('watchCount')
    info['had_an_ico'] = 'ico' in token_data

    if status is None or status == 'untracked':
        info[IS_ACTIVE] = None
    elif token_data[STATUS] == 'active':
        info[IS_ACTIVE] = True
    else:
        if status != 'inactive':
            log.debug(f"{token_data.get(SYMBOL)} status is {status}; marking inactive")

        info[IS_ACTIVE] = False

    if URLS in token_data and CHAT in token_data[URLS] and token_data[URLS][CHAT]:
        chat_urls = token_data[URLS][CHAT]
        info['url_telegram'] = next((u for u in chat_urls if '/t.me/' in u or 'telegram' in u), None)
        info['url_discord'] = next((u for u in chat_urls if '/discord.' in u), None)

        token_data[URLS][CHAT] = [
            c for c in token_data[URLS][CHAT]
            if c not in [info['url_telegram'], info['url_discord']]
        ]

    for url_type, urls in token_data.get(URLS, {}).items():
        if len(urls) == 0:
            continue
        elif len(urls) == 1:
            info[f"url_{url_type}"] = urls[0]
        elif url_type == 'explorer':
            token_url = next((url for url in urls if TOKEN in url), None)
            token_url = token_url or next((url for url in urls if TOKEN in url), None)

            if token_url:
                info[URL_EXPLORER] = token_url
            else:
                console.print(f"Found multiple explorer URLs, choosing first: {urls}", style='red dim')
                info[URL_EXPLORER] = urls[0]
        else:
            console.print(f"Found multiple {url_type} URLs, choosing first: {urls}", style='bytes')
            info[f"url_{url_type}"] = urls[0]

    # Short circuit if there's no chain (AKA 'platform') or address info
    if PLATFORMS not in token_data:
        if info.get(URL_EXPLORER) and 'etherscan' in info[URL_EXPLORER]:
            # Parse the missing address from the URL if we possible
            log.debug(f"Using address for {info[SYMBOL]} from {URL_EXPLORER}...")
            info[ADDRESS] = Ethereum.extract_address_from_scanner_url(info[URL_EXPLORER])
        else:
            # Print (almost) the whole JSON dict if there's no chain/address info
            msg = Text("No platforms for '", 'bright_red').append(info.get(SYMBOL, ''), 'magenta')

            # delete some of the longer elements so we only see a summary of unprintable coins
            for k in NON_DISPLAY_KEYS:
                if k in token_data:
                    del token_data[k]

            log.info(msg.append("'!").plain)
            log.debug(token_data)

        return [info]

    chains = token_data['platforms']
    log.debug(f"Token exists on {len(chains)} different chains...")
    tokens_with_chain_data = []

    for chain in chains:
        token_with_chain = info.copy()

        token_with_chain.update({
            BLOCKCHAIN: chain['contractPlatform'].lower(),
            ADDRESS: chain[CONTRACT_ADDRESS]
        })

        if token_with_chain[ADDRESS].startswith(ADDRESS_PREFIX):
            token_with_chain[ADDRESS] = token_with_chain[ADDRESS].lower()

        tokens_with_chain_data.append(token_with_chain)

    return tokens_with_chain_data


def extract_cmc_data_from_repo() -> List[Dict[str, Any]]:
    """Go through ~11,000 .json files in the CoinMarketCap data repo."""
    table_rows = []

    for json_filename in files_in_dir(CMC_DATA_DIR, 'json'):
        log.debug(f"Processing file {path.basename(json_filename)}...")

        with open(json_filename, 'r') as json_data:
            token_info = json.load(json_data)['data']
            key_list_str = ', '.join(sorted(token_info.keys()))
            log.debug(f"keys: {key_list_str}")
            table_rows.extend(extract_data(token_info))
            log.debug(table_rows[-1])

    return sorted(table_rows, key=lambda r: [r.get(SYMBOL, 'zzzzzz'), r.get(BLOCKCHAIN, 'zzzzzz')])


def extract_coin_market_cap_data_to_csv() -> None:
    """Print rich.Table and some summary stats then write a CSV."""
    table = Table(*TABLE_COLS)
    rows = extract_cmc_data_from_repo()
    other_cols = set()

    for row in rows:
        style = 'reverse' if ADDRESS not in row else ''
        table.add_row(*[str(row.get(col, '')) for col in TABLE_COLS], style=style)

        for key in [k for k in row.keys() if k not in CSV_OUTPUT_COLUMNS]:
            other_cols.add(key)

    # Print table and some summary stats
    console.print(table)
    _count_by_col(rows, BLOCKCHAIN)
    console.line(2)
    _count_by_col(rows, 'category')

    # Write CSV data
    console.print(f"Writing CSV data to '{CMC_CSV_PATH}...")
    columns = CSV_OUTPUT_COLUMNS + sorted(list(other_cols)) + ['extracted_at']

    with open(CMC_CSV_PATH, 'w') as csvfile:
        extracted_at = datetime.utcnow().replace(microsecond=0).isoformat()
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(columns)

        for row in rows:
            if all(row.get(col) is None for col in TABLE_COLS):
                continue

            row['extracted_at'] = extracted_at
            csv_writer.writerow([str(row.get(c, '')) for c in columns])

    console.print("Finished.")


def _count_by_col(rows: List[Dict[str, Any]], column: str) -> None:
    """Basically GROUP BY, COUNT(*)."""
    console.print(f"Counting by {column}")
    chains = set([r.get(column) for r in rows])

    for chain in sorted([c for c in chains if c]) + [None]:
        count = len([r for r in rows if r.get(column) == chain])
        chain = chain or 'n/a'
        console.print(f"{chain: >40} {count: <15}")
