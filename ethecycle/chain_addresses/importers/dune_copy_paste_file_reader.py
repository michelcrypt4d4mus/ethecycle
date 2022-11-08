"""
It's easy to quickly copy/paste a bunch of stuff from dune if you get it set up right but it
emerges in a pretty shitty format.

Ideal cols: address, [direction], total_usd, txn_count, avg_usd_per_txn, labels
"""
from os import path
from typing import List

from rich.text import Text

from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.chain_addresses.address_db import insert_addresses
from ethecycle.config import Config
from ethecycle.util.filesystem_helper import GZIP_EXTENSION, get_lines
from ethecycle.util.logging import console, log
from ethecycle.util.number_helper import comma_format_str, usd_string
from ethecycle.util.string_constants import ALAMEDA, ETHEREUM, FTX, ETHEREUM
from ethecycle.util.string_helper import (is_integer, is_usd, has_as_substring,
     strip_and_set_empty_string_to_none)
from ethecycle.models.wallet import Wallet


class DuneCopyPasteReader:
    def __init__(self, dune_data_file: str, blockchain: str, default_name: str, data_source: str) -> None:
        if not path.isfile(dune_data_file) and path.isfile(dune_data_file + GZIP_EXTENSION):
            dune_data_file += GZIP_EXTENSION

        self.dune_file = dune_data_file
        self.blockchain = blockchain
        self.default_name = default_name
        self.data_source = data_source
        self.extracted_wallet_count = 0

        if blockchain != ETHEREUM:
            raise ValueError('only eth!')

    def extract_wallets(self) -> None:
        """Extract the wallets into chain address DB."""
        wallets: List[Wallet] = []
        current_wallet = None

        for line in get_lines(self.dune_file):
            # When we find an address start new current_wallet, append old current_wallet to 'wallets' after setting name
            if Ethereum.is_valid_address(line):
                # Starting condition
                if current_wallet is None:
                    current_wallet = self._new_wallet(line)
                    continue

                # Close out the old wallet
                self._name_wallet(current_wallet)
                wallets.append(current_wallet)

                # Create a new wallet to collect data for
                current_wallet = self._new_wallet(line)
            elif line == 'inbound':
                to_or_from = 'to'
            elif line == 'outbound':
                to_or_from = 'from'
            elif is_usd(line) or is_integer(line):
                self.current_numbers.append(int(line.replace('$', '').replace(',', '')))
            else:
                self.current_label = strip_and_set_empty_string_to_none(line)

            log.debug(line)

        insert_addresses(wallets)

    def _new_wallet(self, address: str) -> Wallet:
        """New wallet."""
        self.current_numbers = []
        self.current_label = None
        self.extracted_wallet_count += 1

        return Wallet(
            blockchain=self.blockchain,
            address=address,
            category=f"big_volume",
            #organization='(Adjacent)',
            data_source=self.data_source
        )

    def _name_wallet(self, wallet: Wallet) -> None:
        """Fill in the 'name' field on 'wallet' obj."""
        if len(self.current_numbers) != 3:
            raise ValueError(f"Need 3 nums: {self.current_numbers}")

        if self.current_label:
            trade_size_str = self.current_label
        else:
            trade_size_str = ''

        if not has_as_substring(trade_size_str, [FTX, ALAMEDA], ignore_case=True):
            trade_size_str += ' ' if len(trade_size_str) > 0 else ''
            trade_size_str += f"({self.default_name} #{self.extracted_wallet_count} by Volume: "
            trade_size_str += f"{usd_string(self.current_numbers[0])} ({comma_format_str(self.current_numbers[1])} xfers, avg "
            trade_size_str += f"{usd_string(self.current_numbers[2])})"

        wallet.name = trade_size_str

        if True or Config.debug:
            console.print(Text('   Extracted Wallet: ').append_text(wallet.__rich__()), highlight=False)
