"""
Read public sheets: https://medium.com/geekculture/2-easy-ways-to-read-google-sheets-data-using-python-9e7ef366c775#e4bb
"""
import re
from os import path

import numpy as np
import pandas as pd
from rich.panel import Panel
from rich.pretty import pprint
from typing import List, Optional, Type
from urllib.parse import urlencode

from ethecycle.blockchains.bitcoin import Bitcoin
from ethecycle.blockchains.chain_info import ChainInfo
from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.chain_addresses.address_db import insert_addresses
from ethecycle.config import Config
from ethecycle.models.wallet import Wallet
from ethecycle.util.filesystem_helper import RAW_DATA_DIR
from ethecycle.util.logging import console, log, print_indented
from ethecycle.util.number_helper import pct, pct_str
from ethecycle.util.string_constants import (BITCOINTALK, FACEBOOK, HTTPS, INDIVIDUAL,
     SOCIAL_MEDIA_ORGS, social_media_url)

ETHEREUM_SHEETS = {
    '1I30YwfcqO7r7hP63hKdJM1BaaqAWiFfz_biIk2fyouM': [
        'Form Responses 1'
    ],
    '1ou1tDAiQ18Y9stKtl7DiiMe6ARlLxPhtFb3pXgVEEYI': [
        'Twitter Campaign',
        'Facebook',
    ],
    '1wVkp__Rw8OaOsavxCeUOP5ViE9y0-iywnAuYsPk714E': [
        'LinkedIn Bounty',
        'Reddit Bounty',
        'Telegram Airdrop',
        'Blog and Media Bounty',
        'Signature Bounty',
        'Twitter Bounty',
        'Facebook Bounty',
    ],
    '1lRkldOzXR5s1kBvbSN8tW_ux5H6ob9YaTW4EP3CkRhU': [
        'TWITTER',
        'FACEBOOK',
        'LINKEDIN',
        2141942915,
        'YOUTUBE',
        'Translation'
    ],
    '1eSfJWCthTyeL_1n6SK8s8SFF3ULA1XG2FBAa-PsVuP0': [
        'Telegram',
        'YouTube',
        'Reddit',
        'Facebook',
        'Translations',
        'Twitter',
    ],
    '1YJq5IAIrjavjNIMQLw7SeVx2_bydwdXELHLxnJhYfSk': [
        'Form Responses 1'
    ],
    '1eZ0gF5Qq6UnEs2hWPIvgE-L9J4uONz134sxnW-T6iBE': [
        'Report Week 1',
        'Content Campaign',
        'Youtube',
        'Twitter',
        'Telegram',
        'Linkedin',
        'Voting Campaign'
    ],
    '1RWH_9vWn3hqnWPST-H5jwSljUneR5xG-yVLu3R9gSGs': [
        'Sign up Bounty',
        'Ramadan Bounty',
        'Form Responses 16',
        'Bittrex Listing Bounty',
        'Poloniex Listing Bounty',
        'Okex Listing Bounty',
        'Huobi Listing Bounty',
        'Binance Listing Campaign',
        '6th AMA',
        'Rejected',
        '3rd AMA Bounty',
        '1st AMA Bounty',
        'Telegram Invitation',
        'CMC Listing Campaign'
    ],
    '1nFL75ojBWi0dNQjX6UcKh8WdvGXYmP23lHiSZdfv8f4': [
        'Sheet1'
    ],
    '1_Ozxkj3WitAiwocvD_o-tscCwT5o_Wn9mAcbv_qcBkQ': [
        'Social Media Campaign',
        'Reddit Campaign',
        'Signature Campaign',
        191343910,
    ],
    '1KX42FnK2TAZ2caf14TiJ5LbA7rUnsHIHX-FdJPfqx5k': [
        'Form Responses 1'
    ],
    '1gFGizvgADXVHMNhiP0WlFJY2floPpIaU14OecgngDXo': [
        'Twitter Campaign',
    ],
    '1VN61OS92gyZSHlYorDMfVVf90n3jl-HKTGbhBXVthNE': [
        'Final sheet Signature',
        'Final Translation',
        'Twitter Bounty',
        'Facebook Bounty',
        'Translation Bounty',
        'Blog/Media Bounty',
        'Signature',
    ],
    '1VY4YK06p_9Mn0tPlHoXO_N3KJZbwGB18uypXSQtk3Gc': [
        'Twitter Master Sheet',
        'Facebook Master Sheet',
        'Telegram Groups',
        'Signature',
    ],
    # This one has 282K rows!
    '1SamWX8hjMLuMx7B03S4QTR6V_dCCkcXN5PBJJdLKjnw': [
        'Form Responses 1',
    ],
    '1WCVpua051XBlLfIZpKrcQMmx_JT2JujtyJIX-bU5o5w': [
        'Application Signature Campaign',
        'Application Translation',
    ],
    '1QlbETkBQAgnSJth5Na2ypQL-RaE_b1tddBX1rqT5ZK8': [
        'Twitter Bounty',
        'Facebook Bounty',
        'Blog/Media-Final Sheet',
        'Blog and Media',
        'Signature Campaign',
        'Translations',
    ],
    '1oF6vA71id2xDp8GTxY7xBMNz67ZpbwVDAzhDeIXtnzo': [
        1187103448,
        'Twitter',
        'Facebook',
        'Instagram',
        'Youtube',
        'LinkedIn',
        'Translation'
    ],
    '1JljucXr5mJU1m2rA63NgRa7pwvmRtkIjjYHPVGpolZA': [
        'Facebook',
        'Twitter',
        'YouTube',
        'Media',
        'VK',
    ],
}

