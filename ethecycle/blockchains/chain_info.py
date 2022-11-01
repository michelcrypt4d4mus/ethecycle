"""
Abstract class to hold blockchain specific info (address lengths, token specifications, etc.).
Should be implemented for each chain with the appropriate overrides of the abstract methods.
"""
import json
from abc import ABC, abstractmethod
from os import listdir, path
from typing import Dict, Optional

from ethecycle.blockchains.token import Token
from ethecycle.data.wallet_labels.wallet_db import wallets_table
from ethecycle.util.filesystem_helper import TOKEN_DATA_DIR
from ethecycle.util.logging import log
from ethecycle.util.string_constants import BLOCKCHAIN
from ethecycle.wallet import Wallet


class ChainInfo(ABC):
    # Should be populated with the categories that have been pulled for this blockchain
    WALLET_LABEL_CATEGORIES = []

    # Lazy load; should only be access through cls.tokens(), cls.wallet_label(), etc.
    _tokens: Dict[str, Token] = {}
    _tokens_by_address: Dict[str, Token] = {}
    _wallet_labels: Dict[str, Wallet] = {}

    @classmethod
    @abstractmethod
    def scanner_url(cls, address: str) -> str:
        pass

    @classmethod
    @abstractmethod
    def token_info_dir(cls) -> str:
        pass

    @classmethod
    def add_hardcoded_tokens(cls) -> None:
        """
        Overload this method for anything not in the ethereum-lists GitHub repo.
        It should add key/value pairs to both cls_tokens and cls_tokens_by_address.
        """
        pass

    @classmethod
    def token_address(cls, token_symbol: str) -> str:
        """Lookup a contract address by the symbol"""
        return cls.tokens()[token_symbol].token_address

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
        if len(cls._tokens) > 0:
            return cls._tokens

        cls.add_hardcoded_tokens()
        token_data_dir = path.join(TOKEN_DATA_DIR, cls.token_info_dir())

        for token_info_json_file in listdir(token_data_dir):
            with open(path.join(token_data_dir, token_info_json_file), 'r') as json_file:
                token_info = json.load(json_file)

            try:
                symbol = token_info['symbol']
                address = token_info['address'].lower()

                token = Token(
                    blockchain=cls._chain_str(),
                    token_type=token_info.get('type'),  # Not always provided
                    address=address,
                    symbol=symbol,
                    name=token_info['name'],
                    decimals=token_info['decimals']
                )

                cls._tokens[symbol] = token
                cls._tokens_by_address[address] = token
            except KeyError as e:
                log.warning(f"Error parsing '{token_info_json_file}': {e}")

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
        if len(cls._wallet_labels) == 0:
            cls._load_known_wallets()

        return cls._wallet_labels

    @classmethod
    def _load_known_wallets(cls) -> None:
        with wallets_table() as table:
            column_names = [c for c in Wallet.__dataclass_fields__.keys() if c != 'chain_info']
            rows = table.select_all(SELECT=column_names, WHERE=table[BLOCKCHAIN] == cls._chain_str())
            rows = [dict(zip(column_names, row)) for row in rows]
            cls._wallet_labels = {row['address']: Wallet(chain_info=cls, **row) for row in rows}

    @classmethod
    def _chain_str(cls) -> str:
        """Returns lowercased version of class name (which should be the name of the blockchain)."""
        return cls.__name__.lower()
