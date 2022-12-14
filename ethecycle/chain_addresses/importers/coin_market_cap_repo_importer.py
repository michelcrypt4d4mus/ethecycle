"""
Extract token data from https://github.com/tttienthinh/CoinMarketCap.git
"""
import json
from os import path
from typing import Any, Dict, List

from inflection import underscore
from rich.pretty import pprint
from rich.table import Table
from rich.text import Text

from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.config import Config
from ethecycle.chain_addresses.address_db import DbRows, insert_addresses
from ethecycle.chain_addresses.github_data_source import GithubDataSource
from ethecycle.models.blockchain import guess_chain_info_from_address
from ethecycle.models.token import Token
from ethecycle.util.filesystem_helper import files_in_dir
from ethecycle.util.logging import console, log, print_address_import
from ethecycle.util.string_constants import *

SOURCE_REPO = GithubDataSource('tttienthinh/CoinMarketCap')

# Strings
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
    coin_market_cap_id
    is_hidden
    is_audited
    had_an_ico
    listed_on_coinmarketcap_at
    launched_at
    cmc_watchers
    url_discord
    url_telegram
""".split()

NON_DISPLAY_KEYS = """
    description
    holders
    notice
    relatedCoins
    relatedExchanges
    slug
    statistics
    tags
    urls
    wallets