BITCOIN_SHEETS = {
    '15MyV7FiYq2cqTSqTYnObrmhD29VxmzxPrckoR6XV1qA': [
        'Signature Campaign',
        'Twitter Bounty',
        'Facebook Bounty',
        'Blog/Media',
    ],
}

# Some sheets have no address column
DEFAULT_LABELS = {
    '1nFL75ojBWi0dNQjX6UcKh8WdvGXYmP23lHiSZdfv8f4': 'petscoin recipient',
    '1YJq5IAIrjavjNIMQLw7SeVx2_bydwdXELHLxnJhYfSk': 'crykart recipient',
}

SHEETS_ARGS = {'tqx': 'out:csv'}
CHARS_THAT_NEED_QUOTE = [c for c in '):;"|-_*&']
ETHEREUM_ADDRESS_REGEX = re.compile('(eth(ereum)?|erc-?20)\\s+(wallet|address)', re.IGNORECASE)
WALLET_ADDRESS_REGEX = re.compile('^wallet\\s+.*\\s*address', re.IGNORECASE)
SHEETS_URL = 'https://docs.google.com/spreadsheets/d/'
VALID_ADDRESS = 'valid_address'

# Fix the embedded timestamp so that every write of a gzipped CSV doesn't change the binary
GZIP_COMPRESSION_ARGS = {'method': 'gzip', 'mtime': 1667767780.0}
GZIPPED_CSV_DIR = str(RAW_DATA_DIR.joinpath('google_sheets'))

# Min % of col matching a URL or @something style string
SOCIAL_MEDIA_PCT_CUTOFF = 88.0

# Max # of mismatches if there are > 1 possible address cols
MAX_MISMATCHES = 10


def import_google_sheets() -> None:
    for sheet_id, worksheets in ETHEREUM_SHEETS.items():
        for worksheet_name in worksheets:
            worksheet = GoogleWorksheet(sheet_id, worksheet_name, Ethereum)
            insert_addresses(worksheet.extract_wallets())
            console.line(2)

    for sheet_id, worksheets in BITCOIN_SHEETS.items():
        for worksheet_name in worksheets:
            worksheet = GoogleWorksheet(sheet_id, worksheet_name, Bitcoin)
            insert_addresses(worksheet.extract_wallets())
            console.line(2)


