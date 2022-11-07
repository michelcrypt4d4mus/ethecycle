import pytest

from ethecycle.blockchains import *
from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.models.token import Token
from ethecycle.models.transaction import Txn
from ethecycle.models.wallet import Wallet
from ethecycle.util.string_constants import *

EXTRACTION_TIMESTAMP_STR = '2020-02-20T02:20:20'
TEST_DATA_SOURCE = 'the_pharcyde/bypass'
TEST_TXN_HASH = '0x666_TRANSACTION_HASHING_OF_THE_BEAST_666'
TEST_TXN_LOG_LEVEL = '777'


@pytest.fixture(autouse=True, scope='session')
def ethereum_of_the_beast(prep_db, token_of_the_beast):
    """Add token to Ethereum ChainInfo in memory."""
    Token.chain_addresses()[ETHEREUM][token_of_the_beast.address] = token_of_the_beast
    Token._by_blockchain_symbol[ETHEREUM][token_of_the_beast.symbol] = token_of_the_beast
    return Ethereum


@pytest.fixture(autouse=True, scope='session')
def wallet_1() -> Wallet:
    return Wallet(
        address='0xPHAT_WALLET_ADDRESS_1',
        chain_info=Ethereum,
        name='Gabriel',
        category=CEX,
        data_source=TEST_DATA_SOURCE,
        extracted_at=EXTRACTION_TIMESTAMP_STR
    )


@pytest.fixture(autouse=True, scope='session')
def wallet_2() -> Wallet:
    return Wallet(
        address='0xPHAT_WALLET_ADDRESS_2',
        chain_info=Ethereum,
        name='Lucifer',
        category=CEX,
        data_source=TEST_DATA_SOURCE,
        extracted_at='2020-02-20T02:20:20'
    )


@pytest.fixture(autouse=True, scope='session')
def token_of_the_beast() -> Token:
    return Token(
        chain_info=Ethereum,
        address='0x666_TOKEN_ADDRESS_OF_THE_BEAST_666',
        symbol='S1X',
        name='Token Of The Beast',
        decimals=6,
        token_type=ERC20,
        data_source=TEST_DATA_SOURCE,
        extracted_at=EXTRACTION_TIMESTAMP_STR
    )


@pytest.fixture(autouse=True, scope='session')
def transaction_of_the_beast(ethereum_of_the_beast, token_of_the_beast, wallet_1, wallet_2) -> Txn:
    return Txn(
        token_address=token_of_the_beast.address,
        from_address=wallet_1.address,
        to_address=wallet_2.address,
        csv_value='6000000',
        transaction_hash=TEST_TXN_HASH,
        log_index=TEST_TXN_LOG_LEVEL,
        block_number=666666,
        chain_info=Ethereum,
        extracted_at=EXTRACTION_TIMESTAMP_STR
    )
