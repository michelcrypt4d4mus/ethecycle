import pytest

from ethecycle.blockchains.blockchains import get_chain_info
from ethecycle.blockchains.chain_info import ChainInfo
from ethecycle.util.string_constants import USDT, USDT_ETHEREUM_ADDRESS


@pytest.fixture
def generic_chain_info():
    return get_chain_info('crypto bro incorporated')


def test_token_address(generic_chain_info):
    with pytest.raises(ValueError):
        generic_chain_info.token_address(USDT)


def test_token_decimals(generic_chain_info):
    assert generic_chain_info.token_decimals('TOKENZ') == 0


def test_token_symbol(generic_chain_info):
    assert generic_chain_info.token_symbol(USDT_ETHEREUM_ADDRESS) is None


def test_is_valid_address(generic_chain_info):
    assert generic_chain_info.is_valid_address(USDT_ETHEREUM_ADDRESS)
    assert generic_chain_info.is_valid_address(USDT_ETHEREUM_ADDRESS + 'x')
    assert generic_chain_info.is_valid_address(USDT_ETHEREUM_ADDRESS.replace('0x', '\\x'))
    assert not generic_chain_info.is_valid_address('xyz')
