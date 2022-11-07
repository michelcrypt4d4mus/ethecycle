"""
Base class for Token, Wallet, and anything else with a blockchain address
"""
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar, Dict, Iterator, List, Optional, Type, Union

from inflection import pluralize, titleize, underscore

from ethecycle.blockchains.chain_info import ChainInfo
from ethecycle.chain_addresses.address_db import table_connection, coalesce_rows
from ethecycle.models.blockchain import get_chain_info
from ethecycle.util.logging import console, log, print_dim
from ethecycle.util.string_helper import strip_and_set_empty_string_to_none
from ethecycle.util.string_constants import *

# TODO: this i a hack
COLUMNS_TO_NOT_LOAD = ['chain_info', 'data_source']


@dataclass(kw_only=True)
class Address:
    address: Optional[str] = None  # Some CMC data has no addresses...
    blockchain: Optional[str] = None
    chain_info: Optional[Type['ChainInfo']] = None
    name: Optional[str] = None
    category: Optional[str] = None
    organization: Optional[str] = None
    data_source: Optional[str] = None
    extracted_at: Optional[Union[datetime, str]] = None

    # TODO: why doesn't this work
    # https://stackoverflow.com/questions/67955425/how-to-add-the-class-instance-to-a-class-variable-in-dataclass-notation
    #has_loaded_data_from_chain_address_db: ClassVar[bool] = False

    def __post_init__(self):
        """Either blockchain arg or chain_info can be provided; the other will be filled in."""
        self.address = strip_and_set_empty_string_to_none(self.address, to_lowercase=True)
        self.blockchain = strip_and_set_empty_string_to_none(self.blockchain, to_lowercase=True)
        self.category = strip_and_set_empty_string_to_none(self.category, to_lowercase=True)
        self.name = strip_and_set_empty_string_to_none(self.name)

        # Fill in either self.chain_info or self.blockchain
        if self.chain_info is not None and self.blockchain is None:
            self.blockchain = self.chain_info.chain_string()
        elif self.chain_info is None and self.blockchain is not None:
            self.chain_info = get_chain_info(self.blockchain)

        if isinstance(self.extracted_at, datetime):
            self.extracted_at = self.extracted_at.replace(microsecond=0).isoformat()

    def table_name(self) -> str:
        """Name of the table these objs are stored to in chain addresses DB."""
        return underscore(pluralize(type(self).__name__))

    @classmethod
    def all(cls) -> Iterator['Address']:
        """Iterate over all the Address objects in the DB."""
        for _blockchain, obj_addresses in cls.chain_addresses().items():
            for _address, obj in obj_addresses.items():
                yield obj

    @classmethod
    def chain_addresses(cls) -> Dict[str, Dict[str, 'Address']]:
        """Lazy load records from the database and activate _after_load_callback()."""
        if not cls.has_loaded_data_from_chain_address_db:
            print_dim(f"Loading '{cls.__name__}' chain address data...")
            cls._by_blockchain_address = defaultdict(lambda: dict())
            column_names = [c for c in cls.__dataclass_fields__.keys() if c not in COLUMNS_TO_NOT_LOAD]

            with table_connection(pluralize(cls.__name__.lower())) as table:
                db_rows = table.select_all(SELECT=column_names) # , WHERE=table[BLOCKCHAIN] == blockchain)

            db_rows = [dict(zip(column_names, row)) for row in db_rows]
            objs = [cls(**row) for row in coalesce_rows(db_rows)]

            for obj in objs:
                if not obj.blockchain or not obj.address:
                    log.debug(f"Skipping obj w/insufficient data: {obj}...")
                    continue

                cls._by_blockchain_address[obj.blockchain][obj.address] = obj

            cls._after_load_callback()
            console.print("    Complete!", style='green dim')
            cls.has_loaded_data_from_chain_address_db = True

        return cls._by_blockchain_address

    @classmethod
    def name_at_address(cls, blockchain: str, address: str) -> Optional[str]:
        """Get the name at a given 'address' on a given 'blockchain'."""
        return cls.get_address_property(blockchain, address, 'name')

    @classmethod
    def category_at_address(cls, blockchain: str, address: str) -> Optional[str]:
        """Get category for an address if there is one in DB."""
        return cls.get_address_property(blockchain, address, 'category')

    @classmethod
    def get_address_property(cls, blockchain: str, address: str, property: str) -> Optional[Any]:
        """Get named property if there's an object at the 'address'."""
        address_obj = cls.at_address(blockchain, address)

        if address_obj is None or property not in dir(address_obj):
            return None

        return getattr(address_obj, property)

    @classmethod
    def at_address(cls, blockchain: str, address: str) -> Optional['Address']:
        """Get named property if there's an object at the 'address'."""
        return cls.chain_addresses()[blockchain.lower()].get(address.lower())

    @classmethod
    def _after_load_callback(cls):
        """Subclasses can define this callback and it will be called immediately after loading from DB."""
        pass


Address.has_loaded_data_from_chain_address_db = False