""".split()


def import_coin_market_cap_repo_addresses() -> None:
    """Go through ~11,000 .json files in the CoinMarketCap data repo and create rows in chain addresses DB."""
    print_address_import(SOURCE_REPO.repo_url)

    with SOURCE_REPO.local_repo_path() as repo_dir:
        data_dir = path.join(repo_dir, 'Download', 'detail')
        tokens = []

        for json_filename in files_in_dir(data_dir, 'json'):
            log.debug(f"Processing file {path.basename(json_filename)}...")

            with open(json_filename, 'r') as json_data:
                for chain_token in _explode_token_blockchain_rows(json.load(json_data)['data']):
                    # Skip rows where all core cols are None
                    if all(chain_token.get(col) is None for col in TABLE_COLS):
                        continue

                    tokens.append(Token.from_properties(chain_token))

        #_print_debug_table(tokens)
        insert_addresses(tokens)


def _explode_token_blockchain_rows(token_data: Dict[str, Any]) -> DbRows:
    """
    Turn a single token's CMC data .json file into 1 or more result rows depending on how many
    chains that token exists on.
    The 1 or more objects returned will all be for the same token but each for a different blockchain
    """
    if Config.debug:
        pprint(token_data)

    row = {
        k: v.strip() if v is not None else None
        for k, v in token_data.items()
        if k in ['category', 'name', SYMBOL]
    }

    row['data_source'] = SOURCE_REPO.repo_url
    row['launched_at'] = token_data.get('dateLaunched')
    row['coin_market_cap_id'] = token_data.get('id')
    row['listed_on_coin_market_cap_at'] = token_data.get('dateAdded')
    row['coin_market_cap_watchers'] = token_data.get('watchCount')

    # Boolean fields
    status = token_data.get(STATUS)
    row['is_hidden'] = status == 'hidden'
    row['is_audited'] = token_data.get('isAudited')
    row['had_an_ico'] = 'ico' in token_data

    if status is None or status == 'untracked':
        row[IS_ACTIVE] = None
    elif token_data[STATUS] == 'active':
        row[IS_ACTIVE] = True
    else:
        if status != 'inactive':
            log.debug(f"{token_data.get(SYMBOL)} status is {status}; marking inactive")

        row[IS_ACTIVE] = False

    # Discord and telegram get their own "chat" entries; everything else goes in the extra_fields hash
    if URLS in token_data and CHAT in token_data[URLS] and token_data[URLS][CHAT]:
        chat_urls = token_data[URLS][CHAT]
        row['url_telegram'] = next((u for u in chat_urls if '/t.me/' in u or TELEGRAM in u), None)
        row['url_discord'] = next((u for u in chat_urls if '/discord.' in u), None)

        token_data[URLS][CHAT] = [
            c for c in token_data[URLS][CHAT]
            if c not in [row['url_telegram'], row['url_discord']]
        ]

    for url_type, urls in token_data.get(URLS, {}).items():
        if len(urls) == 0:
            continue
        elif len(urls) == 1:
            row[f"url_{url_type}"] = urls[0]
        elif url_type == 'explorer':
            # Prefer etherscan over others (?)
            token_url = next((url for url in urls if TOKEN in url), None)

            if token_url:
                row[URL_EXPLORER] = token_url
            else:
                log.debug(f"Found multiple explorer URLs, choosing first: {urls}")
                row[URL_EXPLORER] = urls[0]
        else:
            log.debug(f"Found multiple {url_type} URLs, choosing first: {urls}")
            row[f"url_{url_type}"] = urls[0]

    # Short circuit if there's no chain (AKA 'platform') or address info
    if PLATFORMS not in token_data:
        if row.get(URL_EXPLORER) and 'etherscan' in row[URL_EXPLORER]:
            # Parse the missing address from the URL if we possible
            log.debug(f"Using address for {row[SYMBOL]} from {URL_EXPLORER}...")
            row[ADDRESS] = Ethereum.extract_address_from_scanner_url(row[URL_EXPLORER])
        else:
            # Print (almost) the whole JSON dict if there's no chain/address info
            msg = Text("No blockchain found for symbol '", 'bright_red').append(row.get(SYMBOL, ''), 'magenta')

            # delete some of the longer elements so we only see a summary of unprintable coins
            for k in NON_DISPLAY_KEYS:
                if k in token_data:
                    del token_data[k]

            log.debug(msg.append("...").plain)
            log.debug(token_data)

        if ADDRESS in row:
            row['chain_info'] = guess_chain_info_from_address(row[ADDRESS])
            log.debug(f"No 'platforms' property. Attempted to guess chain for {row}")

        return [row]

    chains = token_data['platforms']
    log.debug(f"Token exists on {len(chains)} different chains...")
    tokens_with_chain_data = []

    for chain in chains:
        blockchain = underscore(chain['contractPlatform'])
        token_with_chain = row.copy()

        token_with_chain.update({
            BLOCKCHAIN: BINANCE_SMART_CHAIN if blockchain.startswith(BINANCE) else blockchain,
            ADDRESS: chain[CONTRACT_ADDRESS]
        })

        # TODO: Lowercasing eth addresses should be unnecessary once we use the Token class.
        if token_with_chain[ADDRESS].startswith(Ethereum.ADDRESS_PREFIXES[0]):
            token_with_chain[ADDRESS] = token_with_chain[ADDRESS].lower()

        if 'contractNativeCurrencyDecimals' in chain:
            decimals = chain['contractNativeCurrencyDecimals']

            if isinstance(decimals, int) and decimals > 0:
                row['decimals'] = decimals

        tokens_with_chain_data.append(token_with_chain)

    if row.get(SYMBOL) == 'USDT':
        pprint(tokens_with_chain_data)

    return tokens_with_chain_data


def _count_by_col(rows: DbRows, column: str) -> None:
    """Basically GROUP BY, COUNT(*)."""
    console.print(f"Counting by {column}")
    chains = set([r.get(column) for r in rows])

    for chain in sorted([c for c in chains if c]) + [None]:
        count = len([r for r in rows if r.get(column) == chain])
        chain = chain or 'n/a'
        console.print(f"{chain: >40} {count: <15}")


def _print_debug_table(rows: DbRows) -> None:
    """Show table of all tokens w/some stats. Colors reversed for tokens w/out a chain address."""
    if not Config.debug:
        return

    table = Table(*TABLE_COLS)
    rows = sorted(rows, key=lambda t: [t.get(SYMBOL, 'zzzzzz'), t.get(BLOCKCHAIN, 'zzzzzz')])

    for row in rows:
        style = 'reverse' if ADDRESS not in row else ''
        table.add_row(*[str(row.get(col, '')) for col in TABLE_COLS], style=style)

    console.print(table)
    _count_by_col(rows, BLOCKCHAIN)
    console.line(2)
    _count_by_col(rows, 'category')
