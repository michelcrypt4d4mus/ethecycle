"""
Abstract class to hold blockchain specific info (address lengths, token specifications, etc.).
Should be implemented for each chain with the appropriate overrides of the abstract methods.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from ethecycle.blockchains.token import Token
from ethecycle.data.chain_addresses.address_db import DbRows, tokens_table, wallets_table
from ethecycle.config import Config
from ethecycle.util.logging import log
from ethecycle.util.string_constants import ADDRESS, BLOCKCHAIN, DATA_SOURCE
from ethecycle.wallet import Wallet


class ChainInfo(ABC):
    # Should be populated with the categories that have been pulled for this blockchain
    LABEL_CATEGORIES_SCRAPED_FROM_DUNE = []

    # Lazy load; should only be access through cls.tokens(), cls.wallet_label(), etc.
    _tokens: Dict[str, Token] = {}
    _tokens_by_address: Dict[str, Token] = {}
    _wallet_labels: Dict[str, Wallet] = {}

    @classmethod
    @abstractmethod
    def scanner_url(cls, address: str) -> str:
        pass

    @classmethod
    def token_address(cls, token_symbol: str) -> str:
        """Lookup a contract address by the symbol"""
        return cls.tokens()[token_symbol].address

    @classmethod
    def token_symbol(cls, token_address: str) -> Optional[str]:
        """Reverse lookup - takes an address, returns a symbol"""
        cls.tokens()  # Force load the tokens

        try:
            return cls._tokens_by_address[token_address].symbol
        except KeyError:
            return None

    @classmethod
    def token_decimals(cls, token_address: str) -> int:
        """Reverse lookup - takes an address, returns a symbol"""
        if token_address in cls.tokens():
            return cls.tokens()[token_address].decimals or 0
        else:
            return 0

    @classmethod
    def tokens(cls) -> Dict[str, Token]:
        """Lazy load token data."""
        if len(cls._tokens) == 0 and not Config.skip_load_from_db:
            cls._load_known_tokens()

        return cls._tokens

    @classmethod
    def wallet_label(cls, wallet_address: str) -> Optional[str]:
        """Lazy loaded wallet address labels."""
        if wallet_address in cls.known_wallets():
            return cls.known_wallets()[wallet_address].label
        else:
            return None

    @classmethod
    def wallet_category(cls, wallet_address: str) -> Optional[str]:
        """Lazy loaded wallet label categories."""
        if wallet_address in cls.known_wallets():
            return cls.known_wallets()[wallet_address].category
        else:
            return None

    @classmethod
    def known_wallets(cls) -> Dict[str, Wallet]:
        """Lazy loaded wallet label, categories, etc."""
        if len(cls._wallet_labels) == 0 and not Config.skip_load_from_db:
            cls._load_known_wallets()

        return cls._wallet_labels

    @classmethod
    def _load_known_wallets(cls) -> None:
        column_names = [c for c in Wallet.__dataclass_fields__.keys() if c != 'chain_info']

        with wallets_table() as table:
            rows = table.select_all(SELECT=column_names, WHERE=table[BLOCKCHAIN] == cls._chain_str())

        rows = [dict(zip(column_names, row)) for row in rows]
        cls._wallet_labels = {row['address']: Wallet(chain_info=cls, **row) for row in rows}

    @classmethod
    def _load_known_tokens(cls) -> None:
        column_names = [c for c in Token.__dataclass_fields__.keys() if c != 'chain_info']

        with tokens_table() as table:
            rows = table.select_all(SELECT=column_names, WHERE=table[BLOCKCHAIN] == cls._chain_str())

        rows = [dict(zip(column_names, row)) for row in rows]
        tokens = [Token(**row) for row in coalesce_rows(rows)]

        cls._tokens = {token.symbol: token for token in tokens}
        cls._tokens_by_address = {token.address: token for token in tokens}

    @classmethod
    def _chain_str(cls) -> str:
        """Returns lowercased version of class name (which should be the name of the blockchain)."""
        return cls.__name__.lower()


def coalesce_rows(rows: DbRows) -> DbRows:
    """Assemble the best data for each address by combining the data_sources in the DB."""
    if len(rows) == 0:
        return rows

    cols = list(rows[0].keys())
    coalesced_rows: Dict[str, Dict[str, Any]] = {}

    for row in rows:
        address = row[ADDRESS]

        if address not in coalesced_rows:
            log.debug(f"Initializing {address} with data from {row[DATA_SOURCE]}")
            coalesced_rows[address] = row
            continue

        coalesced_row = coalesced_rows[address]

        for col in cols:
            log.debug(f"Updating {address}: {col} with '{row[col]}' from {row[DATA_SOURCE]}...")
            coalesced_row[col] = coalesced_row[col] or row[col]

    return list(coalesced_rows.values())