class GoogleWorksheet:
    def __init__(self, sheet_id: str, worksheet_name: str, chain_info: Type[ChainInfo]) -> None:
        self.sheet_id = sheet_id
        self.worksheet_name = worksheet_name
        self.chain_info = chain_info
        self._build_url()
        self.df = pd.read_csv(self.url)
        self.df = self.df[[c for c in self.df if not c.startswith("Unnamed")]]
        self.df_length = len(self.df)
        self.column_names = list(self.df.columns.values)
        self.email_col = None
        self._write_df_to_csv()

    def extract_wallets(self) -> List[Wallet]:
        self.address_col_label = self._guess_address_column()
        print_indented(f"Wallet column: '{self.address_col_label}'")

        # Remove rows with null addresses
        self.df = self.df[self.df[self.address_col_label].notnull()]
        non_null_address_count = len(self.df)
        self.null_address_count = self.df_length - non_null_address_count

        # Determine which social media column is suitable for use as the wallet label
        self.social_media_col_label = self._guess_social_media_column()
        self.df[self.social_media_col_label].str.strip()

        # Strip whitespace from remaining rows' addresses and check filter invalid rows
        self.df[self.address_col_label].str.strip()
        is_valid_address = lambda r: self.chain_info.is_valid_address(r[self.address_col_label])
        self.df[VALID_ADDRESS] = self.df.apply(is_valid_address, axis=1)
        valid_address_df = self.df[self.df[VALID_ADDRESS] == True]
        self.invalid_address_count = non_null_address_count - len(valid_address_df)

        # Build Wallet() objects for valid rows
        wallets = [self._build_wallet(row) for (_row_number, row) in valid_address_df.iterrows()]
        self._print_extraction_stats()

        if Config.debug:
            for wallet in wallets[0:10]:
                pprint(wallet)

        return wallets

    def _build_wallet(self, df_row: pd.Series) -> Wallet:
        row = df_row.to_dict()
        address = row[self.address_col_label]
        wallet_name = row[self.social_media_col_label]

        if isinstance(wallet_name, float) and np.isnan(wallet_name):
            name = '?'
        else:
            name = row[self.social_media_col_label].removeprefix(HTTPS).removeprefix('www.')

        wallet = Wallet(
            address=address,
            chain_info=Ethereum,
            category=INDIVIDUAL,
            data_source=self.url,
            name=name
        )

        return wallet

    def _build_url(self):
        """Build google sheets URL."""
        base_url = f"{SHEETS_URL}{self.sheet_id}"

        if isinstance(self.worksheet_name, int):
            self.url = f"{base_url}/export?format=csv&gid={self.worksheet_name}"
        else:
            args = SHEETS_ARGS.copy()
            args['sheet'] = self.worksheet_name
            self.url = f'{base_url}/gviz/tq?{urlencode(args).replace("/", "%%2F")}'

        console.print(f"Reading sheet '{self.worksheet_name}' from '{self.url}'...")

    def _guess_address_column(self) -> str:
        """Guess which col has the addresses."""
        wallet_cols = [c for c in self.column_names if ETHEREUM_ADDRESS_REGEX.search(c)]

        # Do a 2nd pass to look for more generic labels
        if len(wallet_cols) == 0:
            wallet_cols = [c for c in self.column_names if WALLET_ADDRESS_REGEX.search(c)]

        if len(wallet_cols) == 0:
            raise ValueError(f"No ethereum address columns found in {self.column_names}")
        elif len(wallet_cols) == 1:
            self.mismatch_count = 0
            return wallet_cols[0]
        elif len(wallet_cols) > 2:
            raise ValueError(f"{len(wallet_cols)} wallet columns found in {self.column_names}")

        print_indented(f"Checking possible wallet cols: {wallet_cols}", style='possibility')
        wallet_cols_df = self.df[wallet_cols]

        mismatches = wallet_cols_df[
               (wallet_cols_df[wallet_cols[0]] != wallet_cols_df[wallet_cols[-1]])
            & ~(wallet_cols_df[wallet_cols[0]].isna() & wallet_cols_df[wallet_cols[0]].isna())
        ]

        def count_valid_rows(col):
            is_valid_address = lambda row: self.chain_info.is_valid_address(row[col])
            return len(self.df[self.df.apply(is_valid_address, axis=1)])

        valid_row_counts = {col: count_valid_rows(col) for col in wallet_cols}
        console.print(f"Valid Row Counts: {valid_row_counts}")

        # Hack to handle cases where one col is an actual address column and the other is not an address col.
        if 0 in valid_row_counts.values():
            self.mismatch_count = 0

            for col, valid_row_count in valid_row_counts.items():
                if valid_row_count > 0:
                    return col

        self.mismatch_count = len(mismatches)

        if self.mismatch_count <= MAX_MISMATCHES:
            return wallet_cols[0]
        else:
            console.print(Panel(f"Mismatches between possible wallet address cols:"))
            print(mismatches)
            raise ValueError(f"Too many mismatches ({self.mismatch_count} > {MAX_MISMATCHES})")

    def _guess_social_media_column(self) -> str:
        """Guess which col has addresses (or place the configured DEFAULT_LABELS value in 'facebook' col)."""
        if self.sheet_id in DEFAULT_LABELS:
            label = DEFAULT_LABELS[self.sheet_id]
            print_indented(f"Applying default label '{label}'...")
            self.df[FACEBOOK] = self.df.apply(lambda row: f"{label} {row.name}", axis=1)
            self.column_names = self.df.columns.values
            return FACEBOOK

        social_media_cols = [
            c for c in self.column_names
            if any(social_media_org in c.lower() for social_media_org in SOCIAL_MEDIA_ORGS)
        ]

        social_media_cols = sorted(
            social_media_cols,
            key=lambda c: "zz_{c}" if (BITCOINTALK in c.lower() or ' post ' in c.lower()) else c
        )

        print_indented(f"All column names: {self.column_names}", style='color(130) dim')
        print_indented(f"Checking possible social media columns: {social_media_cols}", style='possibility')

        # First check social media cols then fall back to 'email' and 'profile' or similar
        for col in social_media_cols:
            if self._is_good_label_col(col):
                return col

        for col in self.column_names:
            if col in social_media_cols:
                continue

            if self._is_good_label_col(col):
                return col

        if self.email_col:
            return self.email_col

        raise ValueError(f"No social media column identified!")

    def _is_good_label_col(self, col: str) -> bool:
        """True if we should use this column as the wallet label based on col name and values."""
        if not isinstance(col, str):
            log.debug(f"Column '{col}' is not a string, skipping...")
            return False

        col_lowercase = col.lower()
        social_media_org = next((org for org in SOCIAL_MEDIA_ORGS if org in col_lowercase), None)

        if social_media_org:
            substring = social_media_url(social_media_org)
        elif col_lowercase.startswith('profile') or col_lowercase.startswith('vk '):
            substring = HTTPS
        elif 'email' in col_lowercase:
            log.info(f"Found email col: {col}")
            self.email_col = col
            return False
        else:
            return False

        log.debug(f"    Substring to look for '{col}' profile is '@' prefix or '{substring}'...")
        row_count = len([c for c in self.df[col] if isinstance(c, str) and (substring in c or c.startswith('@'))])
        msg = f"'{col}': {row_count} of {self.df_length} ({pct_str(row_count, len(self.df))} good label)"

        if pct(row_count, len(self.df)) > SOCIAL_MEDIA_PCT_CUTOFF:
            print_indented(f"CHOOSING {msg}", style='color(143)', indent_level=2)
            return True
        else:
            print_indented(f"IGNORING {msg}", style='color(155) dim', indent_level=2)
            return False

    def _write_df_to_csv(self) -> None:
        file_basename = f"{self.sheet_id}___{self.worksheet_name}.csv.gz".replace('/', '_slash_')
        file_path = path.join(GZIPPED_CSV_DIR, file_basename)
        print_indented(f"Writing sheet to CSV: '{file_path}'", style='dim')

        if False and path.isfile(file_path):
            console.print(f"File already exists: '{file_path}', skipping...")
        else:
            self.df.to_csv(file_path, index=False, compression=GZIP_COMPRESSION_ARGS)

    def _print_extraction_stats(self) -> None:
        invalid_row_msgs = [
            f"{self.invalid_address_count} invalid",
            f"{self.mismatch_count} mismatches",
            f"{self.null_address_count} null addresses",
        ]

        invalid_msg = ', '.join(invalid_row_msgs)
        valid_row_count = self.df_length - self.invalid_address_count - self.mismatch_count - self.null_address_count
        console.print(f"Total rows: {self.df_length}, valid rows: {valid_row_count} ({invalid_msg})")
