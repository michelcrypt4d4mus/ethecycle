"""
Read public sheets: https://medium.com/geekculture/2-easy-ways-to-read-google-sheets-data-using-python-9e7ef366c775#e4bb
"""
import re

import numpy as np
import pandas as pd
from urllib.parse import urlencode
from typing import List, Optional

from ethecycle.chain_addresses.address_db import insert_wallets_from_data_source
from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.config import Config
from ethecycle.models.wallet import Wallet
from ethecycle.util.logging import console, log
from ethecycle.util.number_helper import pct, pct_str
from ethecycle.util.string_constants import INDIVIDUAL, SOCIAL_MEDIA_LINKS

GOOGLE_SHEETS = {
    '1QlbETkBQAgnSJth5Na2ypQL-RaE_b1tddBX1rqT5ZK8': [
        'Twitter Bounty',
        'Facebook Bounty',
    ]
}

ARGS = {
    'tqx': 'out:csv',
}

ETHEREUM_ADDRESS_REGEX = re.compile('ethereum\\s+(wallet)?\\s*address', re.IGNORECASE)
SHEETS_URL = 'https://docs.google.com/spreadsheets/d/'
MAX_ROWS = 5


def import_google_sheets() -> None:
    wallets: List[Wallet] = []

    for sheet_id, worksheets in GOOGLE_SHEETS.items():
        for worksheet in worksheets:
            url = _build_url(sheet_id, worksheet)
            df = pd.read_csv(url)
            df = df[[c for c in df if not c.startswith("Unnamed")]]
            column_names = list(df.columns.values)
            df_length = len(df)
            invalid_address_count = 0
            wallet_cols = _guess_address_column(column_names)

            if len(wallet_cols) == 0:
                raise ValueError(f"No wallet cols found in {column_names}")

            # Remove cols where possible wallet cols are both na
            df = df[df[wallet_cols].notnull().all(axis=1)]
            df_not_nulls_length = len(df)
            df_nulls_length = df_length - df_not_nulls_length

            address_col_label = wallet_cols[0]
            df['valid_address'] = df.apply(lambda r: Ethereum.is_valid_address(address_col_label), axis=1)
            valid_address_df = df[df['valid_address']]
            valid_address_count = len(valid_address_df)
            invalid_addresses_count = df_not_nulls_length - valid_address_count

            wallet_cols_df = df[wallet_cols]
            mismatches = wallet_cols_df[wallet_cols_df[address_col_label] != wallet_cols_df[wallet_cols[-1]]]
            mismatches_length = len(mismatches)
            social_media_col_label = _guess_social_media_column(column_names, df)

            for (row_number, row) in df.iterrows():
                wallets.append(_build_wallet(row, address_col_label, social_media_col_label, url))

            if Config.debug:
                print(df.head())
                console.print(f"COLUMN NAMES: {column_names}", style='bright_red')
                console.print(f"\nWallet cols: {wallet_cols}\n", style='green')
                console.print(df[wallet_cols].head())
                console.print(f"\nMISMATCHES", style='blue')
                console.print(mismatches)
                console.print(f"SOCIAL COL: {social_media_col_label}", style='magenta')

            valid_row_count = df_length - invalid_address_count - mismatches_length - df_nulls_length
            console.print(f"Total rows: {df_length}, VALID: {valid_row_count} ({invalid_addresses_count} invalid, {mismatches_length} mismatches, {df_nulls_length} nulls)")


def _build_wallet(df_row: pd.Series, address_col_label: str, social_col_label: str, url: str) -> Wallet:
    row = df_row.to_dict()
    address = row[address_col_label].strip()
    social_label = row[social_col_label]

    if isinstance(social_label, float) and np.isnan(social_label):
        label = '?'
    else:
        label = row[social_col_label].removeprefix('https://').removeprefix('www.').strip()

    wallet = Wallet(
        address=address,
        chain_info=Ethereum,
        category=INDIVIDUAL,
        data_source=url,
        label=label
    )

    if Config.debug:
        log.debug(f"SAMPLE ROW: {row}")
        console.print(wallet)

    return wallet


def _build_url(sheet_id: str, worksheet_name: str) -> str:
    args = ARGS.copy()
    args.update({'sheet': worksheet_name})
    url = f'{SHEETS_URL}{sheet_id}/gviz/tq?{urlencode(args)}'
    console.print(f"Reading '{worksheet_name}' from '{url}'...")
    return url


def _guess_address_column(columns: List[str]) -> Optional[List[str]]:
    """Guess which col has the addresses."""
    ethereum_wallet_cols = [c for c in columns if ETHEREUM_ADDRESS_REGEX.match(c)]

    if len(ethereum_wallet_cols) > 0:
        return ethereum_wallet_cols


def _guess_social_media_column(columns: List[str], df: pd.DataFrame) -> str:
    """Guess which col has the addresses."""
    social_media_cols = [
        c for c in columns
        if any(social_media_org in c.lower() for social_media_org in SOCIAL_MEDIA_LINKS)
    ]

    for col in social_media_cols:
        social_media_url = _social_media_url(col)
        row_count = len([c for c in df[col] if isinstance(c, str) and social_media_url in c])
        console.print(f"    {col}: {row_count} of {len(df)} ({pct_str(row_count, len(df))}", style='color(155)')

        if pct(row_count, len(df)) > 95.0:
            console.print(f"        CHOOSING '{col}'", style='color(143)')
            return col

    raise ValueError(f"No social media column identified!")


def _social_media_url(column: str) -> str:
    """Find which social media org and return e.g. twitter.com."""
    for social_media_org in SOCIAL_MEDIA_LINKS:
        if social_media_org in column.lower():
            return f"{social_media_org}.com"
