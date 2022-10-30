"""
Abstract class to hold blockchain specific info (address lengths, token specifications, etc.).
Should be implemented for each chain with the appropriate overrides of the abstract methods.
"""
import gzip
import json
from abc import ABC, abstractmethod
from collections import namedtuple
from os import listdir, path
from typing import Dict, Optional

from ethecycle.blockchains.token import Token
from ethecycle.util.filesystem_helper import TOKEN_DATA_DIR, WALLET_LABELS_DIR
from ethecycle.util.logging import log
from ethecycle.util.string_constants import TOKEN

WalletInfo = namedtuple('WalletInfo', ['label', 'category'])

ADDRESS_PREFIX = '0x'
WALLET_FILE_EXTENSION = '.txt.gz'


class ChainInfo(ABC):
    # Should be populated with the categories that have been pulled for this blockchain
    WALLET_LABEL_CATEGORIES = []

    # Lazy load; should only be access through cls.tokens(), cls.wallet_label(), etc.
    _tokens: Dict[str, Token] = {}
    _tokens_by_address: Dict[str, Token] = {}
    _wallet_labels: Dict[str, WalletInfo] = {}

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
                    token_address=address,
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
        if wallet_address in cls.wallet_labels():
            return cls.wallet_labels()[wallet_address].label
        else:
            return None

    @classmethod
    def wallet_category(cls, wallet_address: str) -> Optional[str]:
        """Lazy loaded wallet label categories."""
        if wallet_address in cls.wallet_labels():
            return cls.wallet_labels()[wallet_address].category
        else:
            return None

    @classmethod
    def wallet_labels(cls) -> Dict[str, WalletInfo]:
        """Lazy loaded wallet label categories."""
        if len(cls._wallet_labels) == 0:
            cls._load_wallet_label_file_contents()

        return cls._wallet_labels

    @classmethod
    def _load_wallet_label_file_contents(cls) -> None:
        """Load file matching blockchain name in wallet files dir"""
        label_file = WALLET_LABELS_DIR.joinpath(cls._chain_str() + WALLET_FILE_EXTENSION)

        if not path.isfile(label_file):
            log.warning(f"{label_file} is not a file - no labels loaded for {cls._chain_str()}")
            return

        with gzip.open(label_file, 'rb') as file:
            wallet_file_lines = [line.decode().rstrip() for line in file if not line.startswith(b'#')]

        for i in range(0, len(wallet_file_lines) - 1, 3):
            address = wallet_file_lines[i]

            if not address.startswith(ADDRESS_PREFIX):
                raise ValueError(f"{address} does not start with {ADDRESS_PREFIX}!")
            elif address in cls._wallet_labels:
                log.warning(f"{address} already labeled as {cls._wallet_labels[address]}, appending {wallet_file_lines[i + 1]}...")
            else:
                cls._wallet_labels[address] = WalletInfo(wallet_file_lines[i + 1], wallet_file_lines[i + 2])

        # Add token addresses
        for symbol, token in cls.tokens().items():
            if token.token_address in cls._wallet_labels:
                log.warning(f"{token.token_address} already labeled as {cls._wallet_labels[token.token_address]}, appending {token.token_address}...")
            else:
                cls._wallet_labels[token.token_address] = WalletInfo(symbol, TOKEN)

    @classmethod
    def _chain_str(cls) -> str:
        """Returns lowercased version of class name (which should be the name of the blockchain)."""
        return cls.__name__.lower()
